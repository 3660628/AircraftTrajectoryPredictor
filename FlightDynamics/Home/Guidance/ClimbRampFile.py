# -*- coding: UTF-8 -*-

'''
Created on 9 December 2014

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

@note: manages both
 initial climb ramp at 8.0 degrees (parameter)
 orientation = true heading of the provided run-way
 length = 5 nautical miles
 start point has field elevation above mean sea level

'''
import time
import unittest

from Home.BadaAircraftPerformance.BadaAircraftDatabaseFile import BadaAircraftDatabase
from Home.BadaAircraftPerformance.BadaAircraftFile import BadaAircraft

from Home.Environment.AirportDatabaseFile import AirportsDatabase
from Home.Environment.Atmosphere import Atmosphere
from Home.Environment.Earth import Earth
from Home.Environment.RunWaysDatabaseFile import RunWay, RunWayDataBase

from Home.Guidance.WayPointFile import WayPoint, Airport
from Home.Guidance.GroundRunLegFile import GroundRunLeg

from Home.Guidance.GraphFile import Graph


OneNauticalMilesInMeters = 1852. # meters
Meter2Feet = 3.2808399 # one meter approx == 3 feet (3 feet and 3 inches)

class ClimbRamp(Graph):
    
    className = ''
    initialWayPoint = None
    runway = None
    aircraft = None
    takeOffPoint = None
    departureAirport = None
    
    def __init__(self,
                 initialWayPoint = None,
                 runway = None, 
                 aircraft = None, 
                 departureAirport = None):
        
        ''' base class init '''
        Graph.__init__(self)

        self.className = self.__class__.__name__
        
        assert isinstance(initialWayPoint, WayPoint)
        self.initialWayPoint = initialWayPoint
        
        assert isinstance(runway , RunWay) and (not(runway is None))
        self.runway = runway

        assert not(departureAirport is None)
        assert isinstance(departureAirport, Airport)
        self.departureAirport = departureAirport
        
        assert isinstance(aircraft, BadaAircraft)
        self.aircraft = aircraft
        ''' everything is OKay to start '''

        
    def buildClimbRamp(self,
                       deltaTimeSeconds,
                       elapsedTimeSeconds, 
                       distanceStillToFlyMeters, 
                       distanceToLastFixMeters,
                       climbRampLengthNautics = 5.0 ):
        
        ''' from the run-way , we get the orientation or run-way true heading in degrees '''
        runWayOrientationDegrees = self.runway.getTrueHeadingDegrees()     
        print self.className + ': run-way orientation degrees= ' + str(runWayOrientationDegrees) + ' degrees'
                
        ''' climb ramp length in meters '''
        ClimbSlopeLengthMeters = climbRampLengthNautics * OneNauticalMilesInMeters

        '''============== initial index for the climb ramp graph ============='''
        index = 0
        
        '''========================'''
        ''' initial conditions '''
        '''========================'''
        cumulatedLegDistanceMeters = 0.0
        elapsedTimeSeconds = elapsedTimeSeconds
        altitudeMeanSeaLevelMeters = self.departureAirport.getFieldElevationAboveSeaLevelMeters()

        '''========================'''        
        ''' loop on the climb ramp '''
        '''========================'''
        endOfSimulation = False
        while ( (endOfSimulation == False) and (cumulatedLegDistanceMeters <= ClimbSlopeLengthMeters)):
            
            ''' initial index '''
            if index == 0:
                intermediateWayPoint = self.initialWayPoint
                
            ''' aircraft fly '''
            endOfSimulation, deltaDistanceMeters , altitudeMeanSeaLevelMeters = self.aircraft.fly(
                                                                    elapsedTimeSeconds = elapsedTimeSeconds,
                                                                    deltaTimeSeconds = deltaTimeSeconds , 
                                                                    distanceStillToFlyMeters = distanceStillToFlyMeters,
                                                                    currentPosition =  intermediateWayPoint,
                                                                    distanceToLastFixMeters = distanceToLastFixMeters)
            ''' distance flown '''
            cumulatedLegDistanceMeters += deltaDistanceMeters
            distanceStillToFlyMeters -= deltaDistanceMeters
