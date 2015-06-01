'''
Created on 8 avr. 2015

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

@note: Read an XLS file containing the runways

'''

import os
import time
import unittest

from Home.xlrd import open_workbook

fieldNames = ['id' , 'airport_ref', 'airport_ident' , 'length_ft' , 'width_ft' ,
              'surface' , 'lighted', 'closed', 
              'le_ident' , 'le_latitude_deg' , 'le_longitude_deg' , 
              'le_elevation_ft', 'le_heading_degT', 'le_displaced_threshold_ft' ,
              'he_ident' , 'he_latitude_deg' , 'he_longitude_deg' , 
              'he_elevation_ft' , 'he_heading_degT', 'he_displaced_threshold_ft' ]

Feet2Meter = 0.3048

class RunWay(object):
    
    '''
    The Charles De Gaulle airport has 2 configurations, depending on the wind directions.
    However, in both configurations Eastward and Westward of Charles de Gaulle:
    - The Run-ways 08R/26L and 09L/27R (far from the terminal) are mainly used for landings.
    - The Run-ways 08L/26R and 09R/27L (near the terminal) are mainly used for take-offs. 
    
    Id, ICAO,Number, Length Meters, Length Feet,Orientation Degrees
    The run-way true heading is defined as the angle 
      1) expressed in degrees
      2) counted from the geographic NORTH, 
      3) clock-wise 
      4) with the run-way end point as the summit of the angle

    Lat-long are the position of the end of the runway
    1) end - if takeoff runway -  is the location the aircraft starts its ground run
    2) end - if landing runway - is the location where after the touch down and deceleration, the ac reaches the taxi speed
     
    '''
    className = ''
    airportICAOcode = ''
    Name = ''
    LengthFeet = 0.0
    TrueHeadingDegrees = 0.0
    TakeOffLanding = ''
    LatitudeDegrees = 0.0
    LongitudeDegrees = 0.0
    
    def __init__(self, 
                 Name, 
                 airportICAOcode, 
                 LengthFeet, 
                 TrueHeadingDegrees, 
                 LatitudeDegrees, 
                 LongitudeDegrees):
        
        self.className = self.__class__.__name__

        assert not(Name is None) and isinstance(Name, (str, unicode)) 
        assert not(airportICAOcode is None) and isinstance(airportICAOcode, (str, unicode))
                    
        assert not (LengthFeet is None) and isinstance(LengthFeet, float) and (LengthFeet>0.0)
            
        assert not (TrueHeadingDegrees is None) and isinstance(TrueHeadingDegrees, float) 
        assert (-360.0 <= TrueHeadingDegrees) and (TrueHeadingDegrees <= 360.0)
                    
        assert not (LatitudeDegrees is None) and (isinstance(LatitudeDegrees, float)) 
        assert (-90.0 <= LatitudeDegrees) and (LatitudeDegrees <= 90.0)
            
        assert not (LongitudeDegrees is None) and (isinstance(LongitudeDegrees, float))
        assert (-180.0 <= LongitudeDegrees) and (LongitudeDegrees <= 180.0)
            
        self.airportICAOcode = airportICAOcode
        self.Name = Name
        self.LengthFeet = LengthFeet
        self.TrueHeadingDegrees = TrueHeadingDegrees
        self.LatitudeDegrees = LatitudeDegrees
        self.LongitudeDegrees = LongitudeDegrees
                                    
            
    def getName(self):
        return self.Name
    
    def getAirportICAOcode(self):
        return self.airportICAOcode
    
    def getLengthMeters(self):
        return self.LengthFeet * Feet2Meter
    
    def getTrueHeadingDegrees(self):
        return self.TrueHeadingDegrees
    
    def getLatitudeDegrees(self):
        return self.LatitudeDegrees
    
    def getLongitudeDegrees(self):
        return self.LongitudeDegrees
    
    def __str__(self):
        strRunWay = self.className
        strRunWay += ': runway= ' + self.Name
        strRunWay += ' airport ICAO code= '     + self.airportICAOcode 
        strRunWay += ' length= {0:.2f} feet'.format(self.LengthFeet) 
        strRunWay += ' true heading= {0:.2f} degrees'.format(self.TrueHeadingDegrees)
        strRunWay += ' latitude= {0:.2f} degrees'.format(self.LatitudeDegrees)
        strRunWay += ' longitude= {0:.2f} degrees'.format(self.LongitudeDegrees)
        return strRunWay
    
    
