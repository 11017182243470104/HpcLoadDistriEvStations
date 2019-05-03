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
CapConMin:		minimum capacity Constraint of the GCP in kW
CapConMax:		maximum capacity Constraint of the GCP in kW
'''
#Alignments depend on formatting standards

import pandas as pd
from random import *
# Class definition


class Chargingpark:
    __CapCon = 0.0
    __cpos = {}

    def __init__(self, cpos, CapCon):
        self.__cpos = cpos
        self.__CapCon = CapCon

    def get_cpos(self):
        return self.__cpos

    def get_attr(self, name):
        if name == "CapCon":
            return self.__CapCon
        else:
            print("Error getting attribute!")
            quit()

    def set_attr(self, name, value):
        if name == "CapCon":
            self.__CapCon = value
        else:
            print("Error setting attribute!")
            quit()


class Cpo:
    __id = 0
    __name = ""
    __customers = {}
    __CapConMax = 0.0  
    __CapConMin = 0.0
    __CapConAkt = 0.0

    def __init__(self, id, name):
        self.__id = id
        self.__name = name
        self.__customers = {}
        self.__CapConMax = 0.0
        self.__CapConMin = 0.0
        self.__CapConAkt = 0.0

    def get_customers(self):
        return self.__customers

    def get_attr(self, name):
        if name == "id":
            return self.__id
        elif name == "name":
            return self.__name
        elif name == "CapConMax":
            return self.__CapConMax
        elif name == "CapConMin":
            return self.__CapConMin
        elif name == "CapConAkt":
            return self.__CapConAkt
        else:
            print("Error getting attribute!")
            quit()

    def set_attr(self, name, value):
        if name == "id":
            self.__id = value
        elif name == "name":
            self.__name = value
        elif name == "CapConMax":
            self.__CapConMax = value
        elif name == "CapConMin":
            self.__CapConMin = value
        elif name == "CapConAkt":
            self.__CapConAkt = value
        else:
            print("Error setting attribute!")
            quit()


class Customer:

    __id = 0
    __name = ""
    __cust_cpo = ""
    __BEVPowMax = 0.0  
    __CSPowMin = 0.0  
    __SoC = 0.0  
    __BC = 0.0  
    __CSPowMax = 0.0
    __eta = 0.0
    __BEVcap_rest = 0.0
    __time_exp = 0.0

    def __init__(self, id, name, cust_cpo, BEVPowMax, CSPowMin, SoC, BC, CSPowMax, eta):
        data = pd.read_excel ('Survey.xlsx', sheet_name='Survey', dtype={'State of charge - Start': float, 'State of charge - End': float, 'Charging duration': float, 'Experience': str, 'Age': float, 'Gender': str } )

        self.__id = id
        self.__name = name
        self.__cust_cpo = cust_cpo
        self.__BEVPowMax = BEVPowMax
        self.__CSPowMin = CSPowMin
        j = randint (1, 50)
        self.__SoC = data['State of charge - Start'][j]
        #self.__SoC = SoC
        self.__BC = BC
        self.__CSPowMax = CSPowMax
        self.__eta = eta
        self.__time_exp = (BC * (100 - SoC)/100) / (min(BEVPowMax, CSPowMax)) 
        self.__BEVcap_rest = BC * (100 - SoC)/100

    def get_attr(self, name):
        if name == "id":
            return self.__id
        elif name == "name":
            return self.__name
        elif name == "cust_cpo":
            return self.__cust_cpo
        elif name == "BEVPowMax":
            return self.__BEVPowMax
        elif name == "CSPowMin":
            return self.__CSPowMin
        elif name == "SoC":
            return self.__SoC
        elif name == "BC":
            return self.__BC
        elif name == "CSPowMax":
            return self.__CSPowMax
        elif name == "eta":
            return self.__eta
        elif name == "time_exp":
            return self.__time_exp
        elif name == "BEVcap_rest":
            return self.__BEVcap_rest
        else:
            print("Error getting attribute!")
            quit()

    def set_attr(self, name, value):
        if name == "id":
            self.__id = value
        elif name == "name":
            self.__name = value
        elif name == "cust_cpo":
            self.__cust_cpo = value
        elif name == "BEVPowMax":
            self.__BEVPowMax = value
        elif name == "CSPowMin":
            self.__CSPowMin = value
        elif name == "SoC":
            self.__SoC = value
        elif name == "BC":
            self.__BC = value
        elif name == "CSPowMax":
            self.__CSPowMax = value
        elif name == "eta":
            self.__eta = value
        elif name == "time_exp":
            self.__time_exp = value
        elif name == "BEVcap_rest":
            self.__BEVcap_rest = value
        else:
            print("Error setting attribute!")
            quit()
