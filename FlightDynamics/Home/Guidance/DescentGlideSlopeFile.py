'''
Created on November 24, 2014

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

start in aircraft approach configuration and end when aircraft speed reaches landing speed

'''
import time
import math
import unittest

from Home.Environment.RunWaysDatabaseFile import RunWayDataBase, RunWay
from Home.Environment.AirportDatabaseFile import AirportsDatabase

from Home.Environment.Atmosphere import Atmosphere
from Home.Environment.Earth import Earth

from Home.Guidance.GraphFile import Graph

from Home.Guidance.WayPointFile import WayPoint, Airport
from Home.BadaAircraftPerformance.BadaAircraftDatabaseFile import BadaAircraftDatabase
from Home.BadaAircraftPerformance.BadaAircraftFile import BadaAircraft


NauticalMiles2Meters = 1852. # meters
Meter2NauticalMiles = 0.000539956803

NumberOfSlopeParts = 100 # dimension less number (number of elementary legs in the slope)

class DescentGlideSlope(Graph):
    '''
    the glide slope starts 5 Nautical miles ahead of the touch-down point
    '''
    className = ''
    descentGlideSlopeDegrees = 0.0
    runWayTouchDownPoint= None
    runWayEndPoint = None
    runway = None
    aircraft = None
    arrivalAirport = None

    def __init__(self, 
                 runway, 
                 aircraft, 
                 arrivalAirport , 
                 descentGlideSlopeDegrees = 3.0):
        '''
        arrival Airport provides the field elevation above sea level in meters
        '''
        self.className = self.__class__.__name__
        Graph.__init__(self)
        
        assert isinstance(descentGlideSlopeDegrees, float)
        self.descentGlideSlopeDegrees = descentGlideSlopeDegrees
        
        # sanity check 
        assert isinstance(arrivalAirport, Airport)
        self.arrivalAirport = arrivalAirport

        ''' sanity check RunWay '''
        assert isinstance(runway, RunWay)
        self.runway = runway
            
        assert isinstance(aircraft, BadaAircraft)
        self.aircraft = aircraft
        
        fieldElevationAboveSeaLevelMeters = arrivalAirport.getFieldElevationAboveSeaLevelMeters()
        print self.className + ': airport field Elevation Above Sea Level= {0:.2f} meters'.format(fieldElevationAboveSeaLevelMeters)

        strName = arrivalAirport.getName() + '-' + 'RunWay'+'-'+self.runway.getName()
        self.runWayEndPoint = WayPoint (Name=strName, 
                                            LatitudeDegrees=runway.getLatitudeDegrees(),
                                            LongitudeDegrees=runway.getLongitudeDegrees(),
                                            AltitudeMeanSeaLevelMeters=fieldElevationAboveSeaLevelMeters)
 
        ''' touch down is provided from BADA Ground Movement Landing Length '''
        landingDistanceMeters = self.aircraft.groundMovement.getLandingLengthMeters()
        #print self.className + ': {0} aircraft landing length: {1:.2F} meters'.format(self.aircraft.ICAOcode, landingDistanceMeters)
        runWayOrientationDegrees = self.runway.getTrueHeadingDegrees()
        ''' if orientation is 270 degrees from runway end point then ... touch down bearing is 360-270=90 bearing from end point '''
        self.runWayTouchDownPoint = self.runWayEndPoint.getWayPointAtDistanceBearing(Name='runway-touch-down',
                                                                          DistanceMeters=landingDistanceMeters,
                                                                          BearingDegrees=runWayOrientationDegrees )
        
        ''' elevation of touch down point = field elevation'''
        self.runWayTouchDownPoint.setAltitudeMeanSeaLevelMeters(fieldElevationAboveSeaLevelMeters)
        strMsg = self.className + ": distance from RunWay - TouchDown to RunWay - End= "
        strMsg += str(self.runWayTouchDownPoint.getDistanceMetersTo(self.runWayEndPoint)) + " meters"
        print strMsg
        
        self.bearingDegrees = self.runWayTouchDownPoint.getBearingDegreesTo(self.runWayEndPoint)
        print self.className + ": bearing from touch-down to runway end= {0:.2f} degrees".format(self.bearingDegrees)
                
        
    def buildGlideSlope(self,
                        deltaTimeSeconds,
                        elapsedTimeSeconds, 
                        initialWayPoint, 
                        flownDistanceMeters, 
                        distanceStillToFlyMeters,
                        distanceToLastFixMeters):
        
        ''' sanity checks '''
        assert isinstance(initialWayPoint, WayPoint)
        '''====================================================='''
        ''' hopefully in approach or landing configuration dh/dt such as dh/ds between 3 and 5 degrees '''
        '''====================================================='''
        ''' descent stops when altitude Mean Sea Level meters <= airport field MSL meters '''
        fieldElevationAboveSeaLevelMeters = self.arrivalAirport.getFieldElevationAboveSeaLevelMeters()

        ''' initial conditions '''
        index = 0
        aircraftAltitudeMeanSeaLevelMeters = self.aircraft.getCurrentAltitudeSeaLevelMeters()
        endOfSimulation = False
        newIntermediatePoint = None
        
        while ( (endOfSimulation == False) and
               (aircraftAltitudeMeanSeaLevelMeters >= fieldElevationAboveSeaLevelMeters) and 
               not( self.aircraft.isArrivalGroundRun()) ):
            ''' initial way point '''
            if index == 0:
                intermediateWayPoint = initialWayPoint
            
            ''' correct bearing to each touch down '''
            self.bearingDegrees = intermediateWayPoint.getBearingDegreesTo(self.runWayTouchDownPoint)
            #print self.className + ': bearing to touch down= {0:.2f} degrees'.format(self.bearingDegrees)
            
            ''' aircraft fly '''
            endOfSimulation, deltaDistanceMeters , aircraftAltitudeMeanSeaLevelMeters = self.aircraft.fly(
                                                                    elapsedTimeSeconds = elapsedTimeSeconds,
                                                                    deltaTimeSeconds = deltaTimeSeconds , 
                                                                    distanceStillToFlyMeters = distanceStillToFlyMeters,
                                                                    currentPosition =  intermediateWayPoint,
                                                                    distanceToLastFixMeters = distanceToLastFixMeters)
            flownDistanceMeters += deltaDistanceMeters
            distanceStillToFlyMeters -= deltaDistanceMeters
            distanceToLastFixMeters -= deltaDistanceMeters
            ''' update aircraft state vector '''
            elapsedTimeSeconds += deltaTimeSeconds
            
            Name = ''
            ''' only the first and the last point has a name '''
            if index == 0:
                Name = 'slope-pt-{0}-{1:.2f}-Nm'.format(index, flownDistanceMeters*Meter2NauticalMiles)
            newIntermediatePoint = intermediateWayPoint.getWayPointAtDistanceBearing( Name = Name, 
                                                                                  DistanceMeters = deltaDistanceMeters, 
                                                                                  BearingDegrees = self.bearingDegrees)
            ''' set altitude '''
            if isinstance(newIntermediatePoint, WayPoint):
                newIntermediatePoint.setAltitudeMeanSeaLevelMeters(aircraftAltitudeMeanSeaLevelMeters)
                newIntermediatePoint.setElapsedTimeSeconds(elapsedTimeSeconds)     
                
            ''' append the new point to the list '''
            self.addVertex(newIntermediatePoint)
            ''' replace the intermediate point '''
            intermediateWayPoint = newIntermediatePoint
            index += 1
        ''' set the name of the last point '''
        Name = 'slope-pt-{0}-{1:.2f}-Nm'.format(index, flownDistanceMeters*Meter2NauticalMiles)
        if not(newIntermediatePoint is None):
            newIntermediatePoint.setName(Name = Name)
  

        
    def buildSimulatedGlideSlope(self, descentGlideSlopeSizeNautics):
        '''====================================================='''
        ''' build the three degrees glide slope '''
        ''' the slope is built backwards and then it is reversed
        ''======================================================'''
        #print self.className + ' ======= simulated glide slope ========='
        glideSlopeLengthMeters = descentGlideSlopeSizeNautics * NauticalMiles2Meters
        print self.className + ': glide slope Length= ' + str(glideSlopeLengthMeters),  ' meters'

        bearingDegrees = self.runway.getTrueHeadingDegrees()
        print self.className + ': glide slope orientation= ' + str(bearingDegrees) + ' degrees'

        fieldElevationAboveSeaLevelMeters = self.arrivalAirport.getFieldElevationAboveSeaLevelMeters()

        ''' internal list that will be reversed '''
        intermediateGlideSlopeRoute = []
        
        '''=============================='''
        index = 0
        initialIndex = index
        elapsedTimeSeconds = 0.0
        '''=================================================================='''
        ''' glide slope to intercept the landing ILS beam '''
        '''=================================================================='''
        ''' glide slope is split into 100 parts '''
        distanceMeters = 0.0
        while (distanceMeters < glideSlopeLengthMeters) :
            
            distanceMeters += glideSlopeLengthMeters/NumberOfSlopeParts
            #print 'index= ', index
            if index == initialIndex:
                ''' first point is the run way touch down '''
                intermediatePoint = self.runWayTouchDownPoint
                #intermediatePoint.dump()
            ''' glide slope angle needs to be positive here : because slope is built backwards from run-way threshold '''
            altitudeMeters = math.tan(math.radians(abs(self.descentGlideSlopeDegrees))) * distanceMeters
            name = 'glide-slope-pt-{0}-{1}-meters'.format(index, distanceMeters)
            ''' distance between each slope point is slope length divided by number of parts '''
            newIntermediatePoint = intermediatePoint.getWayPointAtDistanceBearing(Name=name, 
                                                                                  DistanceMeters=glideSlopeLengthMeters/NumberOfSlopeParts, 
                                                                                  BearingDegrees=bearingDegrees)
            ''' set altitude '''
            if isinstance(newIntermediatePoint, WayPoint):
                ''' need to add altitude above ground to field elevation '''
                altitudeMeters += fieldElevationAboveSeaLevelMeters
                newIntermediatePoint.setAltitudeMeanSeaLevelMeters(altitudeMeters)
                elapsedTimeSeconds += 0.1
                newIntermediatePoint.setElapsedTimeSeconds(elapsedTimeSeconds = elapsedTimeSeconds)

                
            ''' append the new point to the list '''
            intermediateGlideSlopeRoute.append(newIntermediatePoint)
            ''' replace the intermediate point '''
            intermediatePoint = newIntermediatePoint
            index += 1
        
        '''============================================================='''
        ''' reverse the order of the temporary list and build the graph '''
        '''============================================================='''
        for point in reversed(intermediateGlideSlopeRoute):
            self.addVertex(point)
        simulatedGlideSlopeLengthMeters = newIntermediatePoint.getDistanceMetersTo(self.runWayTouchDownPoint)
        print self.className + ': distance from last way point to touch-down: {0:.2f} nautics'.format(simulatedGlideSlopeLengthMeters * Meter2NauticalMiles)



