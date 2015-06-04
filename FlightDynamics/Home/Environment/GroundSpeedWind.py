'''
Created on February 18, 2015

@author: Robert PASTOR
'''

import math
Knots2MetersPerSecond = 0.514444444
MetersPerSecond2Knots = 1.94384449

class Wind(object):
    windSpeedMetersPerSecond = 0.0
    windDirectionDegrees = 0.0
    
    def __init__(self, windSpeedMetersPerSecond, windDirectionDegrees):
        assert (windSpeedMetersPerSecond >= 0.0)
        assert (windDirectionDegrees >= 0.0) and (windDirectionDegrees <= 360.0)
        
        self.windSpeedMetersPerSecond = windSpeedMetersPerSecond
        self.windDirectionDegrees = math.fmod(windDirectionDegrees + 180.0, 360.0)
    
    
class GroundSpeed(object):
    wind = None
    
    def __init__(self, wind):
        assert (isinstance(wind, Wind))
        self.wind = wind
        
    def computeGroundSpeedMetersPerSecond(self, TasMetersPerSecond, velocityAzimuthDegrees):
        
        assert (TasMetersPerSecond >= 0.0)
        assert (velocityAzimuthDegrees >= 0.0) and (velocityAzimuthDegrees <= 360.0)

        GS1 = TasMetersPerSecond * math.cos(math.radians(velocityAzimuthDegrees))
        GS1 += self.wind.windSpeedMetersPerSecond * math.sin(math.radians(90.0-self.wind.windDirectionDegrees))
        
        GS2 = TasMetersPerSecond * math.sin(math.radians(velocityAzimuthDegrees))
        GS2 += self.wind.windSpeedMetersPerSecond * math.cos(math.radians(90.0-self.wind.windDirectionDegrees))
        
        groundSpeedMetersPerSecond = math.sqrt(GS1*GS1 + GS2*GS2)
        return groundSpeedMetersPerSecond
    
    def computeGroundSpeedAngleDegrees(self, TasMetersPerSecond, velocityAzimuthDegrees):
        
        R1 = TasMetersPerSecond * math.sin(math.radians(velocityAzimuthDegrees))
        R1 += self.wind.windSpeedMetersPerSecond * math.cos(math.radians(90.0-self.wind.windDirectionDegrees))
        
        R2 = TasMetersPerSecond * math.cos(math.radians(velocityAzimuthDegrees))
        R2 += self.wind.windSpeedMetersPerSecond * math.sin(math.radians(90.0-self.wind.windDirectionDegrees))
        return math.degrees(math.atan(R1/R2))
        
if __name__ == '__main__':
    
    print " ========== Ground Speed testing ======= "
    
    ''' direction from where comes the wind - as seen by the aircraft '''
    windDirectionDegrees = 125.0
    windSpeedKnots = 25.0
    wind = Wind(windSpeedKnots*Knots2MetersPerSecond, windDirectionDegrees)
    
    velocityAzimuthDegrees = 30.0
    TasKnots = 150.0
     
    groundSpeed = GroundSpeed(wind)
    GS = groundSpeed.computeGroundSpeedMetersPerSecond(TasKnots*Knots2MetersPerSecond, velocityAzimuthDegrees)
    print 'ground speed= {0:.2f} knots'.format(GS * MetersPerSecond2Knots)
    courseDegrees = groundSpeed.computeGroundSpeedAngleDegrees(TasKnots*Knots2MetersPerSecond, velocityAzimuthDegrees)
    print 'ground track angle= {0:.2f} degrees'.format(courseDegrees)