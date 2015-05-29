# -*- coding: UTF-8 -*-
'''
Created on 3 mai 2015


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

import math

class TransitionAltitude(object):
    '''
    The transition altitude (also called crossover altitude), Hp,trans (feet), between a given CAS,
    VCAS [m/s] and a Mach number, M, is defined to be the geo-potential pressure altitude at
    which VCAS and Mach represent the same TAS value
    '''
    
    def __init__(self, engine):
        self.className = self.__class__.__name__
        self.engine = engine
    
    def computeTransitionAltitudeFeet(self, VCasMeterSecond, Mach):
        '''
        The altitude at which the transition takes places is typically near 27.000 feet for most jets
        depending upon the chosen CAS/Mach speed profile and atmospheric conditions
        Adiabatic index of air : κ = 1.4
        '''
        K = 1.4
        '''
        where a0 is the ISA speed of sound at sea level = 340.29 m.s-1
        '''
        a0 = 340.29 
        '''
        deltaTrans : is the pressure ratio at the transition altitude
        '''
        deltaTrans = 1 + ((K - 1)/2.0)*(VCasMeterSecond/a0)*(VCasMeterSecond/a0)
        deltaTrans = math.pow(deltaTrans, (K/(K-1)))
        deltaTrans = deltaTrans - 1
        deltaTrans = deltaTrans / (math.pow(1 + (((K-1)/2.0)*Mach*Mach), (K/(K-1))) - 1)
        '''
        ISA temperature gradient with altitude below the tropo-pause :
        value is minus 0.0065 Kelvins per meters [°K/m]
        '''
        BetaTemperatureKelvinMeter = - 0.0065
        ''' thetaTrans is the temperature ratio at the transition altitude '''
        thetaTransition = math.pow(deltaTrans, - (BetaTemperatureKelvinMeter * 287.05287) / 9.809)
        HpressureTransitionFeet = (1000.0/(0.3048 * 6.5))*(288.15)*(1 - thetaTransition)
        ''' 27.000 feets for most jets '''
        if not(self.engine.isJet()):
            ''' there is no transition altitude for turbo prop engines aircrafts '''
            raise ValueError (self.className + 'no transition altitude for turbo prop or piston engine aircraft')
        return HpressureTransitionFeet


