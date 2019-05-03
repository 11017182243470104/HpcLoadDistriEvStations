'''
BC: 			battery capacity in kWh
BEVPowMax: 	    maximum power the battery is able to be charged with in kW
CapCon: 		capacity Constraint of the GCP in kW
CapConWert: 	capacity Constraint of the GCP in kW
CapConAkt:		capacity Constraint of the GCP in kW
CSPowMax:		maximum charging power of the CS in kW
CSPowMin: 		minimum charging power of the CS in kW
SoC:			State of Charge, battery charging level in percent
eta: 			battery's efficiency
BEVcap_rest:	remaining battery capacity in kWh
CapCon_smpl:	capacity Constraint of the GCP divided by the number of cars currently charging in kW
CapConMin:		minimum capacity Constraint of the GCP in kW
CapConMax:		maximum capacity Constraint of the GCP in kW
'''


# Model with linear function and quadratic deviation

from gurobipy import *
from terminaltables import AsciiTable
import pandas as pd
from random import *


def solve_instance(Chargingpark):

    cpos, CapConMax, CapConMin, CapConAkt = multidict({Chargingpark.get_cpos()[c].get_attr("name"):
                                                   [Chargingpark.get_cpos()[c].get_attr("CapConMax"),
                                                   Chargingpark.get_cpos()[c].get_attr("CapConMin"),
                                                   Chargingpark.get_cpos()[c].get_attr("CapConAkt")]
                                                   for c in Chargingpark.get_cpos()})

    all_customers = {}
    for c in Chargingpark.get_cpos():
        for i in Chargingpark.get_cpos()[c].get_customers():
            all_customers[Chargingpark.get_cpos()[c].get_customers()[i].get_attr("id")] =\
                Chargingpark.get_cpos()[c].get_customers()[i]

    customers, cust_cpo, BEVPowMax, CSPowMin, CSPowMax, BEVcap_rest, time_exp, eta, SoC, BC = multidict({
                                                    all_customers[i].get_attr("id"): [
                                                        all_customers[i].get_attr("cust_cpo"),
                                                        all_customers[i].get_attr("BEVPowMax"),
                                                        all_customers[i].get_attr("CSPowMin"),
                                                        all_customers[i].get_attr("CSPowMax"),
                                                        all_customers[i].get_attr("BEVcap_rest"),
                                                        all_customers[i].get_attr("time_exp"),
                                                        all_customers[i].get_attr("eta"),
                                                        all_customers[i].get_attr("SoC"), 
                                                        all_customers[i].get_attr("BC")]  
                                                    for i in all_customers})

    CapCon = Chargingpark.get_attr("CapCon")

    # Optimizationmodel

    m = Model("Multi-CPO-Setting")
    m.ModelSense = +1  # objective will be minimized

    # Variables

    bpwr_opt = m.addVars(customers, name="customer power optimal")    
    cpwr_opt = m.addVars(cpos, name="cpo power optimal")              

    # Objective: piecewise linearized objective function for each customer (100 pieces)

    bpwr = {i: [CSPowMin[i] + (min(BEVPowMax[i], CSPowMax[i]) - CSPowMin[i]) * k / 99 for k in range(100)]          
            for i in customers}

    time_var = {i: [pow(BEVcap_rest[i]/(bpwr[i][k] * eta[i]) - time_exp[i], 1) for k in range(100)]         
                for i in customers}
    
    for i in customers:
        m.setPWLObj(bpwr_opt[i], bpwr[i], time_var[i])

    # Constraints

    for c in cpos:
        m.addConstr(
            sum(bpwr_opt[i] for i in customers if cust_cpo[i] == c) <= cpwr_opt[c], 
            name="CPO capacity restriction"
        )

    m.addConstr(
        sum(bpwr_opt[i] for i in customers) <= CapCon,     
        name="Customer capacity restriction"
    )

    m.addConstrs(
        bpwr_opt[i] >= CSPowMin[i] for i in customers
    )

    m.addConstrs(
        bpwr_opt[i] <= BEVPowMax[i] for i in customers    
    )

    m.addConstrs(
        bpwr_opt[i] <= CSPowMax[i] for i in customers     
    )

    for c in cpos:
        if sum(min(BEVPowMax[i], CSPowMax[i]) for i in customers if cust_cpo[i] == c) > CapConAkt[c]:
            m.addConstr(
                cpwr_opt[c] >= max(CapConMin[c], CapConAkt[c]),
                name="Distribute among CPOs"
            )
        else:
            m.addConstr(
                cpwr_opt[c] == sum(min(BEVPowMax[i], CSPowMax[i]) for i in customers if cust_cpo[i] == c),
                name="No wasted power"
            )

    # Optimize

    m.optimize()

    objective_opt = m.getAttr("ObjVal")
    solution_cpo = m.getAttr("x", cpwr_opt)
    solution_cust = m.getAttr("x", bpwr_opt)

    for i in customers:
        print(str(i), " ", solution_cust[i])
    

    # Calculate simple solution without optimization
    
    CapCon_smpl = {c: CapConAkt[c] / len(Chargingpark.get_cpos()[c].get_customers()) for c in cpos}

    if ((BEVPowMax["Auto0"] < BEVPowMax["Auto1"]) and (BEVPowMax["Auto0"] < (CapCon/2)) and (BEVPowMax["Auto1"] > (CapCon/2))) :
        objective_smpl = (pow(BEVcap_rest["Auto0"] / (min(CapCon_smpl[cust_cpo["Auto0"]], BEVPowMax["Auto0"], CSPowMax["Auto0"]) * eta["Auto0"]) - time_exp["Auto0"], 2)) + (pow(BEVcap_rest["Auto1"] / (min(BEVPowMax["Auto1"], CSPowMax["Auto1"], (CapCon - min(CapCon_smpl[cust_cpo["Auto0"]], BEVPowMax["Auto0"], CSPowMax["Auto0"]))) * eta["Auto1"]) - time_exp["Auto1"], 2))
        difmax_smpl = max(((BEVcap_rest["Auto0"] / (min(CapCon_smpl[cust_cpo["Auto0"]], BEVPowMax["Auto0"], CSPowMax["Auto0"]) * eta["Auto0"]) - time_exp["Auto0"])), ((BEVcap_rest["Auto1"] / (min(BEVPowMax["Auto1"], CSPowMax["Auto1"], (CapCon - min(CapCon_smpl[cust_cpo["Auto0"]], BEVPowMax["Auto0"], CSPowMax["Auto0"]))) * eta["Auto1"]) - time_exp["Auto1"])))
        difmin_smpl = min(((BEVcap_rest["Auto0"] / (min(CapCon_smpl[cust_cpo["Auto0"]], BEVPowMax["Auto0"], CSPowMax["Auto0"]) * eta["Auto0"]) - time_exp["Auto0"])), ((BEVcap_rest["Auto1"] / (min(BEVPowMax["Auto1"], CSPowMax["Auto1"], (CapCon - min(CapCon_smpl[cust_cpo["Auto0"]], BEVPowMax["Auto0"], CSPowMax["Auto0"]))) * eta["Auto1"]) - time_exp["Auto1"])))
        average_smpl = ((((BEVcap_rest["Auto0"] / (min(CapCon_smpl[cust_cpo["Auto0"]], BEVPowMax["Auto0"], CSPowMax["Auto0"]) * eta["Auto0"]) - time_exp["Auto0"])) + ((BEVcap_rest["Auto1"] / (min(BEVPowMax["Auto1"], CSPowMax["Auto1"], (CapCon - min(CapCon_smpl[cust_cpo["Auto0"]], BEVPowMax["Auto0"], CSPowMax["Auto0"]))) * eta["Auto1"]) - time_exp["Auto1"]))) / 2)
        print ("A")
	
    elif ((BEVPowMax["Auto0"] > BEVPowMax["Auto1"]) and (BEVPowMax["Auto1"] < (CapCon/2)) and (BEVPowMax["Auto0"] > (CapCon/2))) :
        objective_smpl = (pow(BEVcap_rest["Auto1"] / (min(CapCon_smpl[cust_cpo["Auto1"]], BEVPowMax["Auto1"], CSPowMax["Auto1"]) * eta["Auto1"]) - time_exp["Auto1"], 2)) + (pow(BEVcap_rest["Auto0"] / (min(BEVPowMax["Auto0"], CSPowMax["Auto0"], (CapCon - min(CapCon_smpl[cust_cpo["Auto1"]], BEVPowMax["Auto1"], CSPowMax["Auto1"]))) * eta["Auto0"]) - time_exp["Auto0"], 2))
        difmax_smpl = max(((BEVcap_rest["Auto1"] / (min(CapCon_smpl[cust_cpo["Auto1"]], BEVPowMax["Auto1"], CSPowMax["Auto1"]) * eta["Auto1"]) - time_exp["Auto1"])), ((BEVcap_rest["Auto0"] / (min(BEVPowMax["Auto0"], CSPowMax["Auto0"], (CapCon - min(CapCon_smpl[cust_cpo["Auto1"]], BEVPowMax["Auto1"], CSPowMax["Auto1"]))) * eta["Auto0"]) - time_exp["Auto0"])))
        difmin_smpl = min(((BEVcap_rest["Auto1"] / (min(CapCon_smpl[cust_cpo["Auto1"]], BEVPowMax["Auto1"], CSPowMax["Auto1"]) * eta["Auto1"]) - time_exp["Auto1"])), ((BEVcap_rest["Auto0"] / (min(BEVPowMax["Auto0"], CSPowMax["Auto0"], (CapCon - min(CapCon_smpl[cust_cpo["Auto1"]], BEVPowMax["Auto1"], CSPowMax["Auto1"]))) * eta["Auto0"]) - time_exp["Auto0"])))
        average_smpl = ((((BEVcap_rest["Auto1"] / (min(CapCon_smpl[cust_cpo["Auto1"]], BEVPowMax["Auto1"], CSPowMax["Auto1"]) * eta["Auto1"]) - time_exp["Auto1"])) + ((BEVcap_rest["Auto0"] / (min(BEVPowMax["Auto0"], CSPowMax["Auto0"], (CapCon - min(CapCon_smpl[cust_cpo["Auto1"]], BEVPowMax["Auto1"], CSPowMax["Auto1"]))) * eta["Auto0"]) - time_exp["Auto0"]))) / 2)
        print ("B")
	
    else :
        objective_smpl = sum(pow(BEVcap_rest[i] / (min(CapCon_smpl[cust_cpo[i]], BEVPowMax[i], CSPowMax[i]) * eta[i]) - time_exp[i], 2) for i in customers)
        difmax_smpl = max([BEVcap_rest[i] / (min(CapCon_smpl[cust_cpo[i]], BEVPowMax[i], CSPowMax[i]) * eta[i]) - time_exp[i] for i in customers])
        difmin_smpl = min([BEVcap_rest[i] / (min(CapCon_smpl[cust_cpo[i]], BEVPowMax[i], CSPowMax[i]) * eta[i]) - time_exp[i] for i in customers])
        average_smpl = ((sum(BEVcap_rest[i] / (min(CapCon_smpl[cust_cpo[i]], BEVPowMax[i], CSPowMax[i]) * eta[i]) - time_exp[i] for i in customers)) / 2)
        print ("C")


    simpleCharRate = {}
    simpleCharRate["Auto0"] = (min(CapCon_smpl[cust_cpo["Auto0"]], BEVPowMax["Auto0"], CSPowMax["Auto0"]) * eta["Auto0"])
    simpleCharRate["Auto1"] = (min(CapCon_smpl[cust_cpo["Auto0"]], BEVPowMax["Auto1"], CSPowMax["Auto1"]) * eta["Auto1"])

    difmax_opt = max([BEVcap_rest[i] / (eta[i] * solution_cust[i]) - time_exp[i] for i in customers])
    difmin_opt = min([BEVcap_rest[i] / (eta[i] * solution_cust[i]) - time_exp[i] for i in customers])
    average_opt = ((sum(BEVcap_rest[i] / (eta[i] * solution_cust[i]) - time_exp[i] for i in customers)) /2)

    data = pd.read_excel ('Umfrage-Original-bearbeitet0415.xlsx', sheet_name='Tabelle1', dtype={'AkkustandStart': float, 'AkkustandEnde': float, 'Dauer': float, 'Implizite Laderate': float, 'Groesser nominelle Ladegeschwindigkeit':bool, 'Groesser als durchschnittliche Ladegeschwindigkeit':bool, 'DauerNormalisiert': float, 'Wissen': float, 'Erfahrung': str, 'Alter': float, 'Geschlecht': str, 'Bildungsabschluss': str } )
    time_exp_real = {}

    percentageCharge = 100 - SoC["Auto0"]  # defines how many percent of the battery will be charged /remain to full charge
    j = randint (1, 187)
    speed_factor = (data['Implizite Laderate'][j]/120) * (min(BEVPowMax["Auto0"], CSPowMax["Auto0"]))
    time_exp_real["Auto0"] = (BEVcap_rest["Auto0"]) / speed_factor
    print ("TIME EPX Real v1", time_exp_real["Auto0"])
    print("imp laderate v1", data['Implizite Laderate'][j])
    print("State of Charge", SoC["Auto0"])

    percentageCharge = 100 - SoC["Auto1"] # defines how many percent of the battery will be charged /remain to full charge
    j = randint (1, 187)
    speed_factor = (data['Implizite Laderate'][j]/120) * (min(BEVPowMax["Auto1"], CSPowMax["Auto1"]))
    time_exp_real["Auto1"] = (BEVcap_rest["Auto1"]) / speed_factor
    print ("TIME EPX Real v2", time_exp_real["Auto1"])
    print("imp laderate v2", data['Implizite Laderate'][j])

    
    difmax_opt_with_RealExpectation = max([BEVcap_rest[i] / (eta[i] * solution_cust[i]) - time_exp_real[i] for i in customers])
    difmin_opt_with_RealExpectation = min([BEVcap_rest[i] / (eta[i] * solution_cust[i]) - time_exp_real[i] for i in customers])
    average_opt_with_RealExpectation = ((sum(BEVcap_rest[i] / (eta[i] * solution_cust[i]) - time_exp_real[i] for i in customers)) /2)

    difmax_smpl_with_RealExpectation = max([BEVcap_rest[i] / (simpleCharRate[i]) - time_exp_real[i] for i in customers])
    difmin_smpl_with_RealExpectation = min([BEVcap_rest[i] / (simpleCharRate[i]) - time_exp_real[i] for i in customers])
    average_smpl_with_RealExpectation = ((sum(BEVcap_rest[i] / (simpleCharRate[i]) - time_exp_real[i] for i in customers)) /2)

    # Output solution customers

    print("\r")

    table_data_cust = [["Act.Ch.Rate", "BEVPowMax", "CSPowMax", "pwr_smpl", "Act. Charging time", "Exp. time"]]

    for i in customers:
        table_data_cust.append([#i,
                                format(solution_cust[i], ".2f"),
                                format(BEVPowMax[i], ".2f"),
                                format(CSPowMax[i], ".2f"),
                                format(min(CapCon_smpl[cust_cpo[i]], min(BEVPowMax[i], CSPowMax[i]) * eta[i]), ".2f"),
                                format(BEVcap_rest[i]/(solution_cust[i] * eta[i]), ".2f"),
                                format(time_exp[i], ".2f"),
                                #format(pow(BEVcap_rest[i]/(eta[i] * solution_cust[i]) - time_exp[i], 2), ".2f")
                                ])

    table_cust = AsciiTable(table_data_cust)

    for i in range(4):
        table_cust.justify_columns[i+1] = "center"

    print(table_cust.table)

    # Output solution CPOs

    print("\r")

    table_data_cpos = [["CPO", "Power", "Max. power customers", "Max. power CPO", "Th. power CPO"]]

    for c in cpos:
        table_data_cpos.append([c,
                                format(solution_cpo[c], ".2f"),
                                sum(min(BEVPowMax[i], CSPowMax[i]) for i in customers if cust_cpo[i] == c),
                                CapConMax[c],
                                format(CapConAkt[c], ".2f")
                                ])

    table_cpos = AsciiTable(table_data_cpos)

    for i in range(4):
        table_cpos.justify_columns[i+1] = "center"

    print(table_cpos.table)
    print("\r")

    # Return objectives and min/max difference

    return [
        [objective_opt, average_opt, difmax_opt, difmin_opt],
        [objective_smpl, average_smpl, difmax_smpl, difmin_smpl],
        [0.0, average_opt_with_RealExpectation, difmax_opt_with_RealExpectation, difmin_opt_with_RealExpectation],
        [0.0, average_smpl_with_RealExpectation, difmax_smpl_with_RealExpectation, difmin_smpl_with_RealExpectation]
    ]
