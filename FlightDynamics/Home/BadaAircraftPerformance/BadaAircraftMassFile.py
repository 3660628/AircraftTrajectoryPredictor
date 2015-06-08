'''
@since: Created on 6 mars 2015

@author: PASTOR Robert

        Written By:
                Robert PASTOR 
                @Email: < robert [--DOT--] pastor0691 (--AT--) orange [--DOT--] fr >

        http://trajectoire-predict.monsite-orange.fr/ 
        Copyright 2015 Robert PASTOR 

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
import unittest
from Home.BadaAircraftPerformance.BadaAircraftPerformanceFile import AircraftPerformance
from Home.BadaAircraftPerformance.BadaAircraftDatabaseFile import BadaAircraftDatabase

Kilogram2Pounds = 2.20462262 # 1 kilogram = 2.204 lbs


class AircraftMass(object):
    '''
    Four mass values are specified for each aircraft in tons:
    mmin - minimum mass
    mmax - maximum mass
    mref - reference mass
    mpyld - maximum payload mass
    '''
    className = ""
    minimumMassKilograms = 0.0
    maximumMassKilograms = 0.0
    referenceMassKilograms = 0.0
    maximumPayLoadMassKilograms = 0.0
    currentMassKilograms = 0.0
    initialMassKilograms = 0.0
    
    def __init__(self, aircraftPerformance):
        
        assert isinstance(aircraftPerformance, AircraftPerformance)
        self.className = self.__class__.__name__
        self.referenceMassKilograms = aircraftPerformance.getReferenceMassTons()*1000.
        self.minimumMassKilograms = aircraftPerformance.getMinimumMassTons()*1000.
        self.maximumMassKilograms = aircraftPerformance.getMaximumMassTons()*1000.
        self.maximumPayLoadMassKilograms = aircraftPerformance.getMaximumPayLoadMassKilograms()*1000.
        ''' aircraft mass is computed adding the pay-load to the minimum and adding the fuel mass '''
        self.currentMassKilograms = self.referenceMassKilograms
        self.initialMassKilograms = self.referenceMassKilograms
        self.dump()
        
    def setAircraftMassKilograms(self, massKilograms):
        assert (self.minimumMassKilograms <= massKilograms) and (massKilograms <= self.maximumMassKilograms)
        print self.className + ' =========================================================='
        print self.className + ': set Aircraft Mass= {0:.2f} kilograms - Mass= {1:.2f} pounds'.format(massKilograms, massKilograms*Kilogram2Pounds)
        self.initialMassKilograms = massKilograms
        self.currentMassKilograms = massKilograms
        print self.className + ' =========================================================='

    def getCurrentMassKilograms(self):
        return self.currentMassKilograms
        
    def getInitialMassKilograms(self):
        return self.initialMassKilograms
        
    def getMinimumMassKilograms(self):
        return self.minimumMassKilograms
    
    def getMaximumMassKilograms(self):
        return self.maximumMassKilograms
    
    def getReferenceMassKilograms(self):
        return self.referenceMassKilograms
    
    def computeInitialFuelMassKilograms(self, flightPathRangeMeters):
        print self.className + ': compute Fuel mass in KiloGrams for flight path range= ' + str(flightPathRangeMeters) + ' meters'
        '''
        SFC Specific Fuel Consumption 
        SFC is defined as the mass flow rate of fuel per unit of thrust (lbm/s/lbf or kg/s/N).
        
        range = Cruise Speed / acceleration of gravity ) * ( 1 / SFC ) * log Nep ( Initial Weight / Final Weight) 
        range = ( speed of sound * Mach ) * ( 1 / ct ) * (CL / CD ) * log nep ( initial Weight / final Weight )
        '''
        return self.aircraftMass.referenceMassKilograms - self.aircraftMass.minimumMassKilograms     
    
    def computeAircraftMass(self, rangeMeters):
        '''
        mass of the aircraft is obtained using the Breguet range equation
        The maximal total range is the distance an aircraft can fly between take-off and landing.
        '''
        assert isinstance(rangeMeters, float)
        print self.className + ': compute aircraft mass - from the range expressed in Meters '
        return self.referenceMassKilogramms
    
    
    def updateAircraftMassKilograms(self, fuelFlowKilograms):
        
        self.currentMassKilograms = self.currentMassKilograms - fuelFlowKilograms
        
        if self.currentMassKilograms > self.maximumMassKilograms:
            raise ValueError (self.className + ': current mass greater to Maximum Mass')
        
        if self.currentMassKilograms < self.minimumMassKilograms:
            raise ValueError (self.className + ': no more fuel !!!')
        
        return self.currentMassKilograms

    
    def dump(self):
        print self.className + ': aircraft reference mass= {0:.2f} kilograms'.format(self.referenceMassKilograms)
        print self.className + ': aircraft minimum mass= {0:.2f} kilograms'.format(self.minimumMassKilograms)
        print self.className + ': aircraft maximum mass= {0:.2f} kilograms'.format(self.maximumMassKilograms)
        print self.className + ': aircraft maximum pay load mass= {0:.2f} kilograms'.format(self.maximumPayLoadMassKilograms)
        
        
class Test_Class(unittest.TestCase):

    def test_Class_One(self):
            
        print '================ test one ===================='
        acBd = BadaAircraftDatabase()
        assert acBd.read()
        
        
        aircraftICAOcode = 'A320'
        if ( acBd.aircraftExists(aircraftICAOcode) and
             acBd.aircraftPerformanceFileExists(aircraftICAOcode)):
            
            print acBd.getAircraftFullName(aircraftICAOcode)
            
            aircraftPerformance = AircraftPerformance(acBd.getAircraftPerformanceFile(aircraftICAOcode))
            aircraftMass = AircraftMass(aircraftPerformance)
            
if __name__ == '__main__':
    unittest.main() 