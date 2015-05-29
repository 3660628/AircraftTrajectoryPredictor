# -*- coding: UTF-8 -*-
'''
Created on 12 octobre 2014

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

from Home.BadaAircraftPerformance.BadaAircraftConfigurationFile import AircraftConfiguration
from Home.Guidance.WayPointFile import WayPoint


class BadaAircraft(AircraftConfiguration):
    className = ""

    ICAOcode = ''
    badaPerformanceFile = ''
    
    WakeTurbulenceCategory = ''
    nbEngines = 0
    engine = None
    
    def __init__(self, 
                 ICAOcode,
                 aircraftFullName,
                 badaPerformanceFilePath, 
                 atmosphere, 
                 earth):
        
        self.className = self.__class__.__name__
        ICAOcode = str(ICAOcode).upper()
        self.ICAOcode = ICAOcode
        self.aircraftFullName = aircraftFullName
                        
        ''' initialize the mother class aircraftConfiguration => is the Chef-d-orchestre '''
        AircraftConfiguration.__init__(self, badaPerformanceFilePath, ICAOcode , atmosphere, earth)

   
    def getWakeTurbulenceCategory(self):
        return self.WakeTurbulenceCategory
        
    def __str__(self):
        strAC = self.className + ' ICAO code= {0}'.format(self.ICAOcode)
        strAC += ' wake Turbulence category= {0}'.format(self.WakeTurbulenceCategory)
        strAC += ' ac full name= {0}'.format(self.aircraftFullName)
        return str(strAC)
    
    def dump(self):
        print self.className + ' ICAO code= {0}'.format(self.ICAOcode)
        print self.className + ' aircraft full name= {0}'.format(self.aircraftFullName)


    def getLandingLengthMeters(self):
        return self.groundMovement.getLandingLengthMeters()
    

    def fly(self, elapsedTimeSeconds, 
            deltaTimeSeconds, 
            distanceStillToFlyMeters,
            currentPosition,
            distanceToLastFixMeters):
        '''
        main aircraft entry point : computes for a delta time 
        1) the ground distance flown (hence needs a ground speed)
        Needs = ground speed => obtained from TAS and Wind speed
        2) the delta increase - decrease in altitude
        
        '''
        assert (isinstance(currentPosition, WayPoint))
        aircraftMassKilograms = self.aircraftMass.getCurrentMassKilograms()
        endOfSimulation, deltaDistanceMeters , altitudeMeters = super(BadaAircraft, self).fly(elapsedTimeSeconds,
                                                                               deltaTimeSeconds, 
                                                                               aircraftMassKilograms,
                                                                               distanceStillToFlyMeters,
                                                                               currentPosition,
                                                                               distanceToLastFixMeters)

        return endOfSimulation, deltaDistanceMeters, altitudeMeters
    
    
    def initStateVector(self, 
                        elapsedTimeSeconds,
                        trueAirSpeedMetersSecond,
                        airportFieldElevationAboveSeaLevelMeters):
         
        aircraftMassKilograms = self.aircraftMass.getCurrentMassKilograms()
        self.StateVector.initStateVector(elapsedTimeSeconds, 
                                            trueAirSpeedMetersSecond, 
                                            airportFieldElevationAboveSeaLevelMeters,
                                            aircraftMassKilograms)
        

        