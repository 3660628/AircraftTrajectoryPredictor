# -*- coding: UTF-8 -*-
'''
Created on 17 December 2014

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


this class computes a turn leg.
the turn radius depends upon the speed of the aircraft
A turn leg connects two great circles, each great circle having a course-heading.

http://www.aerospaceweb.org/question/performance/q0146.shtml

extract from A320 Airbus instructor manual

The RADIUS OF TURN of the trajectory is a function of TAS and BANK.
TAS [kt] RADIUS (15° Φ) [NM] RADIUS (25° Φ) [NM]
150             1.2                 0.7
180             1.8                 1.0
210             2.4                 1.4
250             3.4                 2.0
300             4.9                 2.8
480             12.5                 7.2

'''
import time
import math
import unittest

from Home.aerocalc.airspeed import cas2tas

from Home.Environment.Atmosphere import Atmosphere
from Home.Environment.Earth import Earth

from Home.Guidance.GraphFile import Graph

from Home.Environment.AirportDatabaseFile import AirportsDatabase
from Home.Environment.RunWaysDatabaseFile import RunWayDataBase
from Home.Environment.WayPointsDatabaseFile import WayPointsDatabase

from Home.Guidance.GroundRunLegFile import GroundRunLeg
from Home.Guidance.DescentGlideSlopeFile import DescentGlideSlope

from Home.Guidance.BaseTurnLegFile import BaseTurnLeg
from Home.Guidance.WayPointFile import WayPoint

from Home.BadaAircraftPerformance.BadaAircraftDatabaseFile import BadaAircraftDatabase
from Home.BadaAircraftPerformance.BadaAircraftFile import BadaAircraft

Meter2Feet = 3.2808399 # one meter approx == 3 feet (3 feet 3â…œ inches)
MeterPerSecond2Knots = 1.9438444924406
Knot2MetersPerSecond = 0.514444444 # meters per second
Meter2NauticalMiles = 0.000539956803 # One Meter = 0.0005 nautical miles


