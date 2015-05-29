# -*- coding: UTF-8 -*-
'''
Created on 31 December 2014

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

Manage the ground run phase

'''
import time
import math
from Home.aerocalc.airspeed import tas2cas

from Home.Environment.RunWaysDatabaseFile import RunWay, RunWayDataBase
from Home.Environment.AirportDatabaseFile import AirportsDatabase

from Home.Environment.Atmosphere import Atmosphere
from Home.Environment.Earth import Earth

from Home.Guidance.GraphFile import Graph
from Home.Guidance.WayPointFile import WayPoint, Airport

from Home.BadaAircraftPerformance.BadaAircraftFile import BadaAircraft
from Home.BadaAircraftPerformance.BadaAircraftDatabaseFile import BadaAircraftDatabase

Meter2Feet = 3.2808399 # feet (3 feet 3⅜ inches)
Knots2MetersPerSecond = 0.514444444 # meters / second
MeterPerSecond2Knots = 1.94384449 # 1 meter per second = 11.94384449 knots

class GroundRunLeg(Graph):
    '''
    ground run inputs are:
    1) airport field elevation above sea level (meters)
    2) runway true heading (in degrees)
    
    departure Ground Run :
    1) initial speed is 0.0 meters / second
    
    arrival Ground Run:
    1) final speed = taxi speed
    '''
    aircraft = None
    airport = None
    runway = None
    
    def __init__(self,
                 runway,
                 aircraft,
                 airport):
            
        ''' base class init '''
        Graph.__init__(self)
        self.className = self.__class__.__name__
        
        assert (isinstance(runway, RunWay) and not(runway is None))
        self.runway = runway
        print self.className + ': ground run - run-way true heading= ' + str(self.runway.getTrueHeadingDegrees()) + ' degrees'
        
        assert (isinstance(aircraft, BadaAircraft) and not(aircraft is None))
        self.aircraft = aircraft
        
        assert (isinstance(airport, Airport)  and not(airport is None))
        self.airport = airport
    
    
    def computeTouchDownWayPoint(self):
        ''' get landing length in meters '''
        landingLengthMeters = self.aircraft.getLandingLengthMeters()
        ''' run-way orientation '''
        runwayTrueHeadingDegrees = self.runway.getTrueHeadingDegrees()
        
        ''' run-way end point '''
        strRunWayEndPointName = self.airport.getName() + '-' + 'Rwy'+'-'+self.runway.getName()
        runWayEndPoint = WayPoint (Name = strRunWayEndPointName, 
                                    LatitudeDegrees = self.runway.getLatitudeDegrees(),
                                    LongitudeDegrees = self.runway.getLongitudeDegrees(),
                                    AltitudeMeanSeaLevelMeters =self.airport.getFieldElevationAboveSeaLevelMeters())
        
        strTouchDownWayPointName = self.airport.getName() + '-' + 'Rwy'+'-' + self.runway.getName() + '-' + 'touch-down'
        touchDownWayPoint = runWayEndPoint.getWayPointAtDistanceBearing(Name = strTouchDownWayPointName, 
                                                                        DistanceMeters = landingLengthMeters, 
                                                                        BearingDegrees = runwayTrueHeadingDegrees)
        touchDownWayPoint.setAltitudeMeanSeaLevelMeters(self.airport.getFieldElevationAboveSeaLevelMeters())
        return touchDownWayPoint
        
    
    def buildArrivalGroundRun(self,
                              deltaTimeSeconds,
                              elapsedTimeSeconds,
                              initialWayPoint):
        
        assert isinstance(initialWayPoint, WayPoint)
        ''' 
        speed decreases from 1.2 V Stall to taxi speed
        (according to the airport elevation stall speed changes with air density)
        '''
        ''' delta time in seconds '''
        elapsedTimeSeconds = elapsedTimeSeconds
        
        ''' get landing length in meters '''
        landingLengthMeters = self.aircraft.getLandingLengthMeters()
        ''' run-way orientation '''
        runwayTrueHeadingDegrees = self.runway.getTrueHeadingDegrees()
        runwayTrueHeadingDegrees = math.fmod(runwayTrueHeadingDegrees + 180.0, 360.0)

        ''' run-way end point '''
        strRunWayEndPointName = 'touch-down-rwy-'+ self.runway.getName() + '-' + self.airport.getName()
        ''' rename the initial way point '''
        initialWayPoint.setName(strRunWayEndPointName)

        ''' graph index '''
        index = 0
        
        distanceStillToFlyMeters = landingLengthMeters
        ''' loop until => end of simulation ( aircraft' speed reduced to the taxi speed = 15 knots) '''
        endOfSimulation = False
        while (endOfSimulation == False) :
            ''' initialisation '''
            if index == 0:
                intermediateWayPoint = initialWayPoint
                
            ''' fly => decrease the true air speed '''
            ''' during ground run => all the energy is used to increase the Kinetic energy => no potential energy increase '''
            endOfSimulation, deltaDistanceMeters , altitudeMeters = self.aircraft.fly(
                                                                    elapsedTimeSeconds = elapsedTimeSeconds,
                                                                    deltaTimeSeconds = deltaTimeSeconds , 
                                                                    distanceStillToFlyMeters = distanceStillToFlyMeters,
                                                                    currentPosition = intermediateWayPoint,
                                                                    distanceToLastFixMeters = 0.0)
            distanceStillToFlyMeters -= deltaDistanceMeters
            #trueAirSpeedMetersSecond = self.aircraft.getCurrentTrueAirSpeedMetersSecond()
            #print 'true air speed= ' + str(trueAirSpeedMetersSecond) + ' meters/second'
            
            ''' name of the next point '''
            Name = ''
            if index == 0:
                Name = 'ground-run-pt-{0}-{1:.2f}-meters'.format(index-1, deltaDistanceMeters)
            #bearingDegrees = math.fmod ( runwayTrueHeadingDegrees + 180.0 , 360.0 )
            bearingDegrees = runwayTrueHeadingDegrees
            newIntermediateWayPoint = intermediateWayPoint.getWayPointAtDistanceBearing(Name = Name, 
                                                                                  DistanceMeters = deltaDistanceMeters, 
                                                                                  BearingDegrees = bearingDegrees)
            ''' during the ground run - altitude = airport field elevation '''
            newIntermediateWayPoint.setAltitudeMeanSeaLevelMeters(self.airport.getFieldElevationAboveSeaLevelMeters())
            
            ''' update route way-point '''
            elapsedTimeSeconds += deltaTimeSeconds
            newIntermediateWayPoint.setElapsedTimeSeconds(elapsedTimeSeconds)
             
            ''' insert in the route '''
            self.addVertex(newIntermediateWayPoint)
            
            ''' copy the intermediate way-point '''
            intermediateWayPoint = newIntermediateWayPoint 
            ''' increment the index '''
            index += 1
  
        #print '============ end of arrival ground run ======================'
        strRunWayEndPointName = self.airport.getName() + '-' + 'rwy'+'-' + self.runway.getName()
        intermediateWayPoint.setName(Name = strRunWayEndPointName)
        
    
    def buildDepartureGroundRun(self, 
                                deltaTimeSeconds,
                                elapsedTimeSeconds,
                                distanceStillToFlyMeters,
                                distanceToLastFixMeters):
        ''' build the departure ground run
        '''
        
        ''' elapsedTimeSeconds in seconds '''
        elapsedTimeSeconds = elapsedTimeSeconds

        ''' run-way end point '''
        strRunWayEndPointName = self.airport.getName() + '-' + 'Rwy'+'-'+self.runway.getName()
        runWayEndPoint = WayPoint (Name=strRunWayEndPointName, 
                                    LatitudeDegrees=self.runway.getLatitudeDegrees(),
                                    LongitudeDegrees=self.runway.getLongitudeDegrees(),
                                    AltitudeMeanSeaLevelMeters=self.airport.getFieldElevationAboveSeaLevelMeters())
        ''' run-way true heading '''
        runwayTrueHeadingDegrees = self.runway.getTrueHeadingDegrees()
        ''' call base class Graph to build Climb Ramp core of the route '''
        index = 0
        self.addVertex(runWayEndPoint)
        index += 1
        
        ''' departure ground run => initial speed is null '''
        trueAirSpeedMetersSecond = 0.1
        ''' ground run leg distance '''
        totalLegDistanceMeters = 0.0
        self.aircraft.initStateVector(    elapsedTimeSeconds,
                                            trueAirSpeedMetersSecond,
                                            self.airport.getFieldElevationAboveSeaLevelMeters())
        ''' 
        Usually, the lift-off speed is designated to be 1.2 * Vstall 
        at a given weight, an aircraft will rotate and climb, stall or fly at an approach to landing at approx the same CAS.
        regardless of the elevation (height above sea level) , even though the true airspeed and ground-speed may differ significantly.
        These V speeds are normally published as IAS rather than CAS so they can be read directly from the airspeed indicator.
        '''
        VStallSpeedCASKnots = self.aircraft.computeStallSpeedCasKnots()
        print self.className + ': V stall Calibrated AirSpeed= {0:.2f} knots'.format(VStallSpeedCASKnots)
        ''' loop until Stall CAS reached '''
        endOfSimulation = False
        while ((endOfSimulation == False) and
               ( tas2cas(tas = trueAirSpeedMetersSecond ,
                       altitude = self.airport.getFieldElevationAboveSeaLevelMeters(),
                                                  temp='std',
                                                  speed_units = 'm/s',
                                                  alt_units = 'm') * MeterPerSecond2Knots )  < (1.2 * VStallSpeedCASKnots)):
            ''' initial loop index '''
            if index == 1:
                intermediateWayPoint = runWayEndPoint
                
            ''' fly => increase in true air speed '''
            ''' during ground run => all the energy is used to increase the Kinetic energy => no potential energy increase '''
            endOfSimulation, deltaDistanceMeters , altitudeMeters = self.aircraft.fly(
                                                                    elapsedTimeSeconds = elapsedTimeSeconds,
                                                                     deltaTimeSeconds = deltaTimeSeconds, 
                                                                     distanceStillToFlyMeters = distanceStillToFlyMeters,
                                                                     currentPosition  = intermediateWayPoint,
                                                                     distanceToLastFixMeters = distanceToLastFixMeters)
            trueAirSpeedMetersSecond = self.aircraft.getCurrentTrueAirSpeedMetersSecond()
            assert (((self.airport.getFieldElevationAboveSeaLevelMeters() - 10.0) <= altitudeMeters) and
                    ( altitudeMeters <= (self.airport.getFieldElevationAboveSeaLevelMeters() + 10.0)))
            #print self.className + ': delta distance= ' + str(deltaDistanceMeters) + ' meters'
            # name of the next point            
            totalLegDistanceMeters += deltaDistanceMeters
            distanceStillToFlyMeters -= deltaDistanceMeters
            distanceToLastFixMeters -= deltaDistanceMeters
            
            Name = ''
            if index == 1:
                Name = 'ground-run-pt-{0}-{1:.2f}-meters'.format(index-1, totalLegDistanceMeters)
            #bearingDegrees = math.fmod ( runwayTrueHeadingDegrees + 180.0 , 360.0 )
            bearingDegrees = runwayTrueHeadingDegrees
            newIntermediateWayPoint = intermediateWayPoint.getWayPointAtDistanceBearing(Name = Name, 
                                                                                  DistanceMeters = deltaDistanceMeters, 
                                                                                  BearingDegrees = bearingDegrees)
            ''' during the ground run - altitude = airport field elevation '''
            newIntermediateWayPoint.setAltitudeMeanSeaLevelMeters(self.airport.getFieldElevationAboveSeaLevelMeters())
            
            ''' update route waypoint '''
            elapsedTimeSeconds += deltaTimeSeconds
            newIntermediateWayPoint.setElapsedTimeSeconds(elapsedTimeSeconds)
 
            ''' insert in the route '''
            self.addVertex(newIntermediateWayPoint)
            
            ''' copy the intermediate way-point '''
            intermediateWayPoint = newIntermediateWayPoint 
            ''' increment the index '''
            index += 1
            
        ''' rename last point as take-off '''
        intermediateWayPoint.setName(Name = 'Take-Off-{0:.2f}-meters'.format(totalLegDistanceMeters))
   