class RunWayDataBase(object):
    FilePath = ''
    #runWaysDb = {}
    
    def __init__(self):
        self.className = self.__class__.__name__

        self.FilePath = "RunWays.xls"
        
        self.FilesFolder = os.getcwd()
        if not('Home' in self.FilesFolder) and not('Environment' in self.FilesFolder):
            self.FilesFolder += os.path.sep + 'Home' + os.path.sep + 'Environment'
        else:
            ''' case when the run is launched from Home/Tests '''
            self.FilesFolder += os.path.sep  + '..' + os.path.sep  + 'Environment'

        print self.className + ': file folder= {0}'.format(self.FilesFolder)
        self.FilePath = os.path.abspath(self.FilesFolder+ os.path.sep + self.FilePath)
        print self.className + ': file path= {0}'.format(self.FilePath)

        #self.runWaysDb = {}
        
    def getInternalRunWays(self, rowValues):
        '''
        in one row there might be TWO runways
        '''
        if len(str(rowValues[self.ColumnNames['id']]).strip())> 0:
                
            runwayDict = {}
            for column in self.ColumnNames:
                if column == 'id':
                    runwayDict[column] = int(rowValues[self.ColumnNames[column]])
                        
                elif column in ['le_latitude_deg', 'le_longitude_deg', 'le_heading_degT', 
                                    'he_latitude_deg', 'he_longitude_deg', 'he_heading_degT' ,
                                    'length_ft']:
                    ''' float values '''
                    if len(str(rowValues[self.ColumnNames[column]]).strip())>0:
                        runwayDict[column] = float(rowValues[self.ColumnNames[column]])
                    
                elif column in ['le_ident', 'he_ident']:
                    strRunwayName = str(rowValues[self.ColumnNames[column]]).strip().split('.')[0]
                    runwayDict[column] = strRunwayName
                    if str(strRunwayName).isdigit() and int(strRunwayName) < 10 and len(strRunwayName)==1:
                        runwayDict[column] = '0' + strRunwayName
                        
                else:
                    # string fields
                    runwayDict[column] = unicode(rowValues[self.ColumnNames[column]]).strip()
            ''' we have transformed the row values into a Dictionnary => now create the runways '''
            keyOne = ''
            keyTwo = ''
            runwayOne = None
            runwayTwo = None
            if (len(str(rowValues[self.ColumnNames['le_ident']]).strip()) > 0 and
                    len(str(rowValues[self.ColumnNames['airport_ident']]).strip()) > 0 and
                    len(str(rowValues[self.ColumnNames['length_ft']]).strip()) > 0 and
                    len(str(rowValues[self.ColumnNames['le_heading_degT']]).strip()) > 0 and
                    len(str(rowValues[self.ColumnNames['le_latitude_deg']]).strip()) > 0 and
                    len(str(rowValues[self.ColumnNames['le_longitude_deg']]).strip()) > 0 ):
                    
                runwayOne = RunWay(Name                =   runwayDict['le_ident'],
                                    airportICAOcode     =   runwayDict['airport_ident'],
                                    LengthFeet          =   runwayDict['length_ft'],
                                    TrueHeadingDegrees  =   runwayDict['le_heading_degT'],
                                    LatitudeDegrees     =   runwayDict['le_latitude_deg'],
                                    LongitudeDegrees    =   runwayDict['le_longitude_deg'])
                    
                keyOne = runwayDict['le_ident']

                    
            if (len(str(rowValues[self.ColumnNames['he_ident']]).strip()) > 0 and
                    len(str(rowValues[self.ColumnNames['airport_ident']]).strip()) > 0 and
                    len(str(rowValues[self.ColumnNames['length_ft']]).strip()) > 0 and
                    len(str(rowValues[self.ColumnNames['he_heading_degT']]).strip()) > 0 and
                    len(str(rowValues[self.ColumnNames['he_latitude_deg']]).strip()) > 0 and
                    len(str(rowValues[self.ColumnNames['he_longitude_deg']]).strip()) > 0 ):
                    
                runwayTwo = RunWay(Name                =   runwayDict['he_ident'],
                                    airportICAOcode     =   runwayDict['airport_ident'],
                                    LengthFeet          =   runwayDict['length_ft'],
                                    TrueHeadingDegrees  =   runwayDict['he_heading_degT'],
                                    LatitudeDegrees     =   runwayDict['he_latitude_deg'],
                                    LongitudeDegrees    =   runwayDict['he_longitude_deg'])
                                    
                keyTwo = runwayDict['he_ident']

        runwayDict = {}
        if len(keyOne)>0 and not(runwayOne is None):
            runwayDict[keyOne] = runwayOne
        if len(keyTwo)>0 and not(runwayTwo is None):
            runwayDict[keyTwo] = runwayTwo
        return runwayDict
    
    
    def getAirportRunways(self, airportICAOcode, runwayLengthFeet = 0.0):
        return None
        
    def hasRunWays(self, airportICAOcode):
        assert not(self.sheet is None)
        assert (isinstance(airportICAOcode, str)) and len(airportICAOcode)>0
        
        for row in range(self.sheet.nrows): 
            rowValues = self.sheet.row_values(row, start_colx=0, end_colx=self.sheet.ncols)
            if (rowValues[self.ColumnNames['airport_ident']] == airportICAOcode):
                return True
        return False
 
    def getRunWaysAsDict(self, airportICAOcode):
        assert not(self.sheet is None)
        assert (isinstance(airportICAOcode, str)) and len(airportICAOcode)>0
        
        runwaysDict = {}
        for row in range(self.sheet.nrows): 
            rowValues = self.sheet.row_values(row, start_colx=0, end_colx=self.sheet.ncols)
            if (rowValues[self.ColumnNames['airport_ident']] == airportICAOcode):
                runwaysDict.update(self.getInternalRunWays(rowValues))
        
        return runwaysDict        

    def getRunWays(self, airportICAOcode):
        assert not(self.sheet is None)
        assert (isinstance(airportICAOcode, str)) and len(airportICAOcode)>0
        
        runwaysDict = self.getRunWaysAsDict(airportICAOcode)
        
        for runway in runwaysDict.itervalues():
            yield runway
            
        
    def findAirportRunWays(self, airportICAOcode , runwayLengthFeet = 0.0):
        ''' returns a dictionnary with runways '''
        ''' assert there is only one sheet '''
        assert not(self.sheet is None)
        assert (isinstance(airportICAOcode, str)) and len(airportICAOcode)>0
        #print self.className + ': find runways for airport= {0}'.format(airportICAOcode)
        runwaysDict = {}
        for row in range(self.sheet.nrows): 
            rowValues = self.sheet.row_values(row, start_colx=0, end_colx=self.sheet.ncols)
            if runwayLengthFeet > 0.0:
                if (rowValues[self.ColumnNames['airport_ident']] == airportICAOcode) and (rowValues[self.ColumnNames['length_ft']] > runwayLengthFeet):
                    runwaysDict.update(self.getInternalRunWays(rowValues))

            else:
                if (rowValues[self.ColumnNames['airport_ident']] == airportICAOcode):
                    runwaysDict.update(self.getInternalRunWays(rowValues))
        return runwaysDict
        
        
    def read(self):
        ''' this method does not read the whole file - only the headers '''
        assert len(self.FilePath)>0 and os.path.isfile(self.FilePath) 
        book = open_workbook(self.FilePath, formatting_info=True)
        ''' assert there is only one sheet '''
        self.sheet = book.sheet_by_index(0)
        for row in range(self.sheet.nrows): 
            rowValues = self.sheet.row_values(row, start_colx=0, end_colx=self.sheet.ncols)
            if row == 0:
                self.ColumnNames = {}
                index = 0
                for column in rowValues:
                    if column not in fieldNames:
                        print self.className + ': ERROR - expected runway column name= {0} not in field names'.format(column)
                        return False
                    else:
                        self.ColumnNames[column] = index
                    index += 1
                break
        
        return True
    
    
    def __str__(self):
        print self.className + ':RunWay DataBase= {0}'.format(self.FilePath)
        
        
    def getFilteredRunWays(self, airportICAOcode, runwayName = ''):
        assert not(airportICAOcode is None) 
        assert isinstance(airportICAOcode, (str,unicode)) 
        assert (len(airportICAOcode)>0)
        #print self.className + ': query for airport= {0} and runway= {1}'.format(airportICAOcode, runwayName)
        assert not(self.sheet is None)
        runwaysDict = {}
        for row in range(self.sheet.nrows): 
            rowValues = self.sheet.row_values(row, start_colx=0, end_colx=self.sheet.ncols)
            if (rowValues[self.ColumnNames['airport_ident']] == airportICAOcode):
                runwaysDict.update(self.getInternalRunWays(rowValues))
        if runwaysDict.has_key(runwayName):
            return runwaysDict[runwayName]
        else:
            ''' return arbitrary chosen first runway '''
            if len(runwaysDict.keys())> 0 :
                return runwaysDict.values()[0]
            else:
                return None
        
        
    def __getitem__(self, key):
        if key in self.runWaysDb.keys():
            return self.runWaysDb[key]
        else:
            return None
            
    