class TurnLeg(Graph):

    className = ''
    initialWayPoint = None
    finalWayPoint = None
    initialHeadingDegrees = 0.0
    finalHeadingDegrees = 0.0
    aircraft = None
    ''' step is one degree if clock-wise or MINUS one degree if anti clock-wise '''
    stepDegrees = 0.0
    ''' reverse the graph -> used for the turn leg build from end of descent glide slope '''
    reverse = False
    listOfAngleDegrees = []
    
    def __init__(self, 
                 initialWayPoint, 
                 finalWayPoint,
                 initialHeadingDegrees, 
                 aircraft,
                 reverse=False):
        '''
        initial way point is the end of the previous great circle
        initial Heading is the last heading of the previous great circle
        final way point is the next fix
        '''
        
        Graph.__init__(self)
        self.className = self.__class__.__name__
        
        ''' link between time step of one second and 3 degrees per second turn rate '''
        ''' 3 degrees per second * 120 seconds = 360 degrees in 2 minutes '''
        self.BaseStepDegrees = 3.0
        
        assert (reverse == True) or (reverse == False)
        self.reverse = reverse
                
        ''' sanity check initialWayPoint '''''''''''
        assert (isinstance(initialWayPoint, WayPoint))
        self.initialWayPoint = initialWayPoint

        ''' sanity check finalWayPoint '''''''''''
        assert (isinstance(finalWayPoint, WayPoint))
        self.finalWayPoint = finalWayPoint

        ''' sanity check initialHeadingDegrees '''''''''''
        assert isinstance(initialHeadingDegrees, float)
        assert (initialHeadingDegrees >= 0.0)
        assert (initialHeadingDegrees <= 360.0)
        self.initialHeadingDegrees = initialHeadingDegrees
        
        ''' sanity check final Heading Degrees '''
        if reverse == True:
            ''' build a turn backwards from last glide slope point to last fix ''' 
            ''' initial is first glide slope point and final is the last fix of the route '''
            self.finalHeadingDegrees = self.finalWayPoint.getBearingDegreesTo(self.initialWayPoint)
            self.finalHeadingDegrees = math.fmod ( self.finalHeadingDegrees + 180.0 , 360.0 )
        else:
            self.finalHeadingDegrees = initialWayPoint.getBearingDegreesTo(finalWayPoint)
            
        ''' sanity checks '''
        assert (self.finalHeadingDegrees >= 0.0) 
        assert (self.finalHeadingDegrees <= 360.0)
        
        ''' sanity check aircraft '''''''''''
        assert (isinstance(aircraft, BadaAircraft))
        self.aircraft = aircraft
                
        ''' compute angle difference '''
        #print self.className + ': turn from= {0:.2f} degrees to {1:.2f} degrees'.format(self.initialHeadingDegrees, self.finalHeadingDegrees)
        
        ''' default value - for turn angle steps '''
        self.stepDegrees = self.BaseStepDegrees # degrees

        ''' turn clock wise or anti clock wise '''
        initialAngleRadians = math.radians(self.initialHeadingDegrees)
        finalAngleRadians = math.radians(self.finalHeadingDegrees)
        angleDifferenceDegrees = math.degrees(math.atan2(math.sin(finalAngleRadians-initialAngleRadians), math.cos(finalAngleRadians-initialAngleRadians)))
        if (angleDifferenceDegrees < 0.0):
            self.stepDegrees = - self.BaseStepDegrees
        else:
            self.stepDegrees = + self.BaseStepDegrees
        
        strMsg = ': turn from= {0:.2f} degrees '.format(self.initialHeadingDegrees)
        strMsg += ' to {0:.2f} degrees'.format(self.finalHeadingDegrees)
        strMsg += ' - turn step is= {0:.2f} degrees'.format(self.stepDegrees) 
                                                
        print self.className + strMsg
        self.previousDistanceToArrivalAxisMeters = 0.0
        
    def buildTurnLeg(self, 
                     deltaTimeSeconds,
                     elapsedTimeSeconds,
                     distanceStillToFlyMeters,
                     distanceToLastFixMeters,
                     finalHeadingDegrees = 0.0,
                     lastTurn = False,
                     bankAngleDegrees = 15.0):
        
        ''' start building a set of turning legs from initial heading to final heading '''
        ''' heading changes according to an aircraft speed => radius of turn '''
        ''' for the last turn => final heading is the heading of run-way '''
        if lastTurn == True:
            self.finalHeadingDegrees = finalHeadingDegrees
        
        ''' initial altitude '''
        altitudeMeanSeaLevelMeters = self.aircraft.getCurrentAltitudeSeaLevelMeters()
        
        ''' if it is the last turn then need to reach the final way point => top of glide slope '''
        tasMetersPerSecond = self.aircraft.getCurrentTrueAirSpeedMetersSecond()
        tasKnots = tasMetersPerSecond * MeterPerSecond2Knots
        
        ''' Radius = (tas*tas) / (gravity * tan(bank angle = 15 degrees)) '''
        radiusOfTurnMeters = (tasMetersPerSecond * tasMetersPerSecond) / (9.81 * math.tan(math.radians(bankAngleDegrees)))
        if ((2*radiusOfTurnMeters) > self.initialWayPoint.getDistanceMetersTo(self.finalWayPoint)):
            ''' increase bank angle to 25 degrees and decrease turn radius '''
            radiusOfTurnMeters = (tasMetersPerSecond * tasMetersPerSecond) / (9.81 * math.tan(math.radians(25.0)))
        ''' case of last turn '''
        if lastTurn == True:
            tasMetersPerSecond = cas2tas(cas = self.aircraft.computeLandingStallSpeedCasKnots(),
                                               altitude = altitudeMeanSeaLevelMeters,
                                               temp = 'std',
                                               speed_units = 'kt',
                                               alt_units = 'm' ) * Knot2MetersPerSecond
            tasKnots = tasMetersPerSecond * MeterPerSecond2Knots
        
            ''' Radius = (tas*tas) / (gravity * tan(bank angle = 15 degrees)) '''
            radiusOfTurnMeters = (tasMetersPerSecond * tasMetersPerSecond) / (9.81 * math.tan(math.radians(bankAngleDegrees)))
        
        print self.className + ': tas= {0:.2f} knots - radius of turn= {1:.2f} meters - radius of turn= {2:.2f} nautics'.format(tasKnots, radiusOfTurnMeters, radiusOfTurnMeters*Meter2NauticalMiles)            
        ''' index used to initialise the loop '''        
        index = 0
            
        ''' build a list that can be reversed afterwards '''
        turnLegList = []
        
        ''' initial time management '''
        ''' 1.0 seconds delta time means THREE degrees turn every second '''
        elapsedTimeSeconds = elapsedTimeSeconds
        
        ''' loop from initial heading to final heading '''
        continueTurning = True
        currentHeadingDegrees = self.initialHeadingDegrees
        print self.className + ': initial heading= {0:.2f} degrees'.format(self.initialHeadingDegrees)
        passedThrough360 = False
        endOfSimulation = False
        while ( (endOfSimulation == False) and (continueTurning == True)):
            ''' initial index - loop initialisation '''
            #print 'altitude= ' + str(altitudeMeanSeaLevelMeters) + ' meters'
            
            ''' init the loop '''
            if index == 0:
                ''' set initial way Point altitude '''
                self.initialWayPoint.setAltitudeAboveSeaLevelMeters(altitudeMeanSeaLevelMeters)             
                ''' prepare for the next round '''
                intermediateWayPoint = self.initialWayPoint
            
            ''' aircraft fly '''
            endOfSimulation, deltaDistanceMeters , altitudeMeanSeaLevelMeters = self.aircraft.fly(
                                                                    elapsedTimeSeconds = elapsedTimeSeconds,
                                                                    deltaTimeSeconds = deltaTimeSeconds , 
                                                                     distanceStillToFlyMeters = distanceStillToFlyMeters,
                                                                     currentPosition = intermediateWayPoint,
                                                                     distanceToLastFixMeters = distanceToLastFixMeters)
            ''' update elapsed time seconds '''
            elapsedTimeSeconds += deltaTimeSeconds
            ''' update distance to fly '''
            distanceStillToFlyMeters -= deltaDistanceMeters
            ''' compute delta heading '''
            deltaHeadingDegrees = math.degrees(math.atan(deltaDistanceMeters / radiusOfTurnMeters))
            #print self.className + ': delta distance= {0:.2f} meters - delta Heading = {1:.2f} degrees'.format(deltaDistanceMeters, deltaHeadingDegrees)
            if self.stepDegrees > 0:
                ''' turn clock-wise => angle increases '''
                currentHeadingDegrees += deltaHeadingDegrees
                #print currentHeadingDegrees ,
                if self.initialHeadingDegrees <= self.finalHeadingDegrees:
                    continueTurning = (currentHeadingDegrees <= self.finalHeadingDegrees)
                else:
                    ''' need to pass through 360.0 before increasing again '''
                    if passedThrough360 == False:
                        if currentHeadingDegrees <= 360.0:
                            continueTurning = (currentHeadingDegrees <= 360.0)
                        else:
                            passedThrough360 = True
                            currentHeadingDegrees = math.fmod(currentHeadingDegrees, 360.0)
                            continueTurning = (currentHeadingDegrees <= self.finalHeadingDegrees)
                    else:
                        currentHeadingDegrees = math.fmod(currentHeadingDegrees, 360.0)
                        continueTurning = (currentHeadingDegrees <= self.finalHeadingDegrees)
                        
            else:
                ''' turning anti clock-wise => angle decreases '''
                currentHeadingDegrees -= deltaHeadingDegrees
                if self.initialHeadingDegrees >= self.finalHeadingDegrees:
                    continueTurning = (currentHeadingDegrees >= self.finalHeadingDegrees)
                else:
                    ''' need to pass through 360.0 '''
                    if passedThrough360 == False:
                        if currentHeadingDegrees >= 0.0:
                            continueTurning = (currentHeadingDegrees >= 0.0)
                        else:
                            passedThrough360 = True
                            currentHeadingDegrees = math.fmod(currentHeadingDegrees + 360.0, 360.0)
                            continueTurning = (currentHeadingDegrees >= self.finalHeadingDegrees)
                    else:
                        currentHeadingDegrees = math.fmod(currentHeadingDegrees + 360.0, 360.0)
                        continueTurning = (currentHeadingDegrees >= self.finalHeadingDegrees)
                
            ''' define the name of the new way-point '''
            name = 'turn-pt-{0}-{1:.2f}-degrees'.format(index, currentHeadingDegrees)
            ''' patch do not define a name as it slows opening the KML file in Google Earth '''
            name = ''
            #print self.className + ' next way-point= ' + name
            ''' convert heading into bearing '''
            bearingDegrees = math.fmod ( currentHeadingDegrees + 180.0 , 360.0 ) - 180.0
            newIntermediateWayPoint = intermediateWayPoint.getWayPointAtDistanceBearing(
                                                                                        Name = name, 
                                                                                  DistanceMeters = deltaDistanceMeters, 
                                                                                  BearingDegrees = bearingDegrees)
            
