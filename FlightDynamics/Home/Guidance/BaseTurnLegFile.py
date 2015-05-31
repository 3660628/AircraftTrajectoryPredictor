# -*- coding: UTF-8 -*-

'''
Created on 24 December 2014

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

@note: returns a list of angles in degrees from an initial to a final heading for a given increment in degrees
is used in case of SIMULATED arrival turn.

'''
import time
import unittest

class BaseTurnLeg(object):
    
    className = ''
    initialHeadingDegrees = 0.0
    finalHeadingDegrees = 0.0
    incrementDegrees = 0.0
    turnLegList = []
    
    def __init__(self, initialHeadingDegrees, 
                 finalHeadingDegrees, 
                 incrementDegrees ):
        
        self.className = self.__class__.__name__

        assert (isinstance(initialHeadingDegrees, float))
        assert (initialHeadingDegrees >= 0.0) and (initialHeadingDegrees <= 360.0)
        self.initialHeadingDegrees = initialHeadingDegrees
            
        assert (isinstance(finalHeadingDegrees, float))
        assert (finalHeadingDegrees >= 0.0) and (finalHeadingDegrees <= 360.0)
        self.finalHeadingDegrees = finalHeadingDegrees
    
        assert isinstance(incrementDegrees, float)
        ''' increment cannot be null but might be positive or negative '''
        assert (incrementDegrees > 0.0) or (incrementDegrees < 0.0)
        self.incrementDegrees = incrementDegrees
            
        strMsg = self.className + ': Base Turn Leg: initial Heading= ' + str(self.initialHeadingDegrees) + ' degrees'
        strMsg += ' final Heading= ' + str(self.finalHeadingDegrees)+ ' degrees '
        strMsg += ' increment= ' + str(self.incrementDegrees) + ' degrees'
        print strMsg
        
        self.turnLegList = []
                    
        
    def build(self):
        
        self.turnLegList = []
        #print self.initialHeadingDegrees
        self.turnLegList.append(self.initialHeadingDegrees)
        
        if self.incrementDegrees > 0.0:
            print self.className + ': increment is > 0.0 => turn clock-wise '
            if self.initialHeadingDegrees < self.finalHeadingDegrees:
                while self.initialHeadingDegrees < self.finalHeadingDegrees:
                    self.initialHeadingDegrees += self.incrementDegrees
                    self.turnLegList.append(self.initialHeadingDegrees)
                    #print self.initialHeadingDegrees
            else:
                ''' initial heading greater to final ... value will increase then go through 360.0 '''
                while (self.initialHeadingDegrees < 360.0):
                    self.initialHeadingDegrees += self.incrementDegrees
                    if self.initialHeadingDegrees < 360.0:
                        self.turnLegList.append(self.initialHeadingDegrees)

                self.initialHeadingDegrees = 0.0
                self.turnLegList.append(self.initialHeadingDegrees)
                
                while self.initialHeadingDegrees < self.finalHeadingDegrees:
                    ''' need to cope with the situation where initial heading will be greater to 360 '''
                    self.initialHeadingDegrees += self.incrementDegrees
                    self.turnLegList.append(self.initialHeadingDegrees)
                    #print self.initialHeadingDegrees
            
        else:
            print self.className + ': increment is < 0.0 => turn anti-clock wise '
            if self.initialHeadingDegrees < self.finalHeadingDegrees:
                #print ''' initial heading lower to final heading '''
                while self.initialHeadingDegrees > 0.0:
                    self.initialHeadingDegrees += self.incrementDegrees
                    if self.initialHeadingDegrees > 0.0:
                        self.turnLegList.append(self.initialHeadingDegrees)
                    
                self.initialHeadingDegrees = 360.0
                self.turnLegList.append(self.initialHeadingDegrees)
                
                while self.finalHeadingDegrees <  self.initialHeadingDegrees:
                    self.initialHeadingDegrees += self.incrementDegrees
                    self.turnLegList.append(self.initialHeadingDegrees)

            else:
                #print self.className + ': initial heading greater to final'
                while self.finalHeadingDegrees < self.initialHeadingDegrees:
                    self.initialHeadingDegrees += self.incrementDegrees
                    self.turnLegList.append(self.initialHeadingDegrees)
        
        return self.turnLegList
    
    def __str__(self):
        return str( self.turnLegList)
    
    
#============================================
class Test_Class(unittest.TestCase):

    def test_Class(self):

    
        print "=========== Base Turn Leg testing   =========== " + time.strftime("%c")
        
        baseTurnLeg = BaseTurnLeg(150.0, 190.0, 1.0)
        baseTurnLeg.build()
        print baseTurnLeg
        
        print "=========== Base Turn Leg testing   =========== " + time.strftime("%c")
    
        baseTurnLeg = BaseTurnLeg(350.0, 10.0, 1.0)
        baseTurnLeg.build()
        print baseTurnLeg
        
        print "=========== Base Turn Leg testing   =========== " + time.strftime("%c")
        baseTurnLeg = BaseTurnLeg(10.0, 350.0, -1.0)
        baseTurnLeg.build()
        print baseTurnLeg
        
        print "=========== Base Turn Leg testing   =========== " + time.strftime("%c")
        baseTurnLeg = BaseTurnLeg(270.0, 80.0, -1.0)
        baseTurnLeg.build()
        print baseTurnLeg
        
        print "=========== Base Turn Leg testing   =========== " + time.strftime("%c")
        try:
            BaseTurnLeg(361.0, 0.0, 0.0)
            self.assertFalse(True)
        except:
            self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()