class Test_Main(unittest.TestCase):

    def test_main_one(self):
    
        print '====================run-ways===================='
        t0 = time.clock()
    
        runWaysDatabase = RunWayDataBase()
        if runWaysDatabase.read():
            print 'runways DB correctly read'
        
        t1 = time.clock()
        print 'time spent= {0:.2f} seconds'.format(t1-t0)
        
        print '====================run-ways===================='
    
        print runWaysDatabase.findAirportRunWays('LFPG')
        t2 = time.clock()
        print 'time spent= {0:.2f} seconds'.format(t2-t1)
        
    
        print '====================run-ways get filtered run ways===================='
        print runWaysDatabase.getFilteredRunWays('LFML') 
        
        print '====================run-ways get filtered run ways===================='
        print runWaysDatabase.getFilteredRunWays('LFBO')
        print '====================run-ways get filtered run ways===================='
    
        print runWaysDatabase.findAirportRunWays('LFBO')
        
        
        print '====================run-ways get filtered run ways===================='
        runway = runWaysDatabase.getFilteredRunWays('EGLL') 
        print runway
        
        print '====================run-ways get filtered run ways===================='
        #print 'number of runways: ' + str(len(runWaysDatabase.getRunWays('LFPG')))
        runway = runWaysDatabase.getFilteredRunWays(airportICAOcode = 'LFPG', runwayName  = '27L')
        print runway
        
        print '====================run-ways get filtered run ways===================='
        runway = runWaysDatabase.getFilteredRunWays(airportICAOcode = 'KJFK', runwayName  = '31L')
        print runway
        
        print '====================run-ways get filtered run ways===================='
    
        runway = runWaysDatabase.getFilteredRunWays(airportICAOcode = 'KLAX', runwayName  = '06L')
        print runway
        
        for ICAOcode in ['LFPG', 'LFPO', 'LFBO', 'LFML', 'LFST', 'KJFK', 'SBGL', 'LFBD']:
            
            print '====================run-ways get filtered run ways===================='
    
            tStart = time.clock()
            print runWaysDatabase.findAirportRunWays(ICAOcode)
            tEnd = time.clock()
            print 'icao= {0} - duration= {1:.2f} seconds'.format(ICAOcode, (tEnd-tStart))
    #     print '====================run-ways===================='
    #     for runway in runWaysDatabase.getRunWays():
    #         print runway.getAirportICAOcode() + '-' + runway.getName()
            
        print '====================run-ways===================='
    #     for runway in runWaysDatabase.getRunWays():
    #         print runway
    
        print '====================run-ways get filtered run ways===================='
    
        print runWaysDatabase.findAirportRunWays('LPPT')
    
    
    def test_main_two(self):
        
        print '====================run-ways test two ===================='

        runWaysDatabase = RunWayDataBase()
        self.assertTrue( runWaysDatabase.read() )
            
        airportICAOcode = 'LPPT'
        self.assertTrue ( runWaysDatabase.hasRunWays(airportICAOcode) )
        
    def test_main_three(self):
        
        print '====================run-ways test three ===================='

        runWaysDatabase = RunWayDataBase()
        self.assertTrue( runWaysDatabase.read() )
        
        airportICAOcode = 'LFPG'
        for runway in runWaysDatabase.getRunWaysAsDict(airportICAOcode) :
            print runway

    def test_main_four(self):

        print '==================== run-ways test four ===================='
    
        runWaysDatabase = RunWayDataBase()
        self.assertTrue( runWaysDatabase.read() )
        
        airportICAOcode = 'LFPG'
        for runway in runWaysDatabase.getRunWays(airportICAOcode) :
            print runway
    
if __name__ == '__main__':
    unittest.main()