#             if lastTurn == True:
#                 arrivalTouchDownWayPoint = self.aircraft.getArrivalRunwayTouchDownWayPoint()
#                 distanceToArrivalTouchDownMeters = newIntermediateWayPoint.getDistanceMetersTo(arrivalTouchDownWayPoint)
#                 arrivalRunWayBearingDegrees = math.fmod ( self.finalHeadingDegrees + 180.0 , 360.0 )
#                 pointAlongRunwayAxis = arrivalTouchDownWayPoint.getWayPointAtDistanceBearing(Name = '',
#                                                                                       DistanceMeters = distanceToArrivalTouchDownMeters,
#                                                                                       BearingDegrees = arrivalRunWayBearingDegrees)
#                 distanceToArrivalRunwayAxis = newIntermediateWayPoint.getDistanceMetersTo(pointAlongRunwayAxis)
#                 print self.className + ': distance to arrival runway axis= {0:.2f} meters'.format(distanceToArrivalRunwayAxis)
#                 if (self.previousDistanceToArrivalAxisMeters > 1.0) and (distanceToArrivalRunwayAxis > self.previousDistanceToArrivalAxisMeters):
#                     continueTurning = False 
#                 self.previousDistanceToArrivalAxisMeters = distanceToArrivalRunwayAxis
                
            newIntermediateWayPoint.setAltitudeAboveSeaLevelMeters(altitudeMeanSeaLevelMeters)
            newIntermediateWayPoint.setElapsedTimeSeconds(elapsedTimeSeconds)
            '''  28 March 2015 - final angle needs to be updated as the aircraft turns '''
            ''' except if we are performing the last turn '''
            if lastTurn == False:
                self.finalHeadingDegrees = newIntermediateWayPoint.getBearingDegreesTo(self.finalWayPoint)

            ''' increment the index '''
            index += 1
            ''' insert in the route '''
            #print index , type(index)
            turnLegList.append(newIntermediateWayPoint)
            ''' copy the intermediate '''
            intermediateWayPoint = newIntermediateWayPoint
            
        ''' set name of last point '''
        name = 'turn-pt-{0}-{1:.2f}-degrees'.format(index, currentHeadingDegrees)
        newIntermediateWayPoint.setName(name)
        ''' reverse the list if needed => and build the route  '''
        if self.reverse == True:
            ''' reverse the order and build the graph '''
            for point in reversed(turnLegList):
                self.addVertex(point)
        else:
            ''' do not reverse it '''
            for point in turnLegList:
                self.addVertex(point)
        
        '''' print final heading  '''
        print self.className + ': final heading= {0:.2f} degrees'.format(currentHeadingDegrees)
        return endOfSimulation


    def buildSimulatedArrivalTurnLeg(self, 
                                     deltaTimeSeconds,
                                     elapsedTimeSeconds = 0.0, 
                                     distanceStillToFlyMeters = 0.0,
                                     simulatedAltitudeSeaLevelMeters = 0.0,
                                     flightPathAngleDegrees = 3.0 ):
        
        ''' the simulated arrival turn leg is built backwards 
        from the start of the descending glide slope backwards to a distance as top of glide slope '''
        
        ''' use base class that returns a list of angles in degrees '''
        ''' WARNING = 3 degrees per second => if delta time = 1 second then step Degrees = 3 degrees '''
        baseTurnLeg = BaseTurnLeg(self.initialHeadingDegrees, self.finalHeadingDegrees, self.stepDegrees)
        self.listOfAngleDegrees = baseTurnLeg.build()
        
        ''' index used to initialise the loop '''        
        index = 0
            
        ''' build a list that can be reversed afterwards '''
        turnLegList = []
        ''' initial altitude '''
        altitudeMeanSeaLevelMeters = simulatedAltitudeSeaLevelMeters
        ''' initial time management '''
        ''' 1.0 seconds delta time means THREE degrees turn every second '''
        elapsedTimeSeconds = elapsedTimeSeconds
        
        ''' loop through the list of angles '''
        for angleDegrees in self.listOfAngleDegrees:
            ''' initial index - loop initialisation '''
            #print 'altitude= ' + str(altitudeMeanSeaLevelMeters) + ' meters'
            
            ''' init the loop '''
            if index == 0:
                ''' set initial way Point altitude '''
                self.initialWayPoint.setAltitudeAboveSeaLevelMeters(altitudeMeanSeaLevelMeters)             
                ''' prepare for the next round '''
                intermediateWayPoint = self.initialWayPoint
            
            ''' aircraft fly '''
            trueAirspeedMeterSeconds = cas2tas(cas = self.aircraft.computeLandingStallSpeedCasKnots(),
                                               altitude = simulatedAltitudeSeaLevelMeters,
                                               temp = 'std',
                                               speed_units = 'kt',
                                               alt_units = 'm' ) * Knot2MetersPerSecond
            deltaDistanceMeters = trueAirspeedMeterSeconds * deltaTimeSeconds 
            altitudeMeanSeaLevelMeters = altitudeMeanSeaLevelMeters + trueAirspeedMeterSeconds * math.sin(math.radians(flightPathAngleDegrees))
            ''' update elapsed time '''
            elapsedTimeSeconds += deltaTimeSeconds

            ''' distance over flown for each degree - depends upon true air speed '''
            #print self.className + ': distance flown when 1 degrees of heading angle changes= '+ str(distanceMeters) + ' meters'
                
            ''' define the name of the new way-point '''
            name = 'turn-pt-{0}-{1:.2f}-degrees'.format(index, angleDegrees)
            #print self.className + ' next way-point= ' + name
            ''' convert heading into bearing '''
            bearingDegrees = math.fmod ( angleDegrees + 180.0 , 360.0 ) - 180.0
            newIntermediateWayPoint = intermediateWayPoint.getWayPointAtDistanceBearing(Name=name, 
                                                                                  DistanceMeters=deltaDistanceMeters, 
                                                                                  BearingDegrees=bearingDegrees)
            newIntermediateWayPoint.setAltitudeAboveSeaLevelMeters(altitudeMeanSeaLevelMeters)
            newIntermediateWayPoint.setElapsedTimeSeconds(elapsedTimeSeconds)

            ''' increment the index '''
            index += 1
            ''' insert in the route '''
            #print index , type(index)
            turnLegList.append(newIntermediateWayPoint)
            ''' copy the intermediate '''
            intermediateWayPoint = newIntermediateWayPoint
        
         
        ''' reverse the list if needed => and build the route  '''
        if self.reverse == True:
            ''' reverse the order and build the graph '''
            index = 0
            for point in reversed(turnLegList):
                self.addVertex(index, point)
                index += 1
        else:
            ''' do not reverse it '''
            index = 0
            for point in turnLegList:
                self.addVertex(index, point)
                index += 1
        
        ''''''''' print location of the last point of the route '''
        assert (self.getNumberOfVertices()>1)
        lastVertex = self.getVertex(self.getNumberOfVertices()-1)
        lastWayPoint = lastVertex.getWeight()
        print 'location of the last point ' + str(lastWayPoint)
        
        
    def buildNewSimulatedArrivalTurnLeg(self, 
                                        deltaTimeSeconds,
                                     elapsedTimeSeconds = 0.0, 
                                     distanceStillToFlyMeters = 0.0,
                                     simulatedAltitudeSeaLevelMeters = 660.0,
                                     flightPathAngleDegrees = 3.0 ,
                                     bankAngleDegrees = 5.0):
        
        ''' if it is the last turn then need to reach the final way point => top of glide slope '''
        tasMetersPerSecond = cas2tas(cas = self.aircraft.computeLandingStallSpeedCasKnots(),
                                               altitude = simulatedAltitudeSeaLevelMeters,
                                               temp = 'std',
                                               speed_units = 'kt',
                                               alt_units = 'm' ) * Knot2MetersPerSecond
        tasKnots = tasMetersPerSecond * MeterPerSecond2Knots
        
        ''' Radius = (tas*tas) / (gravity * tan(bank angle = 15 degrees)) '''
        radiusOfTurnMeters = (tasMetersPerSecond * tasMetersPerSecond) / (9.81 * math.tan(math.radians(bankAngleDegrees)))
        print self.className + ': tas= {0:.2f} knots - radius of turn= {1:.2f} meters - radius of turn= {2:.2f} nautics'.format(tasKnots, radiusOfTurnMeters, radiusOfTurnMeters*Meter2NauticalMiles)            
 
        ''' index used to initialise the loop '''        
        index = 0
        ''' build a list that can be reversed afterwards '''
        turnLegList = []
        ''' initial altitude '''
        altitudeMeanSeaLevelMeters = simulatedAltitudeSeaLevelMeters
        ''' initial time management '''
        ''' 1.0 seconds delta time means THREE degrees turn every second '''
        elapsedTimeSeconds = elapsedTimeSeconds
        
        ''' loop from initial heading to final heading '''
        continueTurning = True
        currentHeadingDegrees = self.initialHeadingDegrees
        print self.className + ': initial heading= {0:.2f} degrees'.format(self.initialHeadingDegrees)
        passedThrough360 = False

        while (  continueTurning == True ):
            
            ''' init the loop '''
            if index == 0:
                ''' set initial way Point altitude '''
                self.initialWayPoint.setAltitudeAboveSeaLevelMeters(altitudeMeanSeaLevelMeters)             
                ''' prepare for the next round '''
                intermediateWayPoint = self.initialWayPoint
    
            deltaDistanceMeters = tasMetersPerSecond * deltaTimeSeconds
            ''' compute delta heading '''
            deltaHeadingDegrees = math.degrees(math.atan(deltaDistanceMeters / radiusOfTurnMeters))

            if self.stepDegrees > 0:
                ''' turn clock-wise => angle increases '''
                currentHeadingDegrees += deltaHeadingDegrees
                #print currentHeadingDegrees ,
                if self.initialHeadingDegrees <= self.finalHeadingDegrees:
                    continueTurning = (currentHeadingDegrees <= self.finalHeadingDegrees)
                else:
                    ''' need to pass through 360.0 before increasing again '''
                    if passedThrough360 == False:
                        if currentHeadingDegrees <= 360.0:
                            continueTurning = (currentHeadingDegrees <= 360.0)
                        else:
                            passedThrough360 = True
                            currentHeadingDegrees = math.fmod(currentHeadingDegrees, 360.0)
                            continueTurning = (currentHeadingDegrees <= self.finalHeadingDegrees)
                    else:
                        currentHeadingDegrees = math.fmod(currentHeadingDegrees, 360.0)
                        continueTurning = (currentHeadingDegrees <= self.finalHeadingDegrees)
                        
            else:
                ''' turning anti clock-wise => angle decreases '''
                currentHeadingDegrees -= deltaHeadingDegrees
                if self.initialHeadingDegrees >= self.finalHeadingDegrees:
                    continueTurning = (currentHeadingDegrees >= self.finalHeadingDegrees)
                else:
                    ''' need to pass through 360.0 '''
                    if passedThrough360 == False:
                        if currentHeadingDegrees >= 0.0:
                            continueTurning = (currentHeadingDegrees >= 0.0)
                        else:
                            passedThrough360 = True
                            currentHeadingDegrees = math.fmod(currentHeadingDegrees + 360.0, 360.0)
                            continueTurning = (currentHeadingDegrees >= self.finalHeadingDegrees)
                    else:
                        currentHeadingDegrees = math.fmod(currentHeadingDegrees + 360.0, 360.0)
                        continueTurning = (currentHeadingDegrees >= self.finalHeadingDegrees)
                
            ''' define the name of the new way-point '''
            name = 'turn-pt-{0}-{1:.2f}-degrees'.format(index, currentHeadingDegrees)
            #print self.className + ' next way-point= ' + name
            ''' convert heading into bearing '''
            bearingDegrees = math.fmod ( currentHeadingDegrees + 180.0 , 360.0 ) - 180.0
            newIntermediateWayPoint = intermediateWayPoint.getWayPointAtDistanceBearing(Name=name, 
                                                                                  DistanceMeters=deltaDistanceMeters, 
                                                                                  BearingDegrees=bearingDegrees)
            newIntermediateWayPoint.setAltitudeAboveSeaLevelMeters(altitudeMeanSeaLevelMeters)
            newIntermediateWayPoint.setElapsedTimeSeconds(elapsedTimeSeconds)
            '''  28 March 2015 - final angle needs to be updated as the aircraft turns '''
            self.finalHeadingDegrees = newIntermediateWayPoint.getBearingDegreesTo(self.finalWayPoint)

            ''' increment the index '''
            index += 1
            ''' insert in the route '''
            #print index , type(index)
            turnLegList.append(newIntermediateWayPoint)
            ''' copy the intermediate '''
            intermediateWayPoint = newIntermediateWayPoint
    
            ''' reverse the list if needed => and build the route  '''
        if self.reverse == True:
            ''' reverse the order and build the graph '''
            for point in reversed(turnLegList):
                self.addVertex(point)
                index += 1
        else:
            ''' do not reverse it '''
            for point in turnLegList:
                self.addVertex(point)
        


