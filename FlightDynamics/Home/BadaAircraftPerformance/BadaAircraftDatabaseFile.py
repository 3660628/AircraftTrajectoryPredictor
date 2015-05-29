'''
Created on 23 mai 2015

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
        

this class is responsible for reading the synonym file
The SYNONYM file provided by BADA contains the set of aircraft ICAO code and the prefix to fetch its OPF (Performance file)
this class is aware of the synonym file structure

'''
import os
import time
import unittest

class BadaSynonymAircraft(object):
    ''' 
    this class stores the data provided in the synonym file for one aircraft 
    '''
    def __init__(self, 
                 aircraftICAOcode , 
                 aircraftFullName ,
                 OPFfilePrefix ,
                 useSynonym):
        
        self.className = self.__class__.__name__
        self.aircraftICAOcode = aircraftICAOcode
        self.aircraftFullName = aircraftFullName
        self.OPFfilePrefix = OPFfilePrefix
        self.useSynonym = useSynonym

    def getICAOcode(self):
        return self.aircraftICAOcode
    
    def getAircraftFullName(self):
        return self.aircraftFullName
    
    def getAircraftOPFfilePrefix(self):
        return self.OPFfilePrefix
    

    
    
class BadaAircraftDatabase(object):
    ''' this class is responsible for reading the synonym file '''
    
    
    def __init__(self):
        self.className = self.__class__.__name__
        
        
        self.OPFfileExtension = '.OPF'
        self.BadaSynonymFilePath = 'SYNONYM.NEW'
        
        self.FilesFolder = os.getcwd()
        if not('Home' in self.FilesFolder) and not('BadaAircraftPerformance' in self.FilesFolder):
            self.FilesFolder += os.path.sep + 'Home' + os.path.sep + 'BadaAircraftPerformance'
        else:
            ''' case when the run is launched from Home/Tests '''
            self.FilesFolder += os.path.sep  + '..' + os.path.sep  + 'BadaAircraftPerformance'
            
        print self.className + ': file folder= {0}'.format(self.FilesFolder)
        self.BadaSynonymFilePath = os.path.abspath(self.FilesFolder+ os.path.sep + self.BadaSynonymFilePath)
        print self.className + ': file path= {0}'.format(self.BadaSynonymFilePath)

        self.aircraftFilesFolder = 'Bada381DataFiles'
        if not('Home' in os.getcwd()):
            self.aircraftFilesFolder = os.path.abspath(os.getcwd() + os.path.sep + 'Home' + os.path.sep + self.aircraftFilesFolder)
        else:
            ''' case when the run is launched from Home/Tests '''
            self.aircraftFilesFolder = os.path.abspath(os.getcwd() + os.path.sep  + '..' + os.path.sep  + self.aircraftFilesFolder)
               
        self.aircraftDict = {}

    def exists(self):
        return os.path.exists(self.BadaSynonymFilePath) and os.path.isfile(self.BadaSynonymFilePath)
        
    def getSynonymFilePath(self):
        return self.BadaSynonymFilePath
    
    def read(self):
        print self.className + ': opening file= ', self.BadaSynonymFilePath
        try:
            f = open(self.BadaSynonymFilePath, "r")
            for line in f:
                line = line.strip()
                useSynonym = False
                if str(line).startswith('CD'):
                    #print self.className + ' line= {0}'.format(line)
                    itemIndex = 0
                    aircraftFullName = ''
                    aircraftICAOcode = ''
                    for item in str(line).split():
                        ''' second item 0..1..2 is the aircraft ICAO code '''
                        if itemIndex == 1:
                            if str(item).strip() == '-':
                                #print self.className +' : has main OPF file'
                                useSynonym = False
                            elif str(item).strip() == '*':
                                #print self.className +' : use synonym OPF file'
                                useSynonym = True

                        if itemIndex == 2:
                            ''' second item is the ICAO code '''
                            aircraftICAOcode = str(item).strip()
                            #print self.className + ': aircraft ICAO code= {0}'.format(aircraftICAOcode)
                            
                        if (item.endswith('_')):
                            break
                        
                        elif itemIndex > 3:
                            aircraftFullName += '-' + item
                            
                        elif itemIndex > 2:
                            aircraftFullName += item
                        
                        itemIndex += 1
                    OPFfilePrefix = str(str(line).split()[-3])
                    #print self.className + ': OPF file prefix= {0}'.format(OPFfilePrefix)
                    ''' situation after the item finishing with two underscores __ '''
                    if self.aircraftDict.has_key(aircraftICAOcode ):
                        print self.className + ': aircraft ICAO code already in Database'
                    else:
                        self.aircraftDict[aircraftICAOcode] = BadaSynonymAircraft(aircraftICAOcode = aircraftICAOcode,
                                                                        aircraftFullName = aircraftFullName,
                                                                        OPFfilePrefix = OPFfilePrefix,
                                                                        useSynonym = useSynonym)         
            f.close()
            print self.className + ': number of aircrafts in db= {0}'.format(len(self.aircraftDict))
            return True
        except Exception as e:
            raise ValueError(self.className + ': error= {0} while reading= {1} '.format(e, self.BadaSynonymFilePath))
        return False    


    def aircraftExists(self, aircraftICAOcode):
        aircraftICAOcode = str(aircraftICAOcode).upper()
        print self.className + ': aircraft= {0} exists= {1}'.format(aircraftICAOcode, 
                                                                    self.aircraftDict.has_key(aircraftICAOcode))
        return self.aircraftDict.has_key(aircraftICAOcode)


    def getAircraftFullName(self, aircraftICAOcode):
        aircraftICAOcode = str(aircraftICAOcode).upper()
        if self.aircraftDict.has_key(aircraftICAOcode):
            ac = self.aircraftDict[aircraftICAOcode]
            return ac.getAircraftFullName()
        else:
            return ''


    def getAircraftPerformanceFile(self, aircraftICAOcode):
        aircraftICAOcode = str(aircraftICAOcode).upper()
        if self.aircraftDict.has_key(aircraftICAOcode):
            ac = self.aircraftDict[aircraftICAOcode]
            OPFfilePrefix = ac.getAircraftOPFfilePrefix()
            
            filePath = os.path.abspath(self.aircraftFilesFolder + os.path.sep + OPFfilePrefix + self.OPFfileExtension)
            return filePath
        
        return ''
        
        
    def aircraftPerformanceFileExists(self, aircraftICAOcode):
        ''' checks that the performance file OPF exists in its specific folder '''
        aircraftICAOcode = str(aircraftICAOcode).upper()
        if self.aircraftDict.has_key(aircraftICAOcode):
            print self.className + ': aircraft= {0} - found in database'.format(aircraftICAOcode)
            ac = self.aircraftDict[aircraftICAOcode]
            OPFfilePrefix = ac.getAircraftOPFfilePrefix()

            filePath = os.path.abspath(self.aircraftFilesFolder + os.path.sep + OPFfilePrefix + self.OPFfileExtension)
            print self.className + ': aircraft= {0} - OPF file= {1} - exists= {2}'.format(aircraftICAOcode,
                                                                                          filePath,
                                                                                          os.path.exists(filePath))
            return os.path.exists(filePath) and os.path.isfile(filePath)
        
        return False


