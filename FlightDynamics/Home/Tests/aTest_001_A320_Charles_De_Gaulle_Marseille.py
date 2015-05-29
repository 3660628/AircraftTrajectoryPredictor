'''
Created on 6 janvier 2015

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

import time


from Home.Guidance.FlightPathFile import FlightPath


Meter2Feet = 3.2808 # one meter equals 3.28 feet
Meter2NauticalMiles = 0.000539956803 # One Meter = 0.0005 nautical miles
NauticalMiles2Meter = 1852 
   

#============================================
if __name__ == '__main__':
    
    print "=========== Flight Plan start  =========== " 
    
    strRoute = 'ADEP/LFPG-ERMONT-GIF-JURAN-MEIL-CHALM-ADES/LFML'
    strRoute = 'ADEP/LFPG-LATRA-LAMUT-LAKOB-OBEPA-LERGA-ADES/LFML'
    flightPath = FlightPath(route = strRoute, 
                            aircraftICAOcode = 'A320',
                            RequestedFlightLevel = 330, 
                            cruiseMach = 0.82, 
                            takeOffMassKilograms = 68000.0)
    '''
    RFL:    FL 310 => 31000 feet
    Cruise Speed    Mach 0.78                                    
    Take Off Weight    62000 kgs    
    '''
    print "=========== Flight Plan compute  =========== " + time.strftime("%c")
    
    t0 = time.clock()
    print 'time zero= ' + str(t0)
    lengthNauticalMiles = flightPath.computeLengthNauticalMiles()
    print 'flight path length= {0:.2f} nautics '.format(lengthNauticalMiles)
    flightPath.computeFlight(deltaTimeSeconds = 1.0)
    print 'simulation duration= ' + str(time.clock()-t0) + ' seconds'
    
    print "=========== Flight Plan create output files  =========== " + time.strftime("%c")
    flightPath.createFlightOutputFiles()
    print "=========== Flight Plan end  =========== " + time.strftime("%c")
