'''
Created on 6 janvier 2015

@author: PASTOR Robert
'''

import time
import sys
import unittest

from Home.Guidance.FlightPathFile import FlightPath


Meter2Feet = 3.2808 # one meter equals 3.28 feet
Meter2NauticalMiles = 0.000539956803 # One Meter = 0.0005 nautical miles
NauticalMiles2Meter = 1852 

class Test_Route(unittest.TestCase):


    def test_route(self):
#============================================
        
        #sys.stdout = open('log.txt','w') #redirect all prints to this log file
        
        print "=========== Flight Plan start  =========== " + time.strftime("%c")
        
        strRoute = 'ADEP/LEMD-ZMR-BARKO-ADES/LEVX'
        strRoute = 'ADEP/LFBM/27-AGN-TOU-GAI-AMOLO-DEGOL-FJR-MARRI-ADES/LFML/31R'
    
        flightPath = FlightPath(route = strRoute, 
                                aircraftICAOcode = 'A320',
                                RequestedFlightLevel = 270, 
                                cruiseMach = 0.78, 
                                takeOffMassKilograms=62000.0)
        '''
        RFL:    FL 310 => 31000 feet
        Cruise Speed    Mach 0.78                                    
        Take Off Weight    62000 kgs    
        '''
        print "=========== Flight Plan compute  =========== " + time.strftime("%c")
        
        t0 = time.clock()
        print 'time zero= ' + str(t0)
        lengthNauticalMiles = flightPath.computeLengthNauticalMiles()
        print 'flight path length= {0:.2f} nautics '.format(lengthNauticalMiles)
        flightPath.computeFlight(deltaTimeSeconds = 1.0)
        print 'simulation duration= ' + str(time.clock()-t0) + ' seconds'
        
        print "=========== Flight Plan create output files  =========== " + time.strftime("%c")
        flightPath.createFlightOutputFiles()
        print "=========== Flight Plan end  =========== " + time.strftime("%c")


if __name__ == '__main__':
    unittest.main()