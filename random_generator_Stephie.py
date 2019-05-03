'''
BC: 			battery capacity in kWh
BEVPowMax: 		maximum power the battery is able to be charged with in kW
CapCon: 		capacity Constraint of the GCP in kW
CapConWert: 	capacity Constraint of the GCP in kW
CapConAkt:		capacity Constraint of the GCP in kW
CSPowMax:		maximum charging power of the CS in kW
CSPowMin: 		minimum charging power of the CS in kW
SoC:			State of Charge, battery charging level in percent
eta: 			battery's efficiency
BEVcap_rest:	remaining battery capacity in kWh
CapConMin:		minimum capacity Constraint of the GCP in kW
CapConMax:		maximum capacity Constraint of the GCP in kW
'''


# Generates random instance of Multi-CPO-Chargingpark

import classes
import names
from random import *
from terminaltables import AsciiTable




def create_rand_instance():

    # Generate the CPO

    all_cpos = {}

    cpo_names = ["Auto"]

    cpo_sample_num = 1
    cpo_sample_name = sample(cpo_names, cpo_sample_num)

    for c in range(cpo_sample_num):
        all_cpos.update({cpo_sample_name[c]:
                        classes.Cpo(c, cpo_sample_name[c])})

    ''' 
	Generate 2 customers for the CPO
	Creating random customers with specific SoC, BEVPowMax and BC values	
	'''

    for c in all_cpos:
        x = 2  							# number of charging ports operated by CPO
        y = randrange(2, x+1)  			# number of CPO's customers
        for i in range(y):
            n = uniform(0,100)			# random number between 0 and 100
            m = uniform(0,100)			# random number between 0 and 100
            SoC = 0 					# battery charging level in percent
            BEVPowMax = 0 				# maximum power the battery is able to be charged with in kW
            BC = 0 						# battery capacity in kWh
            if (n <= 27):
                BEVPowMax = 50
            elif (n <= 37):
                BEVPowMax = 63
            elif (n <= 46):
                BEVPowMax = 50
            elif (n <= 55):
                BEVPowMax = 120
            elif (n <= 60):
                BEVPowMax = 135
            elif (n <= 72):
                BEVPowMax = 40
            elif (n <= 84):
                BEVPowMax = 50
            elif (n <= 89):
                BEVPowMax = 40
            elif (n <= 92):
                BEVPowMax = 120
            else:
                BEVPowMax = 50
				
            if (n <= 9):
                BC = 21.6
            elif (n <= 27):
                BC = 33.2
            elif (n <= 37):
                BC = 27
            elif (n <= 46):
                BC = 30
            elif (n <= 49):
                BC = 75
            elif (n <= 52):
                BC = 100
            elif (n <= 58):
                BC = 85
            elif (n <= 60):
                BC = 60
            elif (n <= 66):
                BC = 24.2
            elif (n <= 72):
                BC = 35.8
            elif (n <= 81):
                BC = 24
            elif (n <= 84):
                BC = 40
            elif (n <= 89):
                BC = 18.7
            elif (n <= 91):
                BC = 90
            elif (n <= 92):
                BC = 100
            elif (n <= 95):
                BC = 14.5
            else:
                BC = 16
				
            if (m <= 1.8):
                SoC = 0.2
            elif(m <= 9.2):
                SoC = 0.3
            elif(m <= 28):
                SoC = 0.4
            elif(m <= 50.6):
                SoC = 0.5
            elif(m <= 68.8):
                SoC = 0.6
            elif(m <= 80.5):
                SoC = 0.7
            elif(m <= 87):
                SoC = 0.8
            elif(m <= 95.7):
                SoC = 0.9
            else:
                SoC = 0.95
			
            all_cpos[c].get_customers().update({c + str(i): classes.Customer(
                                                           c + str(i),  # id
                                                           names.get_first_name(),  # name
                                                           c,  # cust_cpo
                                                           BEVPowMax,  # BEVPowMax
                                                           10.0,  # CSPowMin
                                                           SoC,  # blvl
                                                           BC,  # bcap
                                                           50,  # CSPowMax
                                                           0.85  # eta
                                                           )})
														   
            all_cpos[c].set_attr("CapConMax", all_cpos[c].get_attr("CapConMax") + all_cpos[c].get_customers()[c + str(i)].get_attr("CSPowMax"))
            all_cpos[c].set_attr("CapConMin", all_cpos[c].get_attr("CapConMin") + all_cpos[c].get_customers()[c + str(i)].get_attr("CSPowMin"))
            all_cpos[c].set_attr("CapConMax", all_cpos[c].get_attr("CapConMax") + 120 * (x - len(all_cpos[c].get_customers())))

    # Determine random transformer power between sum over CapConMin and CapConMax for all cpos

    CapConWert = 90

    for c in all_cpos:
        all_cpos[c].set_attr("CapConAkt",
                             CapConWert * all_cpos[c].get_attr("CapConMax")
                             / sum(all_cpos[c].get_attr("CapConMax") for c in all_cpos))

    # print random instance

    print("\r")
    print("CapCon: ", CapConWert)

    table_data_cpos = [["CPO", "CapConMax", "CapConMin", "CapConAkt"]]

    for c in all_cpos:
        table_data_cpos.append([c,
                                format(all_cpos[c].get_attr("CapConMax"), ".2f"),
                                format(all_cpos[c].get_attr("CapConMin"), ".2f"),
                                format(all_cpos[c].get_attr("CapConAkt"), ".2f"),
                                ])

    table_cpos = AsciiTable(table_data_cpos)

    # create Chargingpark Object with generated data
    return classes.Chargingpark(all_cpos, CapConWert)