class TestMethods(unittest.TestCase):
#============================================
    def test_upper(self):
    
        t0 = time.clock()
        print '================================='
        acBd = BadaAircraftDatabase()
        print 'file= {0} - exists= {1}'.format(acBd.getSynonymFilePath(), acBd.exists())
        
        t1 = time.clock()
        print 'duration= {0} seconds'.format(t1-t0)
        
        print '================================='
        readReturn = acBd.read()
        print 'file= {0} - read= {1}'.format(acBd.getSynonymFilePath(), readReturn )
        
        t2 = time.clock()
        print 'duration= {0} seconds'.format(t2-t1)
        print '================================='
    
        print acBd.getAircraftFullName('A320')
        
        print '================================='
        print 'aircraft= {0} - exists= {1}'.format('A320', acBd.aircraftPerformanceFileExists('A320'))
        
        print '================================='
        print acBd.getAircraftPerformanceFile('A320')
        
        for acICAOcode in ['A10', 'b737', 'A320', 'B747', 'F50', 'B741', 'B742', 'B743', 'A319', 'CL73']:
            print "================================="
            print "aircraft= ", acICAOcode
            print "================================="
            print 'aircraft= {0} exists= {1}'.format(acICAOcode, acBd.aircraftExists(acICAOcode))
            if acBd.aircraftExists(acICAOcode):
                print 'aircraft= {0} performance file= {1}'.format(acICAOcode, acBd.getAircraftPerformanceFile(acICAOcode))
                print 'aircraft= {0} full name= {1}'.format(acICAOcode, acBd.getAircraftFullName(acICAOcode))
                print  acBd.getAircraftPerformanceFile(acICAOcode)
                        
                        
        assert (True)
    

if __name__ == '__main__':
    unittest.main()