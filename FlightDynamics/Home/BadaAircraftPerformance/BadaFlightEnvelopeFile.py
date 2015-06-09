'''
Created on 26 mars 2015

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
        
'''
import unittest

from Home.BadaAircraftPerformance.BadaAircraftPerformanceFile import AircraftPerformance
from Home.BadaAircraftPerformance.BadaAeroDynamicsFile import AeroDynamics
from Home.BadaAircraftPerformance.BadaAircraftStateVectorFile import StateVector
from Home.BadaAircraftPerformance.BadaAircraftDatabaseFile import BadaAircraftDatabase

from Home.Environment.Atmosphere import Atmosphere
from Home.Environment.Earth import Earth

Meter2Feet = 3.2808
Feet2Meter = 0.3048
MeterSecond2Knots = 1.9438444924406


class FlightEnvelope(AeroDynamics):
    '''
    design issue = TAS + altitude (and ISA temperature) => compute CAS
    
    Definition

    Calibrated airspeed (CAS) is indicated airspeed corrected for instrument errors and position error 
    (due to incorrect pressure at the static port caused by airflow disruption).

    Description
    
    CAS has two primary applications in aviation:

    for navigation, CAS is traditionally calculated as one of the steps between indicated airspeed (IAS) and true airspeed (TAS);
    for aircraft control, CAS is one of the primary reference points, as it describes the dynamic pressure acting on aircraft surfaces 
    regardless of the existing conditions of temperature, pressure altitude or wind.

    The first application has rapidly decreased in importance due to the widespread use of GPS and inertial navigation systems. 
    With these systems, pilots are able to read TAS and ground-speed directly from cockpit displays. 
    This negates the requirement to calculate TAS from IAS with calibrated airspeed as an intermediate step.
    
    The second application, however, remains critical. 
    As an example, at a given weight, an aircraft will rotate and climb, stall or fly an approach to a landing at approximately the same calibrated airspeeds, 
    regardless of the elevation, even though the true airspeed and ground speed may differ significantly. 
    These V (vertical) speeds are normally published as IAS rather than CAS so they can be read directly from the airspeed indicator. 
    
    '''
    # VMO - maximum operating speed (CAS), in knots
    MaxOpSpeedCasKnots = 0.0
    # MMO - maximum operational Mach number
    MaxOpMachNumber = 0.0
    # hMO - maximum operating altitude, in feet, above standard MSL
    MaxOpAltitudeFeet = 0.0
    ''' 
    hmax - maximum altitude, in feet, above standard MSL at Max Take-Off Weight under ISA
    conditions (allowing about 300 fpm of residual Rate Of Climb), 
    '''
    MaxAltitudeMslFeet = 0.0
    # Gw - mass gradient on hmax , in feet/kg
    # Gt - temperature gradient on hmax in feet/degree Celsius
    ''' speed history - check that speed stays within the flight envelope '''
    StateVector = None

    def __init__(self, aircraftPerformance, ICAOcode, atmosphere, earth):

        self.className = self.__class__.__name__
        
        ''' init mother class '''
        AeroDynamics.__init__(self, aircraftPerformance, atmosphere, earth)

        assert isinstance(atmosphere, Atmosphere)
        self.atmosphere = atmosphere
        
        assert isinstance(aircraftPerformance, AircraftPerformance)
        self.MaxOpSpeedCasKnots = aircraftPerformance.getVmoCasKnots()
        self.MaxOpMachNumber = aircraftPerformance.getMaxOpMachNumber()
        self.MaxOpAltitudeFeet = aircraftPerformance.getMaxOpAltitudeFeet()
                
        self.targetCruiseAltitudeMslMeters = self.MaxOpAltitudeFeet / Meter2Feet        
        self.targetCruiseMachNumber = self.MaxOpMachNumber
        self.arrivalAirportFieldElevationMeters = 0.0
        
        self.StateVector = StateVector(ICAOcode, atmosphere)
        self.departureAirportAltitudeMSLmeters = 0.0
        
        self.approachWayPoint = None
        self.arrivalRunWayTouchDownWayPoint = None

    def setTargetCruiseFlightLevel(self, 
                                   RequestedFlightLevel, 
                                   departureAirportAltitudeMSLmeters):
        
        self.departureAirportAltitudeMSLmeters = departureAirportAltitudeMSLmeters
        QNHhectoPascals =  1013.25  - (departureAirportAltitudeMSLmeters / 8.5344)
        ''' flight level is expressed in hundreds of feet '''
        assert RequestedFlightLevel >= 15.0 and RequestedFlightLevel <= 450.0
        self.targetCruiseFlightLevel = RequestedFlightLevel
        ''' pression de reference  MSL =  1013,25    hecto Pascals '''
        ''' delta meter for each hecto pascal = 8,5344 meter '''
        ''' compute Mean Sea Level altitude expressed in meters '''
        self.targetCruiseAltitudeMslMeters = ( RequestedFlightLevel * 100.0 * Feet2Meter ) + (1013.25 - QNHhectoPascals) * 8.5344
        self.targetCruiseAltitudeMslMeters = ( RequestedFlightLevel * 100.0 * Feet2Meter )
        print self.className + ': set Cruise FL= {0} - QNH= {1:.2f} hecto Pascals - computed Altitude MSL=  {2:.2f} meters'.format(RequestedFlightLevel , QNHhectoPascals, self.targetCruiseAltitudeMslMeters)


    def getTargetCruiseFlightLevelMeters(self):
        return self.targetCruiseAltitudeMslMeters
    
    
    def setTargetApproachWayPoint(self, approachWayPoint):
        self.approachWayPoint = approachWayPoint
        
        
    def getTargetApproachWayPoint(self):
        return self.approachWayPoint
    
    
    def getMaxOperationalMach(self):
        return self.MaxOpMachNumber
        
        
    def setTargetCruiseMach(self, cruiseMachNumber):
        ''' check that target mach is always lower or equal to Max Operational Mach '''
        if isinstance(cruiseMachNumber, str) and (cruiseMachNumber == 'use-default'):
            cruiseMachNumber = self.MaxOpMachNumber

        assert (cruiseMachNumber <= self.MaxOpMachNumber)
        print self.className + ' ===================================================='
        print self.className + ': set target cruise Mach= {0}'.format(cruiseMachNumber)
        self.targetCruiseMachNumber = cruiseMachNumber
        print self.className + ' ===================================================='


    def getTargetCruiseMach(self):
        return self.targetCruiseMachNumber
    
    
    def setArrivalRunwayTouchDownWayPoint(self, arrivalRunWayTouchDownWayPoint):
        ''' target runway touch down way point '''
        self.arrivalRunWayTouchDownWayPoint = arrivalRunWayTouchDownWayPoint


    def getArrivalRunwayTouchDownWayPoint(self):
        return self.arrivalRunWayTouchDownWayPoint
        

    def dump(self):
        print self.className + ': VMO CAS= ' + str(self.MaxOpSpeedCasKnots) + ' knots'
        print self.className + ': Max Operational Mach Number= ' + str(self.MaxOpMachNumber)
        print self.className + ': Max Operational Altitude= ' + str(self.MaxOpAltitudeFeet) + ' feet'
        
    def __str__(self):
        strMsg = self.className + ': VMO CAS= {0} knots'.format(self.MaxOpSpeedCasKnots)
        strMsg += ' - Max Operational Mach Number= {0}'.format(self.MaxOpMachNumber)
        strMsg += ' - Max Operational Altitude= {0} feet'.format(self.MaxOpAltitudeFeet)
        return strMsg
        
    def getMaxAltitudeMslMtowFeet(self):
        return self.MaxOpAltitudeFeet
    
    
    def getMaxOpSpeedCasKnots(self):
        return self.MaxOpSpeedCasKnots
    

    def initStateVector(self, 
                        elapsedTimeSeconds,
                        trueAirSpeedMetersSecond,
                        airportFieldElevationAboveSeaLevelMeters,
                        aircraftMassKilograms):
        ''' 
        altitude and speed changes are modifying the configuration of the aircraft 
        '''
        lastAltitudeMeanSeaLevelMeters = self.StateVector.getCurrentAltitudeSeaLevelMeters()
        targetCruiseAltitudeMeanSeaLevelMeters = self.getTargetCruiseFlightLevelMeters()
