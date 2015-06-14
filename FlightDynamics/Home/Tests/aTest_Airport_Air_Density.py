# -*- coding: UTF-8 -*-

'''
Created on 25 déc. 2014

@author: PASTOR Robert

test how air density changes according to airport field elevation

'''
import unittest
import time

from Home.Environment.Atmosphere import Atmosphere
from Home.Environment.AirportDatabaseFile import AirportsDatabase

#============================================
class Test_Class(unittest.TestCase):

    def test_class_one(self):

        print '==================== Main start ==================== '+ time.strftime("%c")

        t0 = time.clock()
        print "time start= {0}".format( t0)
        atmosphere = Atmosphere()
        
        t1 = time.clock()
        print "simulation time= {0} - simulation duration= {1:3.10f} seconds".format(t1 , (t1-t0))
    
        print '==================== load airports ==================== '+ time.strftime("%c")
        airportsDB = AirportsDatabase()
        assert airportsDB.read()
        print '==================== air density at airports field elevation ==================== '+ time.strftime("%c")
    
        for airport in airportsDB.getAirports():
            print '=======================' + airport.getName() + '===================='
            print 'field elevation= ' + str(airport.getFieldElevationAboveSeaLevelMeters()) + ' meters'
            altitudeMeters = airport.getFieldElevationAboveSeaLevelMeters()
            print 'air density= ' + str(atmosphere.getAirDensityKilogramsPerCubicMeters(altitudeMeters)) + ' kg / meters ^^ 3'

    def test_class_two(self):

        print '==================== Main start ==================== '+ time.strftime("%c")

        t0 = time.clock()
        print "time start= {0}".format( t0)
        atmosphere = Atmosphere()
        
        t1 = time.clock()
        print "simulation time= {0} - simulation duration= {1:3.10f} seconds".format(t1 , (t1-t0))
    
        print '==================== load airports ==================== '+ time.strftime("%c")
        airportsDB = AirportsDatabase()
        assert airportsDB.read()

        altitudeMeters = 10.0
        print 'air density= ' + str(atmosphere.getAirDensityKilogramsPerCubicMeters(altitudeMeters)) + ' kg / meters ^^ 3'
        
        print '==================== air density at given altitudes ==================== '+ time.strftime("%c")
    
        for altitudeMeters in ['10.0', '1000.0', '2000.0', '3000.0', '4000.0']:
            strMsg = 'altitude= ' + str(altitudeMeters) + ' meters ... air density= '
            strMsg += str(atmosphere.getAirDensityKilogramsPerCubicMeters(float(altitudeMeters))) 
            strMsg += ' kg / cubic meters'
            print strMsg
        
if __name__ == '__main__':
    unittest.main()
        