if __name__ == '__main__':

    atmosphere = Atmosphere()
    earth = Earth()
    
    print '==================== Ground run ==================== '+ time.strftime("%c")
    acBd = BadaAircraftDatabase()
    aircraftICAOcode = 'A320'
    if acBd.read():
        if ( acBd.aircraftExists(aircraftICAOcode) 
             and acBd.aircraftPerformanceFileExists(acBd.getAircraftPerformanceFile(aircraftICAOcode))):
            
            print '==================== aircraft found  ==================== '+ time.strftime("%c")
            aircraft = BadaAircraft(aircraftICAOcode, 
                                  acBd.getAircraftPerformanceFile(aircraftICAOcode),
                                  atmosphere,
                                  earth)
            aircraft.dump()
    
    print '==================== Ground run ==================== '+ time.strftime("%c")
    airportsDB = AirportsDatabase()
    assert airportsDB.read()
    
    CharlesDeGaulle = airportsDB.getAirportFromICAOCode('LFPG')
    print CharlesDeGaulle
    
    print '==================== Ground run - read runway database ==================== '+ time.strftime("%c")
    runWaysDatabase = RunWayDataBase()
    assert runWaysDatabase.read()
    
    print '==================== Ground run ==================== '+ time.strftime("%c")
    runway = runWaysDatabase.getFilteredRunWays('LFPG', aircraft.WakeTurbulenceCategory)
    print runway
    
    print '==================== departure Ground run ==================== '+ time.strftime("%c")
    groundRun = GroundRunLeg(runway=runway, 
                             aircraft=aircraft,
                             airport=CharlesDeGaulle)
    groundRun.buildDepartureGroundRun(deltaTimeSeconds = 0.1,
                                elapsedTimeSeconds = 0.0,
                                distanceStillToFlyMeters = 100000.0)
    groundRun.createKmlOutputFile()
    groundRun.createXlsxOutputFile()
        
    print '==================== Get Arrival Airport ==================== '+ time.strftime("%c")
    arrivalAirportIcaoCode = 'LFML'
    arrivalAirport = airportsDB.getAirportFromICAOCode(arrivalAirportIcaoCode)
    print arrivalAirport
    
    print '====================  arrival run-way ==================== '+ time.strftime("%c")
    arrivalRunway = runWaysDatabase.getFilteredRunWays(arrivalAirportIcaoCode,
                                                        aircraft.WakeTurbulenceCategory)
    print arrivalRunway
    print '==================== arrival Ground run ==================== '+ time.strftime("%c")
#     aircraft.setLandingConfiguration(elapsedTimeSeconds = 0.0)
#     
#     aircraft.initStateVector(elapsedTimeSeconds = 0.0,
#                           trueAirSpeedMetersSecond = 101.0 * Knots2MetersPerSecond, 
#                           airportFieldElevationAboveSeaLevelMeters = arrivalAirport.getFieldElevationAboveSeaLevelMeters())
# 
#     groundRun = GroundRunLeg(runway = runway, 
#                              aircraft = aircraft,
#                              airport = CharlesDeGaulle)
#     groundRun.buildArrivalGroundRun(deltaTimeSeconds = 0.1,
#                               elapsedTimeSeconds = 0.0,
#                               initialWayPoint)
#     groundRun.createXlsxOutputFile()
#     groundRun.createKmlOutputFile()
