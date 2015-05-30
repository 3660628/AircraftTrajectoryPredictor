
'''
Created on 25 janvier 2015

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

@note: typical flight plan 

    strRoute = 'ADEP/LFBO-TOU-ALIVA-TOU37-FISTO-LMG-PD01-PD02-AMB-AMB01-AMB02-PD03-PD04-OLW11-OLW83-ADES/LFPO'

purpose : build a fix list from a route expressed as a sequence of names

@ TODO: it should be possible to insert in the flight plan
1) a lat-long expressed point such as N88-55-66W001-02-03
2) a condition such as before a given fix , a speed condition is reached (below 10.000 feet speed is lower to 250knots)

'''
import math
import unittest

from Home.Environment.WayPointsDatabaseFile import WayPointsDatabase
from Home.Environment.AirportDatabaseFile import AirportsDatabase

from Home.Environment.RunWaysDatabaseFile import RunWayDataBase
from Home.Guidance.WayPointFile import WayPoint

Meter2NauticalMiles = 0.000539956803 # nautical miles

class FlightPlan(object):
    
    className = ''
    strRoute = ''
    fixList = []
    wayPointsDict = {}
    departureAirportIcaoCode = ''
    departureAirport = None
    arrivalAirportIcaoCode = ''
    arrivalAirport = None
    
    def __init__(self, strRoute):
        
        self.className = self.__class__.__name__

        assert isinstance(strRoute, (str, unicode))
        self.strRoute = strRoute
        self.fixList = []
        self.wayPointsDict = {}
        self.buildFixList()
        
        
    def __str__(self):
        return self.className + ' fix list= ' + str(self.fixList)
        
        
    def getArrivalAirport(self):
        return self.arrivalAirport
    
    
    def getDepartureAirport(self):
        return self.departureAirport


    def buildFixList(self):
        '''
        from the route build a fix list and from the fix list build a way point list
        '''
        
        self.wayPointsDict = {}
        wayPointsDb = WayPointsDatabase()
        assert (wayPointsDb.read())
        
        airportsDb = AirportsDatabase()
        assert airportsDb.read()
        
        runwaysDb = RunWayDataBase()
        assert runwaysDb.read()
        
        #print self.className + ': ================ get Fix List ================='
        self.fixList = []
        index = 0
        for fix in self.strRoute.split('-'):
            fix = str(fix).strip()
            ''' first item is the Departure Airport '''
            if index == 0 and str(fix).startswith('ADEP'):
                ''' ADEP is the first fix of the route '''
                if len(str(fix).split('/')) >= 2:
                    self.departureAirportIcaoCode = str(fix).split('/')[1]
                    self.departureAirport = airportsDb.getAirportFromICAOCode(ICAOcode = self.departureAirportIcaoCode)
                    print self.className + ': departure airport= ' + str(self.departureAirport)

                self.departureRunwayName = ''
                if len(str(fix).split('/')) >= 3:
                    self.departureRunwayName = str(fix).split('/')[2]
                    
                if not(self.departureAirport is None):
                    self.departureRunway = runwaysDb.getFilteredRunWays(airportICAOcode = self.departureAirportIcaoCode, 
                                                                        runwayName = self.departureRunwayName)
                    print self.className + ': departure runway= {0}'.format(self.departureRunway)
                
            elif index == (len(self.strRoute.split('-'))-1) and str(fix).startswith('ADES'):
                ''' ADES is the last fix of the route '''
                if len(str(fix).split('/')) >= 2:
                    self.arrivalAirportIcaoCode = str(fix).split('/')[1]
                    self.arrivalAirport = airportsDb.getAirportFromICAOCode(ICAOcode = self.arrivalAirportIcaoCode)
                    print self.className + ': arrival airport= ' + str(self.arrivalAirport)
                
                self.arrivalRunwayName = ''
                if len(str(fix).split('/')) >= 3:
                    self.arrivalRunwayName = str(fix).split('/')[2]
                
                if not(self.arrivalAirport is None):
                    self.arrivalRunway =  runwaysDb.getFilteredRunWays(airportICAOcode = self.arrivalAirportIcaoCode, 
                                                                       runwayName = self.arrivalRunwayName)
                    print self.className + ': arrival runway= {0}'.format(self.arrivalRunway)

            else:
                ''' do not take the 1st one (ADEP) and the last one (ADES) '''
                self.fixList.append(fix)
                wayPoint = wayPointsDb.getWayPoint(fix)
                if not(wayPoint is None):
                    #print wayPoint
                    self.wayPointsDict[fix] = wayPoint
                else:
                    ''' do not insert way point names when there is no known latitude - longitude '''
                    self.fixList.pop()
                
            index += 1             
        #print self.className + ': fix list= ' + str(self.fixList)
        assert (self.allAnglesLessThan90degrees(minIntervalNautics = 10.0))
       
        
    def insert(self, position, wayPoint):
        ''' 
        insert a waypoint is the list and add the waypoint to the flight plan dictionnary 
        '''
        assert (isinstance(wayPoint, WayPoint))

        if position == 'begin':
            self.fixList.insert(0, wayPoint.getName())
        elif position == 'end':
            self.fixList.insert(len(self.fixList), wayPoint.getName())
        else:
            if isinstance(position, int):
                self.fixList.insert(position, wayPoint.getName())

        self.wayPointsDict[wayPoint.getName()] = wayPoint


    def getFirstWayPoint(self):
        ''' 
        if fix list is empty , need at least an arrival airport 
        '''
        if len(self.fixList) > 0:
            firstFix = self.fixList[0]
            return self.wayPointsDict[firstFix]
        else:
            ''' fix list is empty => need an arrival airport at least '''
            assert not(self.arrivalAirport is None)
            return self.arrivalAirport
      
      
    def getLastWayPoint(self):
        ''' if fix list is empty, return arrival airport '''
        if len(self.fixList) > 0:
            lastFix = self.fixList[-1]
            return self.wayPointsDict[lastFix]
        else:
            return self.arrivalAirport
        
        
    def isOverFlight(self):
        return (self.departureAirport is None) and (self.arrivalAirport is None)
    
    
    def isDomestic(self):
        return not(self.departureAirport is None) and not(self.arrivalAirport is None)
    
    
    def isInBound(self):
        return (self.departureAirport is None) and not(self.arrivalAirport is None)
        
        
    def isOutBound(self):
        return not(self.departureAirport is None) and (self.arrivalAirport is None)
    
    
    def checkAnglesGreaterTo(self, 
                             firstWayPoint, 
                             secondWayPoint, 
                             thirdWayPoint, 
                             maxAngleDifferenceDegrees = 45.0):
        
        print self.className + ': {0} - {1} - {2}'.format(firstWayPoint.getName(),
                                                        secondWayPoint.getName(), 
                                                        thirdWayPoint.getName())
        firstAngleDegrees = firstWayPoint.getBearingDegreesTo(secondWayPoint)
        secondAngleDegrees = secondWayPoint.getBearingDegreesTo(thirdWayPoint)
                
        assert (firstAngleDegrees >= 0.0) and (secondAngleDegrees >= 0.0)
        
        print self.className + ': first angle= {0:.2f} degrees and second angle= {1:.2f} degrees'.format(firstAngleDegrees, secondAngleDegrees)
        firstAngleRadians = math.radians(firstAngleDegrees)
        secondAngleRadians = math.radians(secondAngleDegrees)

        angleDifferenceDegrees = math.degrees(math.atan2(math.sin(secondAngleRadians-firstAngleRadians), math.cos(secondAngleRadians-firstAngleRadians)))
        print self.className + ': difference= {0:.2f} degrees'.format(angleDifferenceDegrees)
        
        if abs(angleDifferenceDegrees) > maxAngleDifferenceDegrees:
            print self.className + ': WARNING - angle difference=  {0:.2f} greater to {1:.2f} degrees'.format(angleDifferenceDegrees, maxAngleDifferenceDegrees)
            return False
        
        firstIntervalDistanceNm = firstWayPoint.getDistanceMetersTo(secondWayPoint) * Meter2NauticalMiles
        secondIntervalDistanceNm = secondWayPoint.getDistanceMetersTo(thirdWayPoint) * Meter2NauticalMiles
        if (firstIntervalDistanceNm < 20.0):
            print self.className + ': WARNING - distance between {0} and {1} less than 20 Nm = {2:.2f}'.format(firstWayPoint.getName(), secondWayPoint.getName(), firstIntervalDistanceNm)
        if (secondIntervalDistanceNm < 20.0):
            print self.className + ': WARNING - distance between {0} and {1} less than 20 Nm = {2:.2f}'.format(secondWayPoint.getName(), thirdWayPoint.getName(), secondIntervalDistanceNm)

        return True


    def isDistanceLessThan(self, 
                           firstIndex, 
                           secondIndex, 
                           minIntervalNautics = 10.0):
        '''
        check distance between two index in the fix list 
        '''
        assert (len(self.fixList) > 0) 
        assert  (firstIndex >= 0) and (firstIndex < len(self.fixList))
        assert  (secondIndex >= 0) and (secondIndex < len(self.fixList))
        assert (firstIndex != secondIndex)
        
        firstWayPoint = self.wayPointsDict[self.fixList[firstIndex]]
        secondWayPoint = self.wayPointsDict[self.fixList[secondIndex]]
        IntervalDistanceNm = firstWayPoint.getDistanceMetersTo(secondWayPoint) * Meter2NauticalMiles
        if IntervalDistanceNm < minIntervalNautics:
            print self.className + ': WARNING - distance between {0} and {1} less than 10 Nm = {2:.2f}'.format(firstWayPoint.getName(), secondWayPoint.getName(), IntervalDistanceNm)
            return False
        return True


    def allAnglesLessThan90degrees(self, minIntervalNautics = 10.0):
        ''' returns True if all contiguous angles lower to 90 degrees '''
        ''' suppress point not compliant with the distance interval rules '''
        
        ''' Note: need 3 way-points to build 2 contiguous angles '''
        oneFixSuppressed = True
        while oneFixSuppressed:
            index = 0
            oneFixSuppressed = False
            for fix in self.fixList:
                print self.className + ': fix= {0}'.format(fix)
                
                if index == 1 and not(self.departureAirport is None):
                    firstWayPoint = self.departureAirport
                    secondWayPoint = self.wayPointsDict[self.fixList[index-1]]
                    thirdWayPoint = self.wayPointsDict[self.fixList[index]]
                    if (self.isDistanceLessThan(firstIndex = index-1, 
                                             secondIndex = index, 
                                             minIntervalNautics = minIntervalNautics) == False):
                        ''' suppress the point from the fix list '''
                        print self.className + ': fix suppressed= {0}'.format(self.fixList[index])
                        self.fixList.pop(index)
                        oneFixSuppressed = True
                        
                    if oneFixSuppressed:
                        print self.className + ': start the whole loop again from the very beginning '
                        break
                    else:
                        self.checkAnglesGreaterTo(firstWayPoint, 
                                              secondWayPoint, 
                                              thirdWayPoint,
                                              maxAngleDifferenceDegrees = 30.0)
    
                if index >= 2:
                    
                    firstWayPoint = self.wayPointsDict[self.fixList[index-2]]
                    secondWayPoint = self.wayPointsDict[self.fixList[index-1]]
                    if (self.isDistanceLessThan(firstIndex = index - 2, 
                                             secondIndex = index - 1, 
                                             minIntervalNautics = minIntervalNautics) == False):
                        ''' suppress the point from the fix list '''
                        print self.className + ': fix suppressed= {0}'.format(self.fixList[index-1])
                        self.fixList.pop(index-1)
                        oneFixSuppressed = True
                        
                    thirdWayPoint = self.wayPointsDict[self.fixList[index]]
                    if (self.isDistanceLessThan(firstIndex = index - 1, 
                                             secondIndex = index, 
                                             minIntervalNautics = minIntervalNautics) == False):
                        ''' suppress the point from the fix list '''
                        print self.className + ': fix suppressed= {0}'.format(self.fixList[index])
                        self.fixList.pop(index)
                        oneFixSuppressed = True
                    
                    if oneFixSuppressed:
                        print self.className + ': start the whole loop again from the very beginning '
                        break
                    else:
                        self.checkAnglesGreaterTo(firstWayPoint, 
                                              secondWayPoint, 
                                              thirdWayPoint,
                                              maxAngleDifferenceDegrees = 30.0)
    
                print self.className + '============ index = {0} ==========='.format(index)
                index += 1
        return True
    
    
    def computeLengthNauticalMiles(self):
        return self.computeLengthMeters() * Meter2NauticalMiles
    
    
    def computeLengthMeters(self):
        '''
        returns a float corresponding to the length of the route in Meters 
        if there is a arrival airport , distance from last fix to arrival airport is added
        '''
        lengthMeters = 0.0
        index = 0
        for fix in self.fixList:
            #print fix
            if not(self.departureAirport is None): 
                if index == 0:
                    lengthMeters += self.departureAirport.getDistanceMetersTo(self.wayPointsDict[fix])
                    previousWayPoint = self.wayPointsDict[fix]

                else:
                    lengthMeters += previousWayPoint.getDistanceMetersTo(self.wayPointsDict[fix])
                    previousWayPoint = self.wayPointsDict[fix]

            else:
                ''' no departure airport '''
                if index == 0:
                    previousWayPoint = self.wayPointsDict[fix]
                else:
                    lengthMeters += previousWayPoint.getDistanceMetersTo(self.wayPointsDict[fix]) 
                    previousWayPoint = self.wayPointsDict[fix]

            index += 1
        ''' add distance from last fix to arrival airport if applicable '''
        if not(self.arrivalAirport is None):
            #print self.className + ': last fix= ' + self.fixList[-1]
            if len(self.wayPointsDict) > 0:
                lengthMeters += self.wayPointsDict[self.fixList[-1]].getDistanceMetersTo(self.arrivalAirport)
            else:
                if (not(self.departureAirport is None)):
                    lengthMeters += self.departureAirport.getDistanceMetersTo(self.arrivalAirport)
            
        return lengthMeters 
    
    def computeDistanceToLastFixMeters(self, currentPosition, fixListIndex):
        '''
        compute length to fly from the provided index in the fix list
        '''
        lengthMeters = 0.0
        if fixListIndex == len(self.fixList):
            return 0.0

        assert (len(self.fixList) > 0) 
        assert (fixListIndex >= 0) 
        assert (fixListIndex < len(self.fixList))
        assert (len(self.wayPointsDict) > 0)
        if len(self.fixList) == 1:
            return 0.0

        for index in range(fixListIndex, len(self.fixList)):
            #print index
            if index == fixListIndex:
                firstWayPoint = currentPosition
            else:
                firstWayPoint = self.wayPointsDict[self.fixList[index]]
            #print firstWayPoint
            if index + 1 < len(self.fixList):
                secondWayPoint = self.wayPointsDict[self.fixList[index+1]]
                #print secondWayPoint
                lengthMeters += firstWayPoint.getDistanceMetersTo(secondWayPoint)
                #print self.className + ': first wayPoint= {0} - second wayPoint= {1}'.format(firstWayPoint, secondWayPoint)
        
        ''' do not count distance from last fix to arrival airport '''