#         self.setCurrentAltitudeSeaLevelMeters(elapsedTimeSeconds, 
#                                                 airportFieldElevationAboveSeaLevelMeters,
#                                                 lastAltitudeMeanSeaLevelMeters,
#                                                 targetCruiseAltitudeMeanSeaLevelMeters)
        self.StateVector.initStateVector(elapsedTimeSeconds, 
                                            trueAirSpeedMetersSecond, 
                                            airportFieldElevationAboveSeaLevelMeters,
                                            aircraftMassKilograms)


    def updateAircraftStateVector(self,
                                  elapsedTimeSeconds            ,
                                  trueAirSpeedMetersPerSecond   ,
                                  altitudeMeanSeaLevelMeters    ,
                                  currentDistanceFlownMeters    ,
                                  distanceStillToFlyMeters      ,
                                  aircraftMassKilograms         ,
                                  flightPathAngleDegrees        ,
                                  thrustNewtons                 ,
                                  dragNewtons                   ,
                                  liftNewtons                   ,
                                  endOfSimulation):
        
        self.StateVector.updateAircraftStateVector(elapsedTimeSeconds           , 
                                                   trueAirSpeedMetersPerSecond  , 
                                                   altitudeMeanSeaLevelMeters   , 
                                                   currentDistanceFlownMeters   , 
                                                   distanceStillToFlyMeters     , 
                                                   aircraftMassKilograms        , 
                                                   flightPathAngleDegrees       ,
                                                   thrustNewtons                 ,
                                                   dragNewtons                   ,
                                                   liftNewtons                   ,
                                                   endOfSimulation)
        
        calibratedAirSpeedKnots = self.atmosphere.tas2cas(tas = trueAirSpeedMetersPerSecond ,
                                                  altitude = altitudeMeanSeaLevelMeters,
                                                  temp='std',
                                                  speed_units = 'm/s',
                                                  alt_units='m'
                                                  ) * MeterSecond2Knots
        if (calibratedAirSpeedKnots > self.MaxOpSpeedCasKnots):
            print self.className + ': CAS= {0:.2f} knots >> higher than Max Op CAS= {1:.2f} knots'.format(calibratedAirSpeedKnots, self.MaxOpSpeedCasKnots)
            endOfSimulation = True
            
        if (altitudeMeanSeaLevelMeters * Meter2Feet) > self.MaxOpAltitudeFeet:
            print self.className + ': current altitude= {0:.2f} feet >> higher than Max Operational Altitude= {1:.2f} feet'.format((altitudeMeanSeaLevelMeters * Meter2Feet), self.MaxOpAltitudeFeet)
            endOfSimulation = True
            
        if altitudeMeanSeaLevelMeters < 0.0:
            print self.className + ': altitude MSL= {0:.2f} meters is negative => end of simulation'.format(altitudeMeanSeaLevelMeters)
            endOfSimulation = True
            
        if trueAirSpeedMetersPerSecond < 0.0:
            print self.className + ': tas= {0:.2f} m/s is negative => end of simulation'.format(trueAirSpeedMetersPerSecond)
            endOfSimulation = True

        return endOfSimulation
    
    def createStateVectorHistoryFile(self):
        self.StateVector.createStateVectorHistoryFile()
    
    
    def getCurrentAltitudeSeaLevelMeters(self):
        return self.StateVector.getCurrentAltitudeSeaLevelMeters()
    
    
    def getCurrentTrueAirSpeedMetersSecond(self):
        return self.StateVector.getCurrentTrueAirSpeedMetersSecond()
    
    
    def getCurrentDistanceFlownMeters(self):
        return self.StateVector.getCurrentDistanceFlownMeters()
    
    
    def getFlightPathAngleDegrees(self):
        return self.StateVector.getFlightPathAngleDegrees()


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
            flightEnvelope = FlightEnvelope(aircraftPerformance = aircraftPerformance,
                                            ICAOcode = aircraftICAOcode,
                                            atmosphere = atmosphere,
                                            earth = earth)
            print flightEnvelope
        
        
        
if __name__ == '__main__':
    unittest.main() 