#             ''' if altitude above ground > 50 feet => move from take-off to initial climb '''
#             if ((altitudeMeanSeaLevelMeters - self.departureAirport.getFieldElevationAboveSeaLevelMeters())*Meter2Feet > 50.0):
#                 self.aircraft.setClimbConfiguration(elapsedTimeSeconds)
            
            ''' name the next way-point '''
            Name = ''
            if index == 0:
                Name = 'climb-ramp-pt-{0}-{1:.2f}-meters'.format(index, cumulatedLegDistanceMeters)
            #bearingDegrees = math.fmod ( runWayOrientationDegrees + 180.0 , 360.0 ) + 180.0
            bearingDegrees = runWayOrientationDegrees
            newIntermediateWayPoint = intermediateWayPoint.getWayPointAtDistanceBearing(Name = Name, 
                                                                                  DistanceMeters = deltaDistanceMeters, 
                                                                                  BearingDegrees = bearingDegrees)
            newIntermediateWayPoint.setAltitudeMeanSeaLevelMeters(altitudeMeanSeaLevelMeters)

            ''' update aircraft state vector '''
            elapsedTimeSeconds += deltaTimeSeconds
            newIntermediateWayPoint.setElapsedTimeSeconds(elapsedTimeSeconds)     
            
            ''' build Climb Ramp the core of the route '''
            self.addVertex(newIntermediateWayPoint)
            
            ''' replace the intermediate point '''
            intermediateWayPoint = newIntermediateWayPoint
            index += 1
        ''' set name of the last point '''
        Name = 'climb-ramp-pt-{0}-{1:.2f}-meters'.format(index, cumulatedLegDistanceMeters)
        newIntermediateWayPoint.setName(Name = Name)
 
 
class Test_ClimbRamp(unittest.TestCase):

    def test_ClimbRamp(self):
        
        atmosphere = Atmosphere()
        earth = Earth()
        
        print '==================== Three Degrees climb slope ==================== '+ time.strftime("%c")
        acBd = BadaAircraftDatabase()
        aircraftICAOcode = 'A320'
        if acBd.read():
            if ( acBd.aircraftExists(aircraftICAOcode) 
                 and acBd.aircraftPerformanceFileExists(aircraftICAOcode)):
                
                print '==================== aircraft found  ==================== '+ time.strftime("%c")
    
                aircraft = BadaAircraft(
                                    ICAOcode = aircraftICAOcode,
                                    aircraftFullName = acBd.getAircraftFullName(aircraftICAOcode),
                                    badaPerformanceFilePath = acBd.getAircraftPerformanceFile(aircraftICAOcode),
                                    atmosphere = atmosphere,
                                    earth = earth)
                aircraft.dump()
        
        assert not(aircraft is None)
        
        print '==================== get Charles Gaulle airport ==================== '+ time.strftime("%c")
        airportsDB = AirportsDatabase()
        assert(airportsDB.read())
        CharlesDeGaulle = airportsDB.getAirportFromICAOCode('LFPG')
        print CharlesDeGaulle
        assert not(aircraft is None)
        
        aircraft.setTargetCruiseFlightLevel(RequestedFlightLevel = 390, 
                                            departureAirportAltitudeMSLmeters = CharlesDeGaulle.getAltitudeMeanSeaLevelMeters())
    
     
        
        print '==================== Three Degrees climb slope==================== '+ time.strftime("%c")
        runWaysDatabase = RunWayDataBase()
        if runWaysDatabase.read():
            print 'runways DB correctly read'
        
        runway = runWaysDatabase.getFilteredRunWays('LFPG')
        print runway
            
        print '==================== Ground Run ==================== '+ time.strftime("%c")
        groundRun = GroundRunLeg(runway=runway, 
                                 aircraft=aircraft,
                                 airport=CharlesDeGaulle)
        groundRun.buildDepartureGroundRun(deltaTimeSeconds = 0.1,
                                    elapsedTimeSeconds = 0.0,
                                    distanceStillToFlyMeters = 100000.0,
                                    distanceToLastFixMeters = 100000.0)
        print '==================== Three Degrees climb slope==================== '+ time.strftime("%c")
    
        initialVertex = groundRun.getVertex(groundRun.getNumberOfVertices()-1)
        initialWayPoint = initialVertex.getWeight()
    
        climbRamp = ClimbRamp(initialWayPoint = initialWayPoint,
                               runway=runway, 
                               aircraft=aircraft, 
                               departureAirport=CharlesDeGaulle)
        
        climbRamp.buildClimbRamp(deltaTimeSeconds = 0.1,
                           elapsedTimeSeconds = 0.0, 
                           distanceStillToFlyMeters = 100000.0, 
                           distanceToLastFixMeters = 100000.0,
                           climbRampLengthNautics = 5.0 )
        groundRun.addGraph(climbRamp)
        
        groundRun.createKmlOutputFile()
        print "=========== ThreeDegreesGlideSlope end =========== " + time.strftime("%c")
    

if __name__ == '__main__':
    unittest.main()