#         if not(self.arrivalAirport is None):
#             lengthMeters += self.wayPointsDict[self.fixList[-1]].getDistanceMetersTo(self.arrivalAirport)

        return lengthMeters
    
    
class Test_Flight_Plan(unittest.TestCase):

    def test_main(self):


        
        print "=========== Flight Plan start  =========== " 
        
        strRoute = 'ADEP/LFBO-TOU-ALIVA-TOU37-FISTO-LMG-PD01-PD02-AMB-AMB01-AMB02-PD03-PD04-OLW11-OLW83-ADES/LFPO'
        flightPlan = FlightPlan(strRoute)
    
        print 'is over flight= {0}'.format(flightPlan.isOverFlight())
        print 'is domestic= ' + str(flightPlan.isDomestic())
        print 'is in Bound= ' + str(flightPlan.isInBound())
        print 'is out Bound= ' + str(flightPlan.isOutBound())
        print 'all angles > 90.0 degrees= ' + str(flightPlan.allAnglesLessThan90degrees())
        print 'flight path length= ' + str(flightPlan.computeLengthNauticalMiles()) + ' nautical miles'
    
        print "=========== Flight Plan start  =========== " 
    
    #     fixListIndex = 0
    #     print 'length from index={0} - length= {1} meters'.format(fixListIndex, 
    #                                                               flightPlan.computeDistanceToLastFixMeters(fixListIndex = 0))
    #     print "=========== Flight Plan start  =========== " 
    # 
    #     fixListIndex = 1
    #     print 'length from index={0} - length= {1} meters'.format(fixListIndex, 
    #                                                               flightPlan.computeStillToFlyMeters(fixListIndex = 0))
    #     
        print flightPlan.getDepartureAirport()
        print flightPlan.getArrivalAirport()
    
        print "=========== Flight Plan start  =========== " 
        
        strRoute = 'TOU-ALIVA-TOU37-FISTO-LMG-PD01-PD02-AMB-AMB01-AMB02-PD03-PD04-OLW11-OLW83-ADES/LFPO'
        flightPlan = FlightPlan(strRoute)
    
        print 'is over flight= ' + str(flightPlan.isOverFlight())
        print 'is domestic= ' + str(flightPlan.isDomestic())
        print 'is in Bound= ' + str(flightPlan.isInBound())
        print 'is out Bound= ' + str(flightPlan.isOutBound())
        print 'all angles > 90.0 degrees= ' + str(flightPlan.allAnglesLessThan90degrees())
        print 'flight path length= ' + str(flightPlan.computeLengthNauticalMiles()) + ' nautical miles'
    
    
        print "=========== Flight Plan start  =========== " 
        
        strRoute = 'ADEP/LFBO-TOU-ALIVA-TOU37-FISTO-LMG-PD01-PD02-AMB-AMB01-AMB02-PD03-PD04-OLW11-OLW83'
        flightPlan = FlightPlan(strRoute)
    
        print 'is over flight= ' + str(flightPlan.isOverFlight())
        print 'is domestic= ' + str(flightPlan.isDomestic())
        print 'is in Bound= ' + str(flightPlan.isInBound())
        print 'is out Bound= ' + str(flightPlan.isOutBound())
        print 'all angles > 90.0 degrees= ' + str(flightPlan.allAnglesLessThan90degrees())
        print 'flight path length= ' + str(flightPlan.computeLengthNauticalMiles()) + ' nautical miles'
    
    
        print "=========== Flight Plan start  =========== " 
        
        strRoute = 'TOU-ALIVA-TOU37-FISTO-LMG-PD01-PD02-AMB-AMB01-AMB02-PD03-PD04-OLW11-OLW83'
        flightPlan = FlightPlan(strRoute)
    
        print 'is over flight= ' + str(flightPlan.isOverFlight())
        print 'is domestic= ' + str(flightPlan.isDomestic())
        print 'is in Bound= ' + str(flightPlan.isInBound())
        print 'is out Bound= ' + str(flightPlan.isOutBound())
        print 'flight path length= ' + str(flightPlan.computeLengthNauticalMiles()) + ' nautical miles'
        
        strRoute = 'ADEP/SBGL-ALDEIA-NIKDO-MACAE-GIKPO-MABSI-VITORIA-GIDOD-'
        strRoute += 'ISILA-POSGA-SEGURO-BIDEV-NAXOV-IRUMI-ESLIB-MEDIT-RUBEN-KIBEG-'
        strRoute += 'AMBET-VUKSU-NORONHA-UTRAM-MEDAL-NAMBI-RAKUD-IRAVU-MOGNI-ONOBI-CABRAL-'
        strRoute += 'IPERA-ISOKA-LIMAL-UDATI-ODEGI-LOMAS-CANARIA-VASTO-SULAM-DIMSA-ATLUX-'
        strRoute += 'SUNID-AKUDA-OBOLO-PESAS-EKRIS-LUSEM-LULUT-BORDEAUX-COGNAC-ADABI-BOKNO-'
        strRoute += 'DEVRO-VANAD-KOVAK-ADES/LFPG'
    
        print "=========== Flight Plan start  =========== " 
    
        flightPlan = FlightPlan(strRoute)
    
        print 'is over flight= ' + str(flightPlan.isOverFlight())
        print 'is domestic= ' + str(flightPlan.isDomestic())
        print 'is in Bound= ' + str(flightPlan.isInBound())
        print 'is out Bound= ' + str(flightPlan.isOutBound())
        print 'flight path length= ' + str(flightPlan.computeLengthNauticalMiles()) + ' nautical miles'
        
        print "=========== Flight Plan start  =========== " 
        strRoute = 'ADEP/SBGL-ALDEIA-NIKDO-MACAE'
        flightPlan = FlightPlan(strRoute)
    
        print "=========== Flight Plan start  =========== " 
    
        strRoute = 'ADEP/LFBM/27-'
        strRoute += 'SAU-VELIN-LMG-BEBIX-GUERE-LARON-KUKOR-MOU-'
        strRoute += 'PIBAT-DJL-RESPO-DANAR-POGOL-OBORN-LUPEN-SUL-'
        strRoute += 'ESULI-TEDGO-ETAGO-IBAGA-RATIP-PIBAD-SOMKO-'
        strRoute += 'ADES/EDDP/26R'
        flightPlan = FlightPlan(strRoute)
        
        print 'flight path length= ' + str(flightPlan.computeLengthNauticalMiles()) + ' nautical miles'
    
if __name__ == '__main__':
    unittest.main()
