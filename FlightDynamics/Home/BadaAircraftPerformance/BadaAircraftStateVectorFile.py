'''
@since: Created on 21 mars 2015

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

MeterSecond2Knots = 1.9438444924406
Meter2Feet = 3.2808
Meter2NauticalMiles = 0.000539956803

from Home.OutputFiles.XlsxOutputFile import XlsxOutput
from Home.Environment.Atmosphere import Atmosphere

class StateVector(object):
    
    className = ''
    aircraftStateHistory = []

    def __init__(self, aircraftICAOcode, atmosphere):
        
        self.className = self.__class__.__name__

        assert isinstance(atmosphere, Atmosphere)
        self.atmosphere = atmosphere
        self.aircraftICAOcode = str(aircraftICAOcode).upper()
        self.aircraftStateHistory = []

        
    def initStateVector(self, 
                          elapsedTimeSeconds, 
                          trueAirSpeedMetersSecond, 
                          altitudeMeanSeaLevelMeters,
                          aircraftMassKilograms,
                          totalDistanceFlownMeters = 0.0,
                          distanceStillToFlyMeters = 0.0):
 
        flightPathAngleDegrees = 0.0
        self.updateAircraftStateVector(elapsedTimeSeconds, 
                                                      trueAirSpeedMetersSecond  , 
                                                      altitudeMeanSeaLevelMeters,
                                                      totalDistanceFlownMeters  ,
                                                      distanceStillToFlyMeters  ,
                                                      aircraftMassKilograms     ,
                                                      flightPathAngleDegrees    ,
                                                      thrustNewtons = 0.0       ,
                                                      dragNewtons   = 0.0       ,
                                                      liftNewtons   = 0.0       ,
                                                      endOfSimulation = False)
        
        
    def updateAircraftStateVector(self, 
                                    elapsedTimeSeconds, 
                                    trueAirSpeedMetersPerSecond,
                                    altitudeMeanSeaLevelMeters,
                                    totalDistanceFlownMeters,
                                    distanceStillToFlyMeters,
                                    aircraftMassKilograms,
                                    flightPathAngleDegrees,
                                    thrustNewtons,
                                    dragNewtons,
                                    liftNewtons,
                                    endOfSimulation):

        ''' need to store both TAS and altitude => compute CAS '''
        aircraftStateDict = {}
        aircraftStateDict[elapsedTimeSeconds] = [altitudeMeanSeaLevelMeters, 
                                                 trueAirSpeedMetersPerSecond, 
                                                 totalDistanceFlownMeters,
                                                 distanceStillToFlyMeters,
                                                 aircraftMassKilograms,
                                                 flightPathAngleDegrees,
                                                 thrustNewtons,
                                                 dragNewtons,
                                                 liftNewtons ]
        self.aircraftStateHistory.append(aircraftStateDict)


    def getCurrentAltitudeSeaLevelMeters(self):
        if len(self.aircraftStateHistory) > 0:
            ''' values returns a list who first element is the expected value '''
            lastDict = self.aircraftStateHistory[-1]
            values = lastDict.values()[0]
            altitudeMSLmeters = values[0]
            return altitudeMSLmeters
        else:
            return 0.0
        

    def getCurrentTrueAirSpeedMetersSecond(self):
        if len(self.aircraftStateHistory) > 0:
            ''' each recorded value is a dictionary '''
            ''' values() retrieves a list with one element - take the one with index = 0 '''
            lastDict = self.aircraftStateHistory[-1]
            values = lastDict.values()[0]
            trueAirSpeedMetersSecond =  values[1]
            return trueAirSpeedMetersSecond
        else:
            raise ValueError(self.className + ': speed history is empty')


    def getCurrentDistanceFlownMeters(self):
        if len(self.aircraftStateHistory) > 0:
            lastDict = self.aircraftStateHistory[-1]
            values = lastDict.values()[0]
            currentDistanceMeters = values[2]
            return currentDistanceMeters
        else:
            return 0.0
        
        
    def getFlightPathAngleDegrees(self):
        if len(self.aircraftStateHistory) > 0:
            lastDict = self.aircraftStateHistory[-1]
            values = lastDict.values()[0]
            flightPathAngleDegrees = values[5]
            return flightPathAngleDegrees
        else:
            return 0.0        

        
    def createStateVectorHistoryFile(self, filePrefix):
        if isinstance(filePrefix, str) and len(filePrefix)>0:
            fileName = self.aircraftICAOcode + '-' + filePrefix + '-Altitude-MSL-Speed-History'
        else:
            fileName = self.aircraftICAOcode +  '-Altitude-MSL-Speed-History'

        xlsxOutput = XlsxOutput(fileName)
        xlsxOutput.writeHeaders(['elapsed-time-seconds', 
                                
                                'altitude-MSL-meters',
                                 'altitude-MSL-feet',

                                 'true-air-speed-meters-second',
                                 'true-air-speed-knots',
                                 
                                 'calibrated-air-speed-knots',
                                 'mach',
                                 'rate-of-climb-descent-feet-minute',
                                 
                                 'distance-flown-nautical-miles',
                                 'distance-to-fly-nautical-miles',
                                 
                                 'aircraft-mass-kilograms'      ,
                                 'flight-path-angle-degrees'    ,
                                 
                                 'thrust-newtons'               ,
                                 'drag-newtons'                 ,
                                 'lift-newtons'                 ,
                                 
                                 'load-factor-g'                
                                 ])

        previousAltitudeMeanSeaLevelFeet = 0.0
        previousElapsedTimeSeconds = 0.0
        cumulatedDistanceFlownNautics = 0.0
        
        for stateVectorHistory in self.aircraftStateHistory:
            for elapsedTimeSeconds, valueList in stateVectorHistory.items():

                ''' altitude '''
                altitudeMeanSeaLevelMeters = valueList[0]
                altitudeMeanSeaLevelFeet = altitudeMeanSeaLevelMeters * Meter2Feet

                ''' speeds '''
                trueAirSpeedMetersSecond = valueList[1]
                trueAirSpeedKnots = trueAirSpeedMetersSecond * MeterSecond2Knots 

                ''' total distance flown in Meters '''
                totalDistanceFlownMeters = valueList[2]
                cumulatedDistanceFlownNautics = totalDistanceFlownMeters * Meter2NauticalMiles
                
                distanceStillToFlyMeters = valueList[3]
                distanceStillToFlyNautics = distanceStillToFlyMeters * Meter2NauticalMiles
                
                ''' aircraft Mass History in Kilograms '''
                aircraftMassKilograms = valueList[4]
                flightPathAngleDegrees = valueList[5]

                thrustNewtons = valueList[6]
                dragNewtons = valueList[7]
                liftNewtons = valueList[8]
                loadFactor = liftNewtons / aircraftMassKilograms

                calibratedAirSpeedMetersSecond = self.atmosphere.tas2cas(tas = trueAirSpeedMetersSecond,
                                                  altitude = altitudeMeanSeaLevelMeters,
                                                  speed_units = 'm/s',
                                                  alt_units='m' )
                calibratesAirSpeedKnots = calibratedAirSpeedMetersSecond * MeterSecond2Knots
                mach = self.atmosphere.tas2mach(tas = trueAirSpeedMetersSecond,
                                altitude = altitudeMeanSeaLevelMeters,
                                speed_units='m/s', 
                                alt_units='m')

                if (elapsedTimeSeconds-previousElapsedTimeSeconds)>0.0:
                    rateOfClimbDescentFeetMinute = (altitudeMeanSeaLevelFeet-previousAltitudeMeanSeaLevelFeet)/ ((elapsedTimeSeconds-previousElapsedTimeSeconds)/60.)
                else:
                    rateOfClimbDescentFeetMinute = 0.0
                previousAltitudeMeanSeaLevelFeet = altitudeMeanSeaLevelFeet
                
                previousElapsedTimeSeconds = elapsedTimeSeconds
                xlsxOutput.writeFifteenFloatValues(elapsedTimeSeconds, 
                                                 altitudeMeanSeaLevelMeters,
                                                 altitudeMeanSeaLevelFeet,
                                                 
                                                 trueAirSpeedMetersSecond,
                                                 trueAirSpeedKnots,
                                                 calibratesAirSpeedKnots,
                                                 mach,
                                                 rateOfClimbDescentFeetMinute,
                                                 
                                                 cumulatedDistanceFlownNautics,
                                                 distanceStillToFlyNautics,
                                                 
                                                 aircraftMassKilograms,
                                                 flightPathAngleDegrees,    
                                                 
                                                 thrustNewtons          ,
                                                 dragNewtons            ,
                                                 liftNewtons            ,
                                                 loadFactor)
        xlsxOutput.close()
                    
                    
