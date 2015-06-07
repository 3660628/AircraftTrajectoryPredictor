'''
Created on 6 mars 2015

@author: PASTOR Robert

        Written By:
                Robert PASTOR 
                Email: < robert [--DOT--] pastor0691 (--AT--) orange [--DOT--] fr >

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
        
 """
this class is responsible for managing the AeroDynamics data provided for each aircraft by BADA
'''

import unittest

from Home.BadaAircraftPerformance.BadaAircraftPerformanceFile import AircraftPerformance
from Home.BadaAircraftPerformance.BadaAircraftDatabaseFile import BadaAircraftDatabase

from Home.Environment.Atmosphere import Atmosphere
from Home.Environment.Earth import Earth


class AeroDynamics(object):
    
    className = ''
    AeroDynamicsLine = 3
    WingAreaSurfaceSquareMeters = 0.0
    VstallKcas = {}
    DragCoeff = {}
    LandingGearDragCoeff = 0.0
    atmosphere = None
    earth = None
    
    
    def __init__(self, 
                 aircraftPerformance, 
                 atmosphere, 
                 earth):
        
        ''' need atmosphere to compute stall speed from air density at airport altitude '''
        self.className = self.__class__.__name__
        assert (isinstance(aircraftPerformance, AircraftPerformance))
        self.WingAreaSurfaceSquareMeters = aircraftPerformance.getWingAreaSurfaceSquareMeters()
        
        assert (isinstance(atmosphere, Atmosphere) and not(atmosphere is None))
        self.atmosphere = atmosphere
        
        assert (isinstance(earth, Earth) and not(earth is None))
        self.earth = earth
        '''
        Specifically, five different configurations are specified with a stall speed 
        [(Vstall)i ] and configuration threshold altitude [Hmax, i ] given for each
        
        CC n Phase  Name    Vstall(KCAS)    CD0          CD2        unused    /
        CD 1 CR   Clean     .13900E+03   .25954E-01   .25882E-01   .00000E+00 /
        CD 2 IC   1         .11300E+03   .28410E-01   .37646E-01   .00000E+00 /
        CD 3 TO   1+F       .10400E+03   .44520E-01   .32811E-01   .00000E+00 /
        CD 4 AP   2         .10000E+03   .46986E-01   .35779E-01   .00000E+00 /
        CD 5 LD   FULL      .94000E+02   .97256E-01   .36689E-01   .00000E+00 /
        '''
        self.VstallKcas = aircraftPerformance.getVstallKcasKnots()
        self.DragCoeff = aircraftPerformance.getDragCoeff()
        self.LandingGearDragCoeff = aircraftPerformance.getLandingGearDragCoeff()
        
        print self.className + ': Wing Area Surface= {0} Square-Meters'.format(self.WingAreaSurfaceSquareMeters)
        print self.className + ': stall speed= {0} knots'.format(self.VstallKcas)
        
    def getVstallKcas(self, phase):
        ''' calibrated air speed in Knots '''
        assert (phase in ['CR', 'IC', 'TO', 'AP', 'LD'])
        return self.VstallKcas[phase]
        
        
    def getDragCoeff(self, phase):
        assert (phase in ['CR', 'IC', 'TO', 'AP', 'LD'])
        CD0 = self.DragCoeff['CD0'][phase]
        CD2 = self.DragCoeff['CD2'][phase]
        return CD0, CD2

    def getWingAreaSurfaceSquareMeters(self):
        return self.WingAreaSurfaceSquareMeters
        
    def __str__(self):
        strMsg = self.className + ': WingAreaSurface Square-Meters= ' + str(self.WingAreaSurfaceSquareMeters)
        strMsg += ': stall speeds in knots= ' + str (self.VstallKcas)
        return strMsg
        
    def dump(self):
        print self.className + ': Wing Area Surface= {0} Square-Meters'.format(self.WingAreaSurfaceSquareMeters)
        print self.className + ': stall speed= {0} knots'.format(self.VstallKcas)
        

class Test_Class(unittest.TestCase):

    def test_Class_One(self):
            
        print '================ test one ===================='
        acBd = BadaAircraftDatabase()
        assert acBd.read()
        
        atmosphere = Atmosphere()
        earth = Earth()
        
        aircraftICAOcode = 'A320'
        if ( acBd.aircraftExists(aircraftICAOcode) and
             acBd.aircraftPerformanceFileExists(aircraftICAOcode)):
            
            print acBd.getAircraftFullName(aircraftICAOcode)
            
            aircraftPerformance = AircraftPerformance(acBd.getAircraftPerformanceFile(aircraftICAOcode))
            aeroDynamics = AeroDynamics(aircraftPerformance, atmosphere, earth)
            
            print aeroDynamics
            for phase in ['CR', 'IC', 'TO', 'AP', 'LD']:
                print 'phase= {0} - Vstall CAS= {1} knots'.format(phase, aeroDynamics.getVstallKcas(phase))
                
            for phase in ['CR', 'IC', 'TO', 'AP', 'LD']:
                print 'phase= {0} - Drag Coeff= {1}'.format(phase, aeroDynamics.getDragCoeff(phase))

            print 'Wing Area Surface={0} Square-meters'.format(aeroDynamics.getWingAreaSurfaceSquareMeters())
        
if __name__ == '__main__':
    unittest.main()