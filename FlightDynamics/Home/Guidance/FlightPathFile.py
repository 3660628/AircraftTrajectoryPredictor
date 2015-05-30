'''
Created on 3 february 2015

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

@ TODO: create a flight list class (with only fixes) , a flight plan with Lat-Long and the flight Path

manage a flight path built from a flight plan
ensure a decoupling between the lateral path and the vertical path.

To simplify the prediction process, the horizontal and vertical components of the trajectory are de-coupled.

The flight legs are consisting of a series of straight-line (great-circle) segments connected by constant radius turns.
The aircraft speed is used to calculate a turn radius.
'''

import math

from Home.Environment.Atmosphere import Atmosphere
from Home.Environment.Earth import Earth

from Home.Guidance.FlightPlanFile import FlightPlan
from Home.Guidance.GroundRunLegFile import GroundRunLeg
from Home.Guidance.ClimbRampFile import ClimbRamp
from Home.Guidance.TurnLegFile import TurnLeg
from Home.Guidance.GreatCircleRouteFile import GreatCircleRoute
from Home.Guidance.DescentGlideSlopeFile import DescentGlideSlope
from Home.Guidance.WayPointFile import Airport

from Home.BadaAircraftPerformance.BadaAircraftDatabaseFile import BadaAircraftDatabase
from Home.BadaAircraftPerformance.BadaAircraftFile import BadaAircraft

Meter2Feet = 3.2808 # one meter equals 3.28 feet
Meter2NauticalMiles = 0.000539956803 # One Meter = 0.0005 nautical miles
NauticalMiles2Meters = 1852.0
Kilogram2Pounds = 2.20462262 # 1 kilogram = 2.204 lbs