#============================================
class Test_DescentGlideSlope(unittest.TestCase):

    def test_DescentGlideSlope(self):
    
        atmosphere = Atmosphere()
        earth = Earth()
        print '==================== three degrees Descent Slope Start  ==================== '+ time.strftime("%c")
    
        acBd = BadaAircraftDatabase()
        aircraftICAOcode = 'A320'
        if acBd.read():
            if ( acBd.aircraftExists(aircraftICAOcode) 
                 and acBd.aircraftPerformanceFileExists(aircraftICAOcode)):
                
                print '==================== aircraft found  ==================== '+ time.strftime("%c")
    
                aircraft = BadaAircraft(ICAOcode = aircraftICAOcode, 
                                        aircraftFullName = acBd.getAircraftFullName(aircraftICAOcode),
                                        badaPerformanceFilePath = acBd.getAircraftPerformanceFile(aircraftICAOcode),
                                        atmosphere = atmosphere,
                                        earth = earth)
                aircraft.dump()
     
        assert not (aircraft is None)
        print '==================== runways database ==================== '+ time.strftime("%c")
        runWaysDatabase = RunWayDataBase()
        assert runWaysDatabase.read()
        
        runway = runWaysDatabase.getFilteredRunWays(airportICAOcode = 'LFML', runwayName = '')
        print runway
      
        print "=========== arrival airport  =========== " + time.strftime("%c")
        airportsDB = AirportsDatabase()
        assert (airportsDB.read())
        
        MarseilleMarignane = airportsDB.getAirportFromICAOCode('LFML')
        print MarseilleMarignane
        
        print "=========== descent glide slope  =========== " + time.strftime("%c")
        threeDegreesGlideSlope = DescentGlideSlope(runway = runway, 
                                                   aircraft = aircraft, 
                                                   arrivalAirport = MarseilleMarignane )
        
        initialWayPoint = WayPoint(Name = 'startOfDescentGlideSlope',
                                   )
        print "=========== DescentGlideSlope build the glide slope  =========== " + time.strftime("%c")
    #     threeDegreesGlideSlope.buildGlideSlope(deltaTimeSeconds = 0.1,
    #                         elapsedTimeSeconds = 0.0, 
    #                         initialWayPoint = None, 
    #                         flownDistanceMeters = 0.0, 
    #                         distanceStillToFlyMeters = 100000.0,
    #                         distanceToLastFixMeters = 100000.0)
    
        threeDegreesGlideSlope.buildSimulatedGlideSlope(descentGlideSlopeSizeNautics = 5.0)
        
        print "=========== DescentGlideSlope  =========== " + time.strftime("%c")
        for node in threeDegreesGlideSlope.getVertices():
            print node
        
        print "=========== DescentGlideSlope length =========== " + time.strftime("%c")
        print "get number of vertices= {0}".format( threeDegreesGlideSlope.getNumberOfVertices() )
        print "get number of edges= {0}".format ( threeDegreesGlideSlope.getNumberOfEdges() )
        print 'Glide Slope overall length= {0} meters'.format( threeDegreesGlideSlope.computeLengthMeters() )
        
        threeDegreesGlideSlope.createKmlOutputFile()
        threeDegreesGlideSlope.createXlsxOutputFile()
        print '==================== three degrees Descent Slope End  ==================== '+ time.strftime("%c")


if __name__ == '__main__':
    unittest.main()