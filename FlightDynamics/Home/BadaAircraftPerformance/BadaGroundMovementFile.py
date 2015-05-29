'''
Created on 12 avr. 2015

@author: PASTOR Robert

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

from Home.BadaAircraftPerformance.BadaAircraftPerformanceFile import AircraftPerformance


class GroundMovement(object):
    className = ''

    TakeOffLengthMeters = 0.0
    LandingLengthMeters = 0.0
    
    def __init__(self, aircraftPerformance):
        self.className = self.__class__.__name__
        assert (isinstance(aircraftPerformance, AircraftPerformance))
        self.TakeOffLengthMeters = aircraftPerformance.getTakeOffLengthMeters()
        self.LandingLengthMeters = aircraftPerformance.getLandingLengthMeters()
    
    def getLandingLengthMeters(self):
        return self.LandingLengthMeters
    
    def getTakeOffLengthMeters(self):
        return self.TakeOffLengthMeters
    
    def computeGroundAccelerationMetersPerSquareMeters(self):
        '''
        start with take-off thrust - in Newtons
        THR - thrust acting parallel to the aircraft velocity vector [Newtons]
        
        '''
        raise ValueError('not yet implemented')

    def dump(self):
        print self.className + ': Take Off Length= ' + str(self.TakeOffLengthMeters) + ' meters'
        print self.className + ': Landing Length= ' + str(self.LandingLengthMeters) + ' meters'