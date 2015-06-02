# -*- coding: UTF-8 -*-

'''
Created on Jul 1, 2014

@author: Robert PASTOR

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
import math
import time
import csv
import unittest
import os

class Earth():
    
    radiusMeters = 6378135.0 # earth’s radius in meters
    omega = 2 * math.pi/ (23 * 3600 + 56 * 60 + 4.0905) # earth’s rot. speed (rad/s)
    mu = 3.986004e14 # mu = GMe %earth’s grav. const (m^3/s^2)
    
    def __init__(self, 
                 radius=6378135.0, # in meters
                 omega=(2 * math.pi/ (23 * 3600 + 56 * 60 + 4.0905)) ,# earth’s rot. speed (rad/s)
                 mu = 3.986004e14 ): # mu = GMe %earth’s grav. const (m^3/s^2)

        self.className = self.__class__.__name__

        self.radiusMeters = radius
        self.omega = omega
        self.mu = mu
        
    def getRadiusMeters(self):
        return self.radiusMeters
        
    
    def  gravity(self, radius, latitudeRadians):
        # returns gc gnorth
        # (c) 2006 Ashish Tewari
        
        phi = math.pi / 2.0 - latitudeRadians
        
        Re = self.radiusMeters
        
        J2 = 1.08263e-3
        J3 = 2.532153e-7
        J4 = 1.6109876e-7
        gc = self.mu * (1-1.5 * J2 * ( 3 * (math.cos(phi) ** 2) -1)*((Re/radius)** 2) - 2 * J3* math.cos(phi)*(5*math.cos(phi)**2-3)*(Re/radius) ** 3-(5/8) * J4 * (35 * (math.cos(phi) ** 4) - 30 * (math.cos(phi)**2) +3 )*((Re/radius)**4)) / (radius**2)
        gnorth = -3 * self.mu * math.sin(phi)* math.cos(phi) * (Re/radius) * (Re/radius) * (J2 + 0.5 * J3 * (5 * math.cos(phi) ** 2 - 1) * (Re/radius) / math.cos(phi) +(5/6) * J4 * (7 * math.cos(phi)**2-1) * (Re/radius) ** 2)/ (radius**2)
        return gc, gnorth


    def dump(self):
        print "earth radius: ", self.radiusMeters, " meters"
        print "earth's rotation speed: ", self.omega, " radians/sec"
        print "earth's gravity constant: ", self.mu, " m^3/s^2"

    def __str__(self):
        strMsg = self.className + " earth radius= {0} meters".format( self.radiusMeters )
        strMsg += " - earth's rotation speed=  {0} radians/sec".format( self.omega,)
        strMsg += " - earth's gravity constant= {0} m^3/s^2".format( self.mu )
        return strMsg

#============================================
class Test_Main(unittest.TestCase):

    def test_main_one(self):
    
        print "=========== gravity =========== " + time.strftime("%c")
        fileName = "gravity.csv"
        if ('Environment' in os.getcwd()):
            fileName = os.getcwd() + os.path.sep + fileName
        else:
            fileName = os.getcwd() + os.path.sep + 'Home' + os.path.sep + 'ResultsFiles' + os.path.sep + fileName
            
        CsvFile = open(fileName, "wb")
        dtr = math.pi/180.
        earthRadiusMeters = 6378.135e3
        try:
            writer = csv.writer(CsvFile)
            writer.writerow(("latitude in degrees", "latitude radians", "radius in meters", "gc " , "gnorth"))
            earth = Earth()
            
            for latitudeDegrees in range(0, 180):
                print 'latitude in degrees: ', latitudeDegrees, " degrees"
                
                gc , gnorth = earth.gravity(earthRadiusMeters, latitudeDegrees*dtr)
                print gc , gnorth
                writer.writerow((latitudeDegrees, latitudeDegrees*dtr, earthRadiusMeters, gc , gnorth))
            
        finally:
            CsvFile.close()
            
    def test_main_two(self):
        
        print "=========== earth =========== " + time.strftime("%c")

        earth = Earth()
        earth.dump()
        
        print "=========== earth =========== " + time.strftime("%c")
        print str(earth)
        
if __name__ == '__main__':
    unittest.main()