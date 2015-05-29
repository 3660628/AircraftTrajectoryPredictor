'''
Created on 6 mars 2015

@author: PASTOR Robert

@author: PASTOR Robert

        Written By:
                Robert PASTOR 
                @Email: < robert [--DOT--] pastor0691 (--AT--) orange [--DOT--] fr >

        @http://trajectoire-predict.monsite-orange.fr/ 
        @copyright: Copyright 2015 Robert PASTOR 

        This program is free software; you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation; either version 3 of the License, or
        (at your option) any later version.
 
        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.
 
        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <http://www.gnu.org/licenses/>.
        
'''

from Home.BadaAircraftPerformance.BadaAircraftPerformanceFile import AircraftPerformance

MeterSecond2Knots = 1.9438444924406


class FuelConsumption(object):
    
    className = ''
    fuelConsumptionCoeff = {}
    
    def __init__(self, aircraftPerformance):
        self.className = self.__class__.__name__
        assert (isinstance(aircraftPerformance, AircraftPerformance))
        self.fuelConsumptionCoeff = aircraftPerformance.getFuelConsumptionCoeff()

    def getFuelConsumptionCoeff(self):
        return self.fuelConsumptionCoeff

    def __str__(self):
        strMsg = self.className
        for index in range(0,6):
            strMsg += ': fuel consumption coeff= ' + str(index) + ' coeff= ' + str(self.fuelConsumptionCoeff[index])
        return strMsg
    
    

class Engine(FuelConsumption):
    '''
    Engine Thrust Block
    
    The OPF engine thrust block consists of 3 data lines with 4 comment lines for a total of 7 lines.
    An example of the engine thrust block is given below.
    
    CC====== Engine Thrust ===============================================/
    CC Max climb thrust coefficients (SIM) /
    1 -> CD .30400E+06 .44800E+05 .11600E-09 .67500E+01 .42600E-02 /
    
    CC Desc(low) Desc(high) Desc level Desc(app) Desc(ld) /
    2 -> CD .73000E-02 .20600E-01 .80000E+04 .12000E+00 .36000E+00 /
    
    CC Desc CAS Desc Mach unused unused unused /
    3 -> CD .28000E+03 .79000E+00 .00000E+00 .00000E+00 .00000E+00 /
    
    The first data line specifies the following BADA parameters used to calculate the maximum climb
    thrust, that is:
    CTc,1 CTc,2 CTc,3 CTc,4 CTc,5
    These parameters are specified in the following fixed format (Fortran notation):
    'CD', 2X, 5 (3X, E10.5)
    '''
    className = ''
        
    # line number starting 0 in BADA.OPF file
    EngineLine = 15
    maxClimbThrustCoeff = {}
    descentThrustCoeff = {}
    engineType = None
    
    class EngineType():
        '''
        The engine type can be one of three values: Jet, Turboprop, or, Piston.
        '''
        engineTypes = ['Jet', 'Turboprop', 'Piston']
        engineType = ''
        
        def __init__(self, strEngineType):
            self.engineType = 'Jet'
            if strEngineType in self.engineTypes:
                self.engineType = strEngineType
        
        def __str__(self):
            return self.engineType
        
        def isJet(self):
            return self.engineType=='Jet'
        
        def isTurboProp(self):
            return self.engineType=='Turboprop'
        
        def isPiston(self):
            return self.engineType=='Piston'
    
    
    def __init__(self, aircraftPerformance):
        
        FuelConsumption.__init__(self, aircraftPerformance)

        assert isinstance(aircraftPerformance, AircraftPerformance)
        self.className = self.__class__.__name__
        self.engineType = Engine.EngineType(aircraftPerformance.getStrEngineType())
        
        for index in range(0,5):
            self.maxClimbThrustCoeff[index] = aircraftPerformance.getMaxClimbThrustCoeff(index)
        for index in range(0,5):
            self.descentThrustCoeff[index] = aircraftPerformance.getDescentThrustCoeff(index)
            
    def isJet(self):
        return self.engineType.isJet()
    
    def isTurboProp(self):
        return self.engineType.isTurboProp()
    
    def isPiston(self):
        return self.engineType.isPiston()

    def getMaxClimbThrustCoeff(self, index):
        return self.maxClimbThrustCoeff[index]

    def getDescentThrustCoeff(self, index):
        return self.descentThrustCoeff[index]
    
    
    def computeNominalFuelFlowKilograms(self, 
                                        trueAirSpeedMetersSecond, 
                                        thrustNewtons, 
                                        deltaTimeSeconds):
        '''
        For the jet and turbo- prop engines, the thrust specific fuel consumption,
        (kg/(min*kN)), is specified as a function of true airspeed, VTAS (knots):
        
        thrust specific fuel flow [kg/(min*kN)]
        
        engineTypes = ['Jet', 'Turboprop', 'Piston']
        
        fuel flow in Kilograms per minutes
        '''
        fuelConsumptionCoeff = self.getFuelConsumptionCoeff()
        if self.isJet():
            ''' true airspeed should be expressed in Knots here '''
            thrustSpecificFuelConsumption = fuelConsumptionCoeff[0] * ( 1 + ( (trueAirSpeedMetersSecond * MeterSecond2Knots) / fuelConsumptionCoeff[1]))
            ''' formulae uses Kilo Newtons hence divide by 1000.0 '''
            fuelFlowKilogramsPerMinute = thrustSpecificFuelConsumption * ( thrustNewtons / 1000.0)
            fuelFlowKilograms = fuelFlowKilogramsPerMinute * (deltaTimeSeconds / 60.0)
            #print self.className + ': delta time = {0} second(s) - fuel flow kilograms= {1} kilograms'.format(deltaTimeSeconds, fuelFlowKilograms)
        elif self.isTurboProp():
            raise ValueError(self.className + ': computeNominalFuelFlow: not yet implemented')
        else:
            raise ValueError(self.className + ': computeNominalFuelFlow: not yet implemented')
        return fuelFlowKilograms
    

