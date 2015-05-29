'''
@since: Created on 3 mars 2015

@author: PASTOR Robert

        Written By:
                Robert PASTOR 
                @Email: < robert [--DOT--] pastor0691 (--AT--) orange [--DOT--] fr >

        http://trajectoire-predict.monsite-orange.fr/ 
        Copyright 2015 Robert PASTOR 

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


import os.path
import re

'''
The wake category can also be one of three values:
H - heavy
M - medium
L - light
'''
wakeTurbulenceCategoryTypes = ['H','M','L']

re_f_float_neg = re.compile('(-?[0-9.]*)(-\d\d\d)')
def fortran_float(input_string):
    """
    Return a float of the input string, just like `float(input_string)`,
    but allowing for Fortran's string formatting to screw it up when 
    you have very small numbers (like 0.31674-103 instead of 0.31674E-103 )
    """
    try:
        fl = float(input_string)
    except ValueError,e:
        match = re_f_float_neg.match(input_string.strip())
        if match:
            processed_string = match.group(1)+'E'+match.group(2)
            fl = float(processed_string)
        else:
            print "Trying to find number from ",input_string
            raise e
    return fl


class AircraftPerformance(object):
    className = ''
    ''' line in the OPF file - first line has index 0 '''
    AircraftTypeLine = 0
    AircraftMassLine = 1
    flightEnvelopeLine = 2
    AeroDynamicsLine = 3
    ConfigurationCharacteristicsLine = 4
    EngineLine = 15
    FuelConsumptionLine = 18
    GroundMovementLine = 21
    
    filePath = ''
    dataLines = {}
    
    def __init__(self, aircraftPerformanceFilePath):
        self.className = self.__class__.__name__

        self.filePath = aircraftPerformanceFilePath
        if self.exists():
            self.read()
            
    def exists(self):
        if os.path.isfile(self.filePath):
            #print self.className + ' : Performance file= ' + self.filePath + " exists"
            return True
        else:
            raise ValueError(self.className +": BADA Performance File not found: "+self.filePath)
        return False
    
    
    def read(self):
        try:
            dataLineIndex = 0
            f = open(self.filePath, "r")
            for line in f:
                line = line.strip()
                ''' data lines are starting with 'CD' '''
                if str(line).startswith('CD'):
                    #print line
                    self.dataLines[dataLineIndex] = line.strip()
                    dataLineIndex += 1
            f.close()
        except:
            raise ValueError(self.className + ': error while reading file = ' + self.filePath)
        
    def getNumberOfEngines(self):
        try:
            if len(self.dataLines)>0:
                # nb engines placed in line index=0 and position in the split =2
                return int(str(self.dataLines[self.AircraftTypeLine]).split()[2])
        except:
            raise ValueError(self.className + ': error while reading number of engines')
        return 0

    def getStrEngineType(self):
        engineType = ''
        try:
            if len(self.dataLines)>0:
                engineType = str(self.dataLines[self.AircraftTypeLine]).split()[4]
            # check that engine type is known
            return engineType
            
        except:
            raise ValueError("BadaPerformanceFile: error while reading engine type")
        return engineType
    
    def getWakeTurbulenceCategory(self):
        wakeTurbulenceCategory = ''
        try:
            if len(self.dataLines)>0:
                wakeTurbulenceCategory = str(self.dataLines[0]).split()[5]
            if wakeTurbulenceCategory in wakeTurbulenceCategoryTypes:
                return wakeTurbulenceCategory
            else:
                raise ValueError('Bada PerformanceFile: unkown wake turbulence category'+wakeTurbulenceCategory)
        except:
            raise ValueError('BadaPerformanceFile: error while reading wake turbulence category')
        return wakeTurbulenceCategory      
    
    def getReferenceMassTons(self):
        try:
            if len(self.dataLines)>0:
                # mass data is in lines index 1 - reference mass has split index 1 (after CD)
                return fortran_float(str(self.dataLines[self.AircraftMassLine]).split()[1])
        except:
            raise ValueError("BadaPerformanceFile: error while reading reference mass in Tons")
        return 0.0
    
    def getMinimumMassTons(self):
        try:
            if len(self.dataLines)>0:
                # mass data is in lines index 1 - reference mass has split index 2 (after CD)
                return fortran_float(str(self.dataLines[self.AircraftMassLine]).split()[2])
        except:
            raise ValueError("BadaPerformanceFile: error while reading minimum mass in Tons")
        return 0.0
    
    def getMaximumMassTons(self):
        try:
            if len(self.dataLines)>0:
                # mass data is in lines index 1 - reference mass has split index 3 (after CD)
                return fortran_float(str(self.dataLines[self.AircraftMassLine]).split()[3])
        except:
            raise ValueError("BadaPerformanceFile: error while reading Maximum mass in Tons")
        return 0.
    
    def getMaximumPayLoadMassKilograms(self):
        try:
            if len(self.dataLines)>0:
                # mass data is in lines index 1 - reference mass has split index 3 (after CD)
                return fortran_float(str(self.dataLines[self.AircraftMassLine]).split()[4])
        except:
            raise ValueError("BadaPerformanceFile: error while reading Max PayLoad mass in Tons")
        return 0.
    
    '''==============================Envelope ============================================='''
   
    def getVmoCasKnots(self):
        try:
            if len(self.dataLines)>0:
                # mass data is in lines index 2 - reference mass has split index 1 (after CD)
                return fortran_float(str(self.dataLines[self.flightEnvelopeLine]).split()[1])
        except:
            raise ValueError("BadaPerformanceFile: error while reading Vmo Cas Knots")
        return 0.0
    
    def getMaxOpMachNumber(self):
        try:
            if len(self.dataLines)>0:
                # mass data is in lines index 2 - reference mass has split index 2 (after CD)
                return fortran_float(str(self.dataLines[self.flightEnvelopeLine]).split()[2])
        except:
            raise ValueError("BadaPerformanceFile: error while reading Max Op Mach Number")
        return 0.0

    def getMaxOpAltitudeFeet(self):
        try:
            if len(self.dataLines)>0:
                # mass data is in lines index 2 - reference mass has split index 3 (after CD)
                return fortran_float(str(self.dataLines[self.flightEnvelopeLine]).split()[3])
        except:
            raise ValueError("BadaPerformanceFile: error while reading Max Operational Altitude in Feet")
        return 0.0
            
    '''=============== Aero Dynamics ==================='''
   
    def getWingAreaSurfaceSquareMeters(self):
        try:
            if len(self.dataLines)>0:
                return fortran_float(str(self.dataLines[self.AeroDynamicsLine]).split()[2])
        except:
            raise ValueError("BadaPerformanceFile: error while reading Wing Area Surface Square Meters")
        return 0.
            
    ''' =================================== '''
    def getTakeOffLengthMeters(self):
        assert(not(self.GroundMovementLine is None)) and (self.GroundMovementLine>0)
        try:
            if len(self.dataLines)>0:
                '''
                TOL - Ground Movement
                '''
                return fortran_float(str(self.dataLines[self.GroundMovementLine]).split()[1])
        except Exception as e:
            raise ValueError("BadaPerformanceFile: error while reading Ground Movement Take Off Length {0}".format(e))
        return 0.0
                
    def getLandingLengthMeters(self):
        '''
        Ground Movement Block
            The OPF ground movement block consists of 1 data line with 3 comment lines for a total of 4 lines.
        An example of a ground movement block is shown below. The ground movement block is the last
        block in the OPF file and is thus followed by the end-of-file line as shown below.
        CC====== Ground ======================================================/
        CC TOL LDL span length unused /
        1 -> CD .23620E+04 .15550E+04 .44840E+02 .54080E+02 .00000E+00 /
        CC====================================================================/
        FI /
        The data line specifies the following BADA parameters for ground movements:
        TOL LDL span length
        These parameters are specified in the following fixed format (Fortran notation):
        'CD', 2X, 4 (3X, E10.5)
        '''
        assert(not(self.GroundMovementLine is None)) and (self.GroundMovementLine>0)
        try:
            if len(self.dataLines)>0:
                return fortran_float(str(self.dataLines[self.GroundMovementLine]).split()[2])

        except Exception as e:
            raise ValueError("BadaPerformanceFile: error while reading Ground Movement Landing Length {0}".format(e))
        return 0.0
    
    '''======== Configuration Characteristics ===================='''
   
    def getVstallKcasKnots(self):
        VstallKcasKnots = {}
        #print self.className + ': get Cruise Vstall KCAS'
        try:
            if len(self.dataLines)>0:
                for line in range(self.ConfigurationCharacteristicsLine, self.ConfigurationCharacteristicsLine+5):
                    #print line
                    key = str(self.dataLines[line]).split()[2]
                    #print key
                    VstallKcasKnots[key] = fortran_float(str(self.dataLines[line]).split()[4])
                    #print VstallKcas[key]
        except Exception as e:
            raise ValueError('BadaPerformanceFile: error while reading V Stall Speeds {0}'.format(e))
        return VstallKcasKnots
    
    def getMaxClimbThrustCoeff(self, index):
        
        assert (isinstance(index, int) and index >= 0 and index <= 5)
        assert(not(self.EngineLine is None)) and (self.EngineLine > 0)

        try:
            if len(self.dataLines) > 0:
                return fortran_float(str(self.dataLines[self.EngineLine]).split()[index+1])

        except Exception as e:
            raise ValueError('BadaPerformanceFile: error while reading Max CLimb Thrust Coeff {0}'.format(e))
        return 0.0
    
    
    def getDescentThrustCoeff(self, index):
        
        assert (isinstance(index, int) and index >= 0 and index <= 5)
        assert(not(self.EngineLine is None)) and (self.EngineLine > 0)

        try:
            if len(self.dataLines) > 0:
                return fortran_float(str(self.dataLines[self.EngineLine+1]).split()[index+1])

        except Exception as e:
            raise ValueError('BadaPerformanceFile: error while reading Max CLimb Thrust Coeff {0}'.format(e))
        return 0.0
           
           
    def getDragCoeff(self):
        '''
        Specifically, five different configurations are specified with a stall speed 
        [(Vstall)i ] and configuration threshold altitude [Hmax, i ] given for each
        
        CC n Phase  Name    Vstall(KCAS)    CD0          CD2        unused    /
        CD 1 CR   Clean     .13900E+03   .25954E-01   .25882E-01   .00000E+00 /
        CD 2 IC   1         .11300E+03   .28410E-01   .37646E-01   .00000E+00 /
        CD 3 TO   1+F       .10400E+03   .44520E-01   .32811E-01   .00000E+00 /
        CD 4 AP   2         .10000E+03   .46986E-01   .35779E-01   .00000E+00 /
        CD 5 LD   FULL      .94000E+02   .97256E-01   .36689E-01   .00000E+00 /
        '''
        DragCoeff = {}
        CD0 = {}
        CD2 = {}
        #print self.className + ': get Drag coeff'
        try:
            if len(self.dataLines)>0:
                for line in range(self.ConfigurationCharacteristicsLine, self.ConfigurationCharacteristicsLine+5):
                    #print line
                    key = str(self.dataLines[line]).split()[2]
                    #print key
                    CD0[key] = fortran_float(str(self.dataLines[line]).split()[5])
                    CD2[key] = fortran_float(str(self.dataLines[line]).split()[6])
                    #print VstallKcas[key]
        except Exception as e:
            raise ValueError('BadaPerformanceFile: error while reading drag coeff {0}'.format(e))
        DragCoeff['CD0'] = CD0
        DragCoeff['CD2'] = CD2
        return DragCoeff
    
    def getLandingGearDragCoeff(self):
        '''
        CC       Gear                                                             /
        CD 1      UP                                                          /
        CD 2      DOWN                   .23500E-01   .00000E+00   .00000E+00 /
        '''
        try:
            if len(self.dataLines)>0:
                line = self.ConfigurationCharacteristicsLine + 8
                
                return fortran_float(str(self.dataLines[line]).split()[3])
                    #print VstallKcas[key]
        except Exception as e:
            raise ValueError('BadaPerformanceFile: error while reading landing gear drag coeff {0}'.format(e))
        
        return 0.0

    def getFuelConsumptionCoeff(self):
        #print self.className + ': get Fuel Consumption'
        FuelConsumptionCoeff = {}
        try:
            index = 0
            if len(self.dataLines)>0:
                for line in range(self.FuelConsumptionLine, self.FuelConsumptionLine+3):
                    # from each line we extract 2 values
                    count = 0
                    #print line
                    FuelConsumptionCoeff[index] = fortran_float(str(self.dataLines[line]).split()[count+1])
                    count += 1
                    index += 1
                    FuelConsumptionCoeff[index] = fortran_float(str(self.dataLines[line]).split()[count+1])
                    index += 1
                    #print VstallKcas[key]
        except Exception as e:
            raise ValueError('BadaPerformanceFile: error while reading fuel consumption coeff {0}'.format(e))
        
        return FuelConsumptionCoeff
