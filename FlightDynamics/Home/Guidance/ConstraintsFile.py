# -*- coding: UTF-8 -*-
'''
Created on 2 juin 2015

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

@note : manages a set of constraints contained in the flight plan


1.3.6.1 − Vitesse

Insérer la vitesse de croisière pour la première partie ou la totalité de la croisière sous une des formes suivantes :
N suivi de 4 chiffres pour la vitesse propre (TAS) en nœuds (exemple : N0450),
K suivi de 4 chiffres pour la vitesse propre en km/h (exemple : K0320), !!!! NOT IMPLEMENTED !!!!!!
M suivi de 3 chiffres pour une vitesse exprimée en nombre de Mach (exemple : M078).

1.3.6.2 − Niveau

Insérer le niveau de croisière prévu pour la première partie ou la totalité de la route à 
parcourir sous l’une des formes suivantes :
F suivi de 3 chiffres : niveau de vol (exemple : F080),
A suivi de 3 chiffres : altitude en centaines de pieds (exemple : A100 pour 10 000 ft),
S suivi de 4 chiffres : niveau métrique standard en dizaines de mètres !!!! NOT IMPLEMENTED !!!!
(lorsque les autorités ATS compétentes le prescrivent, exemple : S1130),
M suivi de 4 chiffres : altitude en dizaines de mètres (lorsque les autorités ATS compétentes le prescrivent, exemple : M0710),
VFR pour un vol VFR sans niveau de croisière déterminé à l’avance. 

'''

feet2Meters = 0.3048 #meters
Meters2Feet = 3.2808399

def mayBeKnotsSpeedConstraint(fixIndex, fix):
    constraintFound = False
    levelConstraint = None
    speedConstraint = None
    ''' maybe a speed constraint starting with N hence knots speed '''
    speedKnots = str(fix[1:])
    if str(speedKnots).isdigit():
        ''' if rest of the string is digit then it is a speed constraint without any level constraint '''
        print 'Constraints: speed constraint expressed as Knots= {0}'.format(speedKnots)
        speedConstraint = SpeedConstraint ( fixIndex = fixIndex , 
                                                    speed = speedKnots ,
                                                    units = 'knots')
        constraintFound = True
                        
    else:
        ''' rest of the string is not composed only of digits '''
        subString = str(fix[1:])
        ''' may contain a level constraint '''
        indexOfLevelConstraint = str(subString).find('F')
        if indexOfLevelConstraint >= 0:
            ''' there is level constraint '''
            speedKnots = str(subString[0:indexOfLevelConstraint])
            if str(speedKnots).isdigit():
                print 'Constraints: speed constraint= {0} knots'.format(speedKnots)
                speedConstraint = SpeedConstraint(fixIndex = fixIndex , 
                                                          speed = speedKnots ,
                                                          units = 'knots')
                constraintFound = True
                levelFlightLevel = str(subString[indexOfLevelConstraint:])
                print 'Constraints: level constraint= {0}'.format(levelFlightLevel)
                levelConstraint = LevelConstraint ( fixIndex = fixIndex,
                                                            level = str(levelFlightLevel[1:]),
                                                            units = 'FL')

            else:
                ''' did found an N ... and a F => but in the middle there are not digits '''
                constraintFound = False
                        
        else:
            ''' did found an N but no F .. now searching for A '''
            indexOfLevelConstraint = str(subString).find('A')
            if indexOfLevelConstraint >= 0:
                ''' there is probably a level constraint '''
                speedKnots = str(subString[1:indexOfLevelConstraint])
                if str(speedKnots).isdigit():
                    print 'Constraints: speed constraint= {0} knots'.format(speedKnots)
                    speedConstraint = SpeedConstraint(fixIndex = fixIndex , 
                                                              speed = speedKnots ,
                                                              units = 'knots')
                    constraintFound = True

                    levelAltitudeFeet = str(subString[indexOfLevelConstraint:])
                    print 'Constraints: level constraint= {0}'.format(levelAltitudeFeet)
                else:
                    ''' found an N, rest of the string are not digits but do not found neither a F nor a A => not a constraint '''
                    constraintFound = False
                        
    return constraintFound, levelConstraint, speedConstraint