class Test_TurnLeg(unittest.TestCase):

    def test_TurnLeg(self):

        print '==================== Turn Leg ==================== '+ time.strftime("%c")
        atmosphere = Atmosphere()
        earth = Earth()
        
        acBd = BadaAircraftDatabase()
        aircraftICAOcode = 'A320'
        assert acBd.read()
        assert acBd.aircraftExists(aircraftICAOcode) 
        assert acBd.aircraftPerformanceFileExists(aircraftICAOcode)
                
        print '==================== aircraft found  ==================== '+ time.strftime("%c")
        aircraft = BadaAircraft(ICAOcode = aircraftICAOcode, 
                                aircraftFullName = acBd.getAircraftFullName(aircraftICAOcode),
                                badaPerformanceFilePath = acBd.getAircraftPerformanceFile(aircraftICAOcode),
                                atmosphere = atmosphere,
                                earth = earth)
        aircraft.dump()
                
        print '==================== Get Airport ==================== '+ time.strftime("%c")
        airportsDB = AirportsDatabase()
        assert airportsDB.read()
        
        print '==================== Get Arrival Airport ==================== '+ time.strftime("%c")
        Lisbonne = airportsDB.getAirportFromICAOCode('LPPT')
        print Lisbonne
        
        print '====================  find the run-ways ==================== '+ time.strftime("%c")
        runWaysDatabase = RunWayDataBase()
        if runWaysDatabase.read():
            print 'runways DB correctly read'
            
        print '====================  take off run-way ==================== '+ time.strftime("%c")
        arrivalRunway = runWaysDatabase.getFilteredRunWays(
                                                           airportICAOcode = 'LPPT', 
                                                           runwayName = '')
        print arrivalRunway
        
        print '==================== Ground run ==================== '+ time.strftime("%c")
        groundRun = GroundRunLeg(runway = arrivalRunway, 
                                 aircraft = aircraft,
                                 airport = Lisbonne)
        
        touchDownWayPoint = groundRun.computeTouchDownWayPoint()
        print touchDownWayPoint
        groundRun.buildDepartureGroundRun(deltaTimeSeconds = 1.0,
                                          elapsedTimeSeconds = 0.0,
                                          distanceStillToFlyMeters = 0.0,
                                          distanceToLastFixMeters = 0.0)
        print '==================== Climb Ramp ==================== '+ time.strftime("%c")
        
        initialWayPoint = groundRun.getLastVertex().getWeight()
    
        descentGlideSlope = DescentGlideSlope( runway   = arrivalRunway,
                                                aircraft = aircraft,
                                                arrivalAirport = Lisbonne ,
                                                descentGlideSlopeDegrees = 3.0)
        ''' if there is a fix nearer to 5 nautics of the touch-down then limit size of simulated glide slope '''
    
        descentGlideSlope.buildSimulatedGlideSlope(descentGlideSlopeSizeNautics = 5.0)
        descentGlideSlope.createKmlOutputFile()
        
        firstGlideSlopeWayPoint = descentGlideSlope.getVertex(v=0).getWeight()
    
        print '==================== Climb Ramp ==================== '+ time.strftime("%c")
        initialWayPoint = groundRun.getLastVertex().getWeight()
    
        print ' ================== turn leg end =============== '
        wayPointsDb = WayPointsDatabase()
        assert (wayPointsDb.read())
        Exona = wayPointsDb.getWayPoint('EXONA')
        Rosal = wayPointsDb.getWayPoint('ROSAL')
    
        print Rosal.getBearingDegreesTo(Exona) 
        initialHeadingDegrees = arrivalRunway.getTrueHeadingDegrees()
        
        lastTurnLeg = TurnLeg( initialWayPoint = firstGlideSlopeWayPoint, 
                               finalWayPoint = Exona,
                               initialHeadingDegrees = initialHeadingDegrees, 
                               aircraft = aircraft,
                               reverse = True)
        deltaTimeSeconds = 1.0
        lastTurnLeg.buildNewSimulatedArrivalTurnLeg(deltaTimeSeconds = deltaTimeSeconds,
                                                     elapsedTimeSeconds = 0.0,
                                                     distanceStillToFlyMeters = 0.0,
                                                     simulatedAltitudeSeaLevelMeters = firstGlideSlopeWayPoint.getAltitudeMeanSeaLevelMeters(),
                                                     flightPathAngleDegrees = 3.0)
        lastTurnLeg.createKmlOutputFile()
        descentGlideSlope.addGraph(lastTurnLeg)
        #descentGlideSlope.createXlsxOutputFile()
        descentGlideSlope.createKmlOutputFile()
        
        print ' ================== turn leg end =============== '

if __name__ == '__main__':
    unittest.main()
    