class FlightPath(FlightPlan):
    
    flightPlan = None
    aircraftICAOcode = ''
    
    def __init__(self, 
                 route, 
                 aircraftICAOcode = 'A320', 
                 RequestedFlightLevel = 330.0, 
                 cruiseMach = 0.8, 
                 takeOffMassKilograms = 62000.0):
        
        self.className = self.__class__.__name__
        FlightPlan.__init__(self, route)
        ''' first bad and incomplete flight length '''
        ''' missing last turn and glide slope '''
        self.flightLengthMeters = self.computeLengthMeters() 
        
        self.aircraftICAOcode = aircraftICAOcode

        self.aircraft = None
        self.getAircraft()
        assert isinstance(self.aircraft, BadaAircraft) and not(self.aircraft is None)
        self.aircraft.setAircraftMassKilograms(takeOffMassKilograms)
        
        assert RequestedFlightLevel >= 15.0 and RequestedFlightLevel <= 450.0
        self.aircraft.setTargetCruiseFlightLevel(RequestedFlightLevel = RequestedFlightLevel, 
                                                 departureAirportAltitudeMSLmeters = self.getDepartureAirport().getFieldElevationAboveSeaLevelMeters())
        self.aircraft.setTargetCruiseMach(cruiseMachNumber = cruiseMach)
        
        self.arrivalAirport = self.getArrivalAirport()
        assert isinstance(self.arrivalAirport, Airport) and not(self.arrivalAirport is None)
        
        self.departureAirport = self.getDepartureAirport()
        assert isinstance(self.departureAirport, Airport) and not(self.departureAirport is None)

        
    def getAircraft(self):
        
        print self.className + ': ================ get aircraft ================='
        atmosphere = Atmosphere()
        earth = Earth()
        acBd = BadaAircraftDatabase()
        assert acBd.read()
        
        if ( acBd.aircraftExists(self.aircraftICAOcode) and
             acBd.aircraftPerformanceFileExists(self.aircraftICAOcode)):
            
            print self.className +': performance file= {0}'.format(acBd.getAircraftPerformanceFile(self.aircraftICAOcode))
            self.aircraft = BadaAircraft(ICAOcode = self.aircraftICAOcode, 
                                         aircraftFullName = acBd.getAircraftFullName(self.aircraftICAOcode),
                                  badaPerformanceFilePath = acBd.getAircraftPerformanceFile(self.aircraftICAOcode),
                                  atmosphere = atmosphere,
                                  earth = earth)
            self.aircraft.dump()
        else:
            raise ValueError(self.className + ': aircraft not found= ' + self.aircraftICAOcode)


    def printPassedWayPoint(self, finalWayPoint):
        
        minutes, seconds = divmod(finalWayPoint.getElapsedTimeSeconds(), 60)
        distanceFlownNautics = self.finalRoute.getLengthMeters() * Meter2NauticalMiles
        strMsg = ': passing waypoint: {0} - alt= {1:.2f} meters - alt= {2:.2f} feet - distance= {3:.2f} nautics'.format(
                                                    finalWayPoint.getName(),
                                                    finalWayPoint.getAltitudeMeanSeaLevelMeters(),
                                                    finalWayPoint.getAltitudeMeanSeaLevelMeters() * Meter2Feet,
                                                    distanceFlownNautics)
        elapsedTimeSeconds = finalWayPoint.getElapsedTimeSeconds()
        if elapsedTimeSeconds >= 60.0 and elapsedTimeSeconds < 3600.0:
            minutes, seconds = divmod(elapsedTimeSeconds, 60)
          
            strMsg += ' - real time = {0:.2f} seconds - {1:.2f} minutes {2:.2f} seconds'.format(elapsedTimeSeconds, minutes, seconds)
        else:
            minutes, seconds = divmod(elapsedTimeSeconds, 60)
            hours, minutes = divmod(minutes, 60)
            strMsg += ' - real time = {0:.2f} seconds - {1:.2f} hours {2:.2f} minutes {3:.2f} seconds'.format(elapsedTimeSeconds, hours, minutes, seconds)

        print self.className + strMsg
        
        
    def turnAndFly(self, 
                   tailWayPoint, 
                   headWayPoint,
                   initialHeadingDegrees,
                   headWayPointIndex):
        ''' 
        execute a turn to align true heading and then fly a great circle 
        '''    
        print ' ================== one Turn Leg for each fix in the list =============== '
        turnLeg = TurnLeg(  initialWayPoint  = tailWayPoint,
                                finalWayPoint    = headWayPoint,
                                initialHeadingDegrees = initialHeadingDegrees,
                                aircraft = self.aircraft,
                                reverse = False)
        
        distanceToLastFixMeters = self.computeDistanceToLastFixMeters(currentPosition = tailWayPoint,
                                                                      fixListIndex = headWayPointIndex)
        print self.className + ': distance to last fix= {0} nautics'.format(distanceToLastFixMeters * Meter2NauticalMiles)
        distanceStillToFlyMeters = self.flightLengthMeters - self.finalRoute.getLengthMeters()
        print self.className + ': still to fly= {0} nautics'.format(distanceStillToFlyMeters * Meter2NauticalMiles)

        endOfSimulation = turnLeg.buildTurnLeg(deltaTimeSeconds = self.deltaTimeSeconds,
                             elapsedTimeSeconds = tailWayPoint.getElapsedTimeSeconds(), 
                             distanceStillToFlyMeters = distanceStillToFlyMeters,
                             distanceToLastFixMeters = distanceToLastFixMeters)
        self.finalRoute.addGraph(turnLeg)

        if (endOfSimulation == False):
            print ' ==================== end of turn leg  ==================== '
                
            endOfTurnLegWayPoint = self.finalRoute.getLastVertex().getWeight()
            lastLeg = self.finalRoute.getLastEdge()
            print self.className + ': end of turn orientation= {0:.2f} degrees'.format(lastLeg.getBearingTailHeadDegrees())
    
            '''==================== check if anticipated turn or fly by is applicable '''
            anticipatedTurnWayPoint = None
            if (self.flightListIndex + 2) < len(self.fixList):
                ''' still another fix in the list '''
                firstAngleDegrees = endOfTurnLegWayPoint.getBearingDegreesTo(headWayPoint)
                secondAngleDegrees = headWayPoint.getBearingDegreesTo(self.wayPointsDict[self.fixList[self.flightListIndex+2]])
                firstAngleRadians = math.radians(firstAngleDegrees)
                secondAngleRadians = math.radians(secondAngleDegrees)
    
                angleDifferenceDegrees = math.degrees(math.atan2(math.sin(secondAngleRadians-firstAngleRadians), math.cos(secondAngleRadians-firstAngleRadians)))
                print self.className + ': difference= {0:.2f} degrees'.format(angleDifferenceDegrees)
    
                tasMetersPerSecond = self.aircraft.getCurrentTrueAirSpeedMetersSecond()
                radiusOfTurnMeters = (tasMetersPerSecond * tasMetersPerSecond) / (9.81 * math.tan(math.radians(15.0)))
    
                anticipatedTurnStartMeters = radiusOfTurnMeters * math.tan(math.radians((180.0 - abs(angleDifferenceDegrees))/2.0))
                print self.className + ': anticipated turn start from end point= {0:.2f} meters'.format(anticipatedTurnStartMeters)
            
                if ((endOfTurnLegWayPoint.getDistanceMetersTo(headWayPoint) > (1.1 * anticipatedTurnStartMeters) 
                    and abs(angleDifferenceDegrees) > 30.)):
                    print self.className + ': Envisage anticipated Fly By turn !!!!!!!!!!!!!!!!!!!!!!!!!'
                    bearingDegrees = math.fmod ( firstAngleDegrees + 180.0 , 360.0 )
                    anticipatedTurnWayPoint = headWayPoint.getWayPointAtDistanceBearing(
                                                                                        Name = 'Anticipated-Turn-' + headWayPoint.getName(),
                                                                                        DistanceMeters = anticipatedTurnStartMeters,
                                                                                        BearingDegrees = bearingDegrees)
                    headWayPoint = anticipatedTurnWayPoint
            
            print ' ==================== great circle ======================== '
            greatCircle = GreatCircleRoute( initialWayPoint = endOfTurnLegWayPoint,
                                            finalWayPoint = headWayPoint,
                                            aircraft = self.aircraft)
            
            distanceToLastFixMeters = self.computeDistanceToLastFixMeters(currentPosition = endOfTurnLegWayPoint,
                                                                          fixListIndex = headWayPointIndex)
            print self.className + ': distance to last fix= {0} nautics'.format(distanceToLastFixMeters * Meter2NauticalMiles)
            
            distanceStillToFlyMeters = self.flightLengthMeters - self.finalRoute.getLengthMeters()
            print self.className + ': still to fly= {0} nautics'.format(distanceStillToFlyMeters * Meter2NauticalMiles)
    
    
            endOfSimulation = greatCircle.computeGreatCircle(deltaTimeSeconds = self.deltaTimeSeconds,
                                           elapsedTimeSeconds = endOfTurnLegWayPoint.getElapsedTimeSeconds(),
                                           distanceStillToFlyMeters = distanceStillToFlyMeters,
                                           distanceToLastFixMeters = distanceToLastFixMeters)
            ''' update final route '''
            self.finalRoute.addGraph(greatCircle)
                    
            print ' ================== end of great circle ================== '
            
            finalWayPoint = self.finalRoute.getLastVertex().getWeight()
            #print self.className + ': current end way point= ' + str(finalWayPoint) 
            
            lastLeg = self.finalRoute.getLastEdge()
            finalHeadingDegrees = lastLeg.getBearingTailHeadDegrees()
            #print self.className + ': last leg orientation= {0:.2f} degrees'.format(finalHeadingDegrees)
    
            distanceStillToFlyMeters = self.flightLengthMeters - self.finalRoute.getLengthMeters()
            print self.className + ': still to fly= {0:.2f} meters - still to fly= {1:.2f} nautics'.format(distanceStillToFlyMeters, distanceStillToFlyMeters *Meter2NauticalMiles)
            ''' print the way point that has been passed right now '''
            self.printPassedWayPoint(finalWayPoint)
        ''' return to caller '''
        return endOfSimulation, finalHeadingDegrees, finalWayPoint.getElapsedTimeSeconds(), anticipatedTurnWayPoint
        
    
    def loopThroughFixList(self, 
                           initialHeadingDegrees, 
                           elapsedTimeSeconds):
        
        anticipatedTurnWayPoint = None
        ''' start loop over the fix list '''
        ''' fix list does not contain departure and arrival airports '''
        self.flightListIndex = 0
        ''' loop over the fix list '''
        endOfSimulation = False
        while (endOfSimulation == False) and (self.flightListIndex < len(self.fixList)):
            #print  self.className + ': initial heading degrees= ' + str(initialHeadingDegrees) + ' degrees'
                
            ''' get the next fix '''
            if (anticipatedTurnWayPoint is None):
                fix = self.fixList[self.flightListIndex]
                ''' tail way point to reach '''
                tailWayPoint = self.wayPointsDict[fix]
            else:
                ''' we do not use the next fix but the anticipated turn way point '''
                tailWayPoint = anticipatedTurnWayPoint
                
            tailWayPoint.setElapsedTimeSeconds(elapsedTimeSeconds)
                                
            if (self.flightListIndex + 1) < len(self.fixList):  
                ''' next way point is still in the fix list => not yet the arrival airport '''
                headWayPoint = self.wayPointsDict[self.fixList[self.flightListIndex+1]]
                  
                ''' turn and fly '''
                endOfSimulation, initialHeadingDegrees , elapsedTimeSeconds , anticipatedTurnWayPoint = self.turnAndFly(
                                                                            tailWayPoint = tailWayPoint,
                                                                            headWayPoint = headWayPoint,
                                                                            initialHeadingDegrees = initialHeadingDegrees,
                                                                            headWayPointIndex =  self.flightListIndex)
            ''' prepare for next loop '''
            self.flightListIndex += 1
            
        ''' return final heading of the last great circle '''
        return endOfSimulation, initialHeadingDegrees
    
    
    def buildDeparturePhase(self):
        ''' 
        this function manages the departure phases with a ground run and a climb ramp 
        '''
        
        print self.className + ' ============== build the departure ground run =========== ' 
        self.finalRoute = GroundRunLeg(runway = self.departureRunway, 
                                 aircraft = self.aircraft,
                                 airport = self.departureAirport)
        
        distanceToLastFixMeters = self.computeDistanceToLastFixMeters(currentPosition = self.departureAirport,
                                                                      fixListIndex = 0)
        distanceStillToFlyMeters = self.flightLengthMeters - self.finalRoute.getLengthMeters()

        elapsedTimeSeconds = 0.0
        self.finalRoute.buildDepartureGroundRun(deltaTimeSeconds  = self.deltaTimeSeconds,
                                                elapsedTimeSeconds = elapsedTimeSeconds,
                                                distanceStillToFlyMeters = distanceStillToFlyMeters,
                                                distanceToLastFixMeters = distanceToLastFixMeters)
        distanceStillToFlyMeters = self.flightLengthMeters - self.finalRoute.getLengthMeters()

        #print '==================== end of ground run ==================== '
        initialWayPoint = self.finalRoute.getLastVertex().getWeight()
        distanceToFirstFixNautics = initialWayPoint.getDistanceMetersTo(self.getFirstWayPoint()) * Meter2NauticalMiles
        #print '==================== Initial Climb Ramp ==================== '

        climbRamp = ClimbRamp(  initialWayPoint = initialWayPoint,
                                    runway = self.departureRunway, 
                                    aircraft = self.aircraft, 
                                    departureAirport = self.departureAirport)
        ''' climb ramp of 5.0 nautics is not possible is first fix in between '''
        climbRampLengthNautics = min(distanceToFirstFixNautics / 2.0 , 5.0)
        climbRamp.buildClimbRamp(deltaTimeSeconds = self.deltaTimeSeconds,
                                 elapsedTimeSeconds = initialWayPoint.getElapsedTimeSeconds(),
                                 distanceStillToFlyMeters = distanceStillToFlyMeters ,
                                 distanceToLastFixMeters = distanceToLastFixMeters,
                                 climbRampLengthNautics = climbRampLengthNautics )
        self.finalRoute.addGraph(climbRamp)
            
        #print '============= initial condition for the route =================' 
            
        initialWayPoint = self.finalRoute.getLastVertex().getWeight()
        lastLeg = self.finalRoute.getLastEdge()
        initialHeadingDegrees = lastLeg.getBearingTailHeadDegrees()
        print self.className + ': last leg orientation= {0:.2f} degrees'.format(initialHeadingDegrees)
            
        #'''============= add way point in the fix list =============== '''
        self.insert(position = 'begin', wayPoint= initialWayPoint )
        #print self.className + ': fix list= {0}'.format(self.fixList)
        
        return initialHeadingDegrees , initialWayPoint
        
        
    def buildSimulatedArrivalPhase(self):
        
        print self.className + '=========== add final turn, descent and ground run ==================='
        arrivalGroundRun = GroundRunLeg( runway   = self.arrivalRunway,
                                         aircraft = self.aircraft,
                                         airport  = self.arrivalAirport )
        self.touchDownWayPoint = arrivalGroundRun.computeTouchDownWayPoint()
        print self.touchDownWayPoint
        ''' distance from last fix to touch down '''
        distanceToLastFixNautics = self.touchDownWayPoint.getDistanceMetersTo(self.getLastWayPoint()) * Meter2NauticalMiles
        
        print self.className + '===================== final 3 degrees descending glide slope ================'
        descentGlideSlope = DescentGlideSlope( runway   = self.arrivalRunway,
                                               aircraft = self.aircraft,
                                               arrivalAirport = self.arrivalAirport,
                                               descentGlideSlopeDegrees = 3.0)
        ''' if there is a fix nearer to 5 nautics of the touch-down then limit size of simulated glide slope '''
        descentGlideSlopeSizeNautics = min(distanceToLastFixNautics / 2.0 , 5.0)
        ''' build simulated glide slope '''
        descentGlideSlope.buildSimulatedGlideSlope(descentGlideSlopeSizeNautics)
        self.firstGlideSlopeWayPoint = descentGlideSlope.getVertex(v=0).getWeight()
        print self.className + ': top of arrival glide slope= {0}'.format(self.firstGlideSlopeWayPoint)
        
        print self.className + ' ================= need a turn leg to find the junction point the last way-point in the fix list to the top of the final glide slope'
        '''
        initial heading is the orientation of the run-way
        '''
        lastFixListWayPoint = self.wayPointsDict[self.fixList[-1]]
        initialHeadingDegrees = self.arrivalRunway.getTrueHeadingDegrees()

        lastTurnLeg = TurnLeg( initialWayPoint = self.firstGlideSlopeWayPoint, 
                           finalWayPoint = lastFixListWayPoint,
                           initialHeadingDegrees = initialHeadingDegrees, 
                           aircraft = self.aircraft,
                           reverse = True)
        lastTurnLeg.buildNewSimulatedArrivalTurnLeg(deltaTimeSeconds = self.deltaTimeSeconds,
                                                 elapsedTimeSeconds = 0.0,
                                                 distanceStillToFlyMeters = 0.0,
                                                 simulatedAltitudeSeaLevelMeters = self.firstGlideSlopeWayPoint.getAltitudeMeanSeaLevelMeters(),
                                                 flightPathAngleDegrees = 3.0,
                                                 bankAngleDegrees = 5.0)
        descentGlideSlope.addGraph(lastTurnLeg)
        #print self.className + ': compute arrival phase length= {0:.2f} meters'.format(descentGlideSlope.getLengthMeters())
        #descentGlideSlope.createXlsxOutputFile()
        #descentGlideSlope.createKmlOutputFile()
        ''' prepare next step '''
        beginOfLastTurnLeg = lastTurnLeg.getVertex(v=0).getWeight()
        print self.className + ': begin of last turn= {0}'.format(beginOfLastTurnLeg)
        
        ''' add the three last way-points in the fix list '''
        self.insert(position = 'end', wayPoint = beginOfLastTurnLeg )
        ''' update the length of the flight path '''
        self.distanceFromApproachToTouchDownMeters = descentGlideSlope.getLengthMeters()
        self.flightLengthMeters = self.computeLengthMeters()  + descentGlideSlope.getLengthMeters()
        print self.className + ': updated flight path length= {0:.2f} nautics'.format(self.flightLengthMeters * Meter2NauticalMiles )
        ''' target approach fix is equal to the begin of the SIMULATED last turn leg '''
        self.aircraft.setTargetApproachWayPoint(beginOfLastTurnLeg)
        self.aircraft.setArrivalRunwayTouchDownWayPoint(self.touchDownWayPoint)
        print self.className + ': fix list= {0}'.format(self.fixList)
        

    def buildArrivalPhase(self, initialHeadingDegrees ):
        
        print self.className + '==================== add last turn ==================== '
        if self.isDomestic() or self.isInBound():
            endOfLastGreatCircleWayPoint = self.finalRoute.getLastVertex().getWeight()
                
            finalHeadingDegrees = self.arrivalRunway.getTrueHeadingDegrees()
            finalHeadingDegrees = math.fmod ( finalHeadingDegrees + 180.0 , 360.0 )
            print self.className + ': runway final heading= {0:.2f} degrees'.format(finalHeadingDegrees)
            
            turnLeg = TurnLeg(  initialWayPoint  = endOfLastGreatCircleWayPoint,
                                    #finalWayPoint    = self.firstGlideSlopeWayPoint,
                                    finalWayPoint    = self.touchDownWayPoint,
                                    initialHeadingDegrees = initialHeadingDegrees,
                                    aircraft = self.aircraft,
                                    reverse = False)
            
            distanceStillToFlyMeters = self.flightLengthMeters - self.finalRoute.getLengthMeters()
            distanceToLastFixMeters = self.computeDistanceToLastFixMeters(currentPosition = endOfLastGreatCircleWayPoint,
                                                                          fixListIndex = self.flightListIndex)
            distanceToLastFixMeters = distanceStillToFlyMeters
            ''' for the last turn => final heading towards the runway orientation '''
            deltaTimeSeconds = 0.1
            turnLeg.buildTurnLeg(deltaTimeSeconds = deltaTimeSeconds,
                                 elapsedTimeSeconds = endOfLastGreatCircleWayPoint.getElapsedTimeSeconds(),
                                 distanceStillToFlyMeters = distanceStillToFlyMeters,
                                 distanceToLastFixMeters = distanceToLastFixMeters,
                                 finalHeadingDegrees = finalHeadingDegrees,
                                 lastTurn = True,
                                 bankAngleDegrees = 5.0)
            self.finalRoute.addGraph(turnLeg)
                
            endOfTurnLegWayPoint = self.finalRoute.getLastVertex().getWeight()
            ''' ============= use touch-down way-point to compute distance to fly ============='''
            distanceStillToFlyMeters = endOfTurnLegWayPoint.getDistanceMetersTo(self.touchDownWayPoint)
            print self.className + ': distance still to fly= {0:.2f} nautics'.format(distanceStillToFlyMeters * Meter2NauticalMiles)
    
            #print '==================== add descent slope ================= '
            descentGlideSlope = DescentGlideSlope( runway   = self.arrivalRunway,
                                                        aircraft = self.aircraft,
                                                        arrivalAirport = self.arrivalAirport,
                                                        descentGlideSlopeDegrees = 3.0)
                  
            flownDistanceMeters = self.finalRoute.getLengthMeters()    
            distanceStillToFlyMeters = self.flightLengthMeters - self.finalRoute.getLengthMeters()
            distanceToLastFixMeters = self.computeDistanceToLastFixMeters(currentPosition = endOfTurnLegWayPoint,
                                                                          fixListIndex = self.flightListIndex)
            distanceToLastFixMeters = distanceStillToFlyMeters

            descentGlideSlope.buildGlideSlope(deltaTimeSeconds = self.deltaTimeSeconds,
                                              elapsedTimeSeconds = endOfTurnLegWayPoint.getElapsedTimeSeconds(), 
                                               initialWayPoint = endOfTurnLegWayPoint, 
                                               flownDistanceMeters = flownDistanceMeters, 
                                               distanceStillToFlyMeters= distanceStillToFlyMeters ,
                                               distanceToLastFixMeters = distanceToLastFixMeters)
            self.finalRoute.addGraph(descentGlideSlope)
            endOfDescentGlideSlope = self.finalRoute.getLastVertex().getWeight()
            
            #print '================= add arrival ground run ================'
            arrivalGroundRun = GroundRunLeg( runway   = self.arrivalRunway,
                                          aircraft = self.aircraft,
                                          airport  = self.arrivalAirport )
            arrivalGroundRun.buildArrivalGroundRun(deltaTimeSeconds = self.deltaTimeSeconds,
                                                   elapsedTimeSeconds = endOfDescentGlideSlope.getElapsedTimeSeconds(),
                                                    initialWayPoint = endOfDescentGlideSlope)
            self.finalRoute.addGraph(arrivalGroundRun)
        
        
      
    def computeFlight(self, deltaTimeSeconds):
        ''' 
        main entry to compute a whole flight 
        '''
        self.deltaTimeSeconds = deltaTimeSeconds
        
        assert not( self.aircraft is None)
        assert not( self.departureRunway is None)
        assert not( self.departureAirport is None)
        
        if self.isDomestic() or self.outBound():
            initialHeadingDegrees , initialWayPoint = self.buildDeparturePhase()
      
        if self.isDomestic() or self.inBound():
            assert not(self.arrivalAirport is None)
            self.buildSimulatedArrivalPhase()
        
        #print '==================== Loop over the fix list ==================== '
        
        endOfSimulation, initialHeadingDegrees = self.loopThroughFixList(initialHeadingDegrees = initialHeadingDegrees,
                                                        elapsedTimeSeconds = initialWayPoint.getElapsedTimeSeconds())
        
        if (endOfSimulation == False):
            #print '=========== build arrival phase =============='
            self.buildArrivalPhase(initialHeadingDegrees)

        print self.className + ' ========== delta mass status =============='
        print self.className + ': initial mass= {0:.2f} kilograms = {1:.2f} pounds'.format(self.aircraft.getAircraftInitialMassKilograms(),
                                                                                           self.aircraft.getAircraftInitialMassKilograms()*Kilogram2Pounds)
        print self.className + ': final mass= {0:.2f} kilograms = {1:.2f} pounds'.format(self.aircraft.getAircraftCurrentMassKilograms(),
                                                                                         self.aircraft.getAircraftCurrentMassKilograms()*Kilogram2Pounds)
        print self.className + ': diff mass= {0:.2f} kilograms = {1:.2f} pounds'.format(self.aircraft.getAircraftInitialMassKilograms()-self.aircraft.getAircraftCurrentMassKilograms(),
                                                                                        (self.aircraft.getAircraftInitialMassKilograms()-self.aircraft.getAircraftCurrentMassKilograms())*Kilogram2Pounds)
        print self.className + ' ========== delta mass status =============='

            
            
    def createFlightOutputFiles(self):
        ''' build outputs '''
        self.finalRoute.createXlsxOutputFile()
        self.finalRoute.createKmlOutputFile()
        ''' add a prefix to the file path to identify the departure and arrival airport '''
        filePrefix = ''
        if not(self.departureAirport is None):
            filePrefix = self.departureAirport.getICAOcode()
            if not(self.arrivalAirport is None):
                filePrefix += '-' + self.arrivalAirport.getICAOcode()
        self.aircraft.createStateVectorOutputFile(filePrefix)
        print self.className + ': final route length= {0} nautics'.format(self.finalRoute.getLengthMeters()*Meter2NauticalMiles)
        