def mayBeMachSpeedConstraint(fixIndex, fix):
    constraintFound = False
    speedConstraint = None
    levelConstraint = None
    speedMach = str(fix[1:])
    if str(speedMach).isdigit():
        ''' the rest of the string is composed only of digits => no other constraints '''
        print 'Constraints: speed constraint expressed as Mach= {0}'.format(speedMach)
        speedConstraint = SpeedConstraint ( fixIndex = fixIndex,
                                                    speed = speedMach,
                                                    units = 'mach')
        constraintFound = True
                
    else:
        ''' rest of the fix after M is not composed only of digits '''
        subString = str(fix[1:])
        ''' check if there is a level constraint '''
        indexOfLevelConstraint = str(subString).find('F')
        if indexOfLevelConstraint >= 0:
            ''' there is level constraint '''
            speedKnots = str(subString[1:indexOfLevelConstraint])
            if str(speedKnots).isdigit():
                print 'Constraints: speed constraint= {0} knots'.format(speedKnots)
                speedConstraint = SpeedConstraint ( fixIndex = fixIndex,
                                                            speed = speedKnots,
                                                            units = 'knots')
                        
                levelFlightLevel = str(subString[indexOfLevelConstraint:])
                print 'Constraints: level constraint= {0}'.format(levelFlightLevel)
                levelConstraint = LevelConstraint( fixIndex = fixIndex,
                                                           level = levelFlightLevel,
                                                           units = 'FL')
                constraintFound = True
 
        else:
            indexOfLevelConstraint = str(subString).find('A')
            if indexOfLevelConstraint >= 0:
                speedMach = subString[:indexOfLevelConstraint]
                ''' there is probably a level constraint '''
                levelAltitudeFeet = str(subString[indexOfLevelConstraint+1:])
                if str(levelAltitudeFeet).isdigit() and str(speedMach).isdigit():
                    speedConstraint = SpeedConstraint ( fixIndex = fixIndex,
                                                            speed = speedMach,
                                                            units = 'mach')
                    print 'Constraints : level constraint= {0}'.format(levelAltitudeFeet)
                    levelConstraint = LevelConstraint ( fixIndex = fixIndex ,
                                                                level = levelAltitudeFeet,
                                                                units = 'feet')
                    constraintFound = True
                else:
                    constraintFound = False
    
    return constraintFound, levelConstraint, speedConstraint
                    

def analyseConstraint(fixIndex , fix):
        
    '''
        N suivi de 4 chiffres pour la vitesse propre (TAS) en noeuds (exemple : N0450),
        M suivi de 3 chiffres pour une vitesse exprimée en nombre de Mach (exemple : M078).
    '''
    '''
        F suivi de 3 chiffres : niveau de vol (exemple : F080),
        A suivi de 3 chiffres : altitude en centaines de pieds (exemple : A100 pour 10 000 ft),
    '''
    constraintFound = False
    speedConstraint = None
    levelConstraint = None
    if str(fix).startswith('N'):
        ''' may be a speed constraint starting with N => hence expressed in knots '''
        return mayBeKnotsSpeedConstraint(fixIndex, fix)
                        
    elif str(fix).startswith('M'):
        ''' may be a Mach Speed Constraint '''
        return mayBeMachSpeedConstraint(fixIndex, fix)
                        
    return constraintFound, levelConstraint, speedConstraint


class ConstraintsApplicability(object):
    pass

    ''' typical values are :
    1) after take-off
    2) before a fix
    3) below a given level (ex: speed must be lower to 250 knots below 10.000 feet
    '''


class Constraints(object):
    ''' 
    the constraints class defines when a constraint becomes applicable 
    '''
    
    def __init__(self, fixIndex ):
        self.className = self.__class__.__name__
        
        assert isinstance(fixIndex, int)
        self.fixIndex = fixIndex
        ''' after a fix => this fix cannot be suppressed or if suppressed then report the constraint to the previous fix'''
        
        ''' after take-off '''
        if fixIndex == 0:
            print self.className + ' constraint is applicable after Take Off or first fix'
    
class SpeedConstraint(Constraints):
    '''
    the speed constraints defines the target value to achieve
    it might be to accelerate from the current to the target
    or it might be to decelerate from the current speed to the target speed
    or finally it may be to stay at the current speed if the difference is less than an epsilon
    '''
    def __init__(self, fixIndex, speed , units ):
        
        Constraints.__init__(self, fixIndex)

        assert units in ['knots' , 'mach']
        self.units = units
        
        assert str(speed).isdigit()
        self.targetSpeed = float(speed)
        
        self.targetSpeedMach = 0.0
        if units == 'mach':
            self.targetSpeedMach = float( speed ) / 100.0
            print self.className + ': speed constraints after fixIndex= {0} - speed= {1} - units= {2}'.format(self.fixIndex,
                                                                                                         self.targetSpeedMach,
                                                                                                         units)
            
        elif units == 'knots':
            self.targetSpeedKnots = float(speed)
            print self.className + ': speed constraints after fixIndex= {0} - speed= {1} - units= {2}'.format(self.fixIndex,
                                                                                                         self.targetSpeedKnots,
                                                                                                         units)
            
        

class LevelConstraint(Constraints):
    
    def __init__(self, fixIndex, level , units ):
        
        Constraints.__init__(self, fixIndex)
        
        assert units in ['FL', 'feet']
        self.units = units
        
        self.targetLevelMeters = 0.0
        if units == 'feet':
            self.targetLevelMeters = float(level) * 100.0 * feet2Meters
        elif units == 'FL':
            self.targetLevelMeters = float(level) * 100.0 * feet2Meters

        print self.className + ': level constraints after fixIndex= {0} - level= {1} meters - level= {2} feet'.format(self.fixIndex,
                                                                                                         self.targetLevelMeters,
                                                                                                         self.targetLevelMeters * Meters2Feet)

