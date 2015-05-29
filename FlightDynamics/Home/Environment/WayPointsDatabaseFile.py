# -*- coding: UTF-8 -*-

'''
Created on 31 mars 2015

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

read an EXCEL file containing the way points
'''

import os
import unittest

from Home.Guidance.WayPointFile import WayPoint

from Home.xlrd import open_workbook
from Home.xlwt.Workbook import Workbook

fieldNames = ['WayPoint', 'Country' , 'Type', 'Latitude', 'Longitude' ]

def convertDegreeMinuteSecondToDecimal(DegreeMinuteSecond='43-40-51.00-N'):
    '''
        convert from Decimal Degrees = Degrees + minutes/60 + seconds/3600
        to float
        mays start or end with NE SW
    '''
    DecimalValue = 0.0
    coeff = 0.0
    assert isinstance(DegreeMinuteSecond, str) or isinstance(DegreeMinuteSecond, unicode)
        
    if ( str(DegreeMinuteSecond).endswith("N") or 
         str(DegreeMinuteSecond).endswith("E") or 
         str(DegreeMinuteSecond).startswith("N") or 
         str(DegreeMinuteSecond).startswith("E") ):
        ''' transform into decimal value '''
        coeff = 1.0
        
    elif ( str(DegreeMinuteSecond).endswith("S") or 
           str(DegreeMinuteSecond).endswith("W") or
           str(DegreeMinuteSecond).startswith("S") or 
           str(DegreeMinuteSecond).startswith("W") ):
        ''' transform into decimal value '''
        coeff = -1.0
    
    else :
        raise ValueError ('Degrees Minutes Seconds string should be started or ended by N-E-S-W')
    
    if  ( str(DegreeMinuteSecond).endswith("N") or 
          str(DegreeMinuteSecond).endswith("E") or 
          str(DegreeMinuteSecond).endswith("S") or 
          str(DegreeMinuteSecond).endswith("W") ):
        ''' suppress last char and split '''
        strSplitList = str(DegreeMinuteSecond[:-1]).split('-')
    else:
        ''' suppress first char and split '''
        strSplitList = str(DegreeMinuteSecond[1:]).split('-')

    #print strSplitList[0]
    if str(strSplitList[0]).isdigit() and str(strSplitList[1]).isdigit():
        DecimalDegreeValue = int(strSplitList[0])
        DecimalMinutesValue = int(strSplitList[1])
        #print strSplitList[1]
        strSplitList2 = str(strSplitList[2]).split(".")
        #print strSplitList2[0]
        if (len(strSplitList2)==2 and str(strSplitList2[0]).isdigit() and str(strSplitList2[1]).isdigit()):
                
            DecimalSecondsValue = int(strSplitList2[0])
            TenthOfSecondsValue = int(strSplitList2[1])
            
            DecimalValue = DecimalDegreeValue + float(DecimalMinutesValue)/float(60.0)
            DecimalValue += float(DecimalSecondsValue)/float(3600.0)
            if TenthOfSecondsValue < 10.0:
                DecimalValue += (float(TenthOfSecondsValue)/float(3600.0)) / 10.0
            else:
                ''' two digits of millis seconds '''
                DecimalValue += (float(TenthOfSecondsValue)/float(3600.0)) / 100.0
                    
            DecimalValue = coeff * DecimalValue
        else:
            raise ValueError ('unexpected Degrees Minutes Seconds format')
    else:
        raise ValueError ('unexpected Degrees Minutes Seconds format')

    #print "DegreeMinuteSecond= ", DegreeMinuteSecond, " DecimalValue= ", DecimalValue
    return DecimalValue


class WayPointsDatabase(object):
    WayPointsDict = {}
    ColumnNames = []
    className = ''
    
    def __init__(self):
        self.className = self.__class__.__name__
        
        self.FilePath = 'WayPoints.xls'
            
        self.FilesFolder = os.getcwd()
        if not('Home' in self.FilesFolder) and not('Environment' in self.FilesFolder):
            self.FilesFolder += os.path.sep + 'Home' + os.path.sep + 'Environment'
        else:
            self.FilesFolder += os.path.sep + '..' +  os.path.sep + 'Environment'

        print self.className + ': file folder= {0}'.format(self.FilesFolder)
        self.FilePath = os.path.abspath(self.FilesFolder+ os.path.sep + self.FilePath)
        print self.className + ': file path= {0}'.format(self.FilePath)

        self.WayPointsDict = {}
        self.ColumnNames = {}

    
    def read(self):
        assert len(self.FilePath)>0
        self.book = open_workbook(self.FilePath)
        ''' assert there is only one sheet '''
        sheet = self.book.sheet_by_name('WayPoints')
        for row in range(sheet.nrows): 
            rowValues = sheet.row_values(row, start_colx=0, end_colx=sheet.ncols)
            # Print the values of the row formatted to 10 characters wide
            if row == 0:
                self.ColumnNames = {}
                index = 0
                for column in rowValues:
                    if column not in fieldNames:
                        print self.className + ': ERROR - expected waypoints column name= {0} not in field names'.format(column)
                        return False
                    else:
                        self.ColumnNames[column] = index
                    index += 1
            else:
                WayPointName = str(rowValues[0]).strip().upper()
                if not(WayPointName in self.WayPointsDict.keys()):
                
                    wayPointDict = {}
                    for column in self.ColumnNames:
                        if column == 'Latitude' or column == 'Longitude':
                            ''' replace degree character '''
                            strLatLong = unicode(rowValues[self.ColumnNames[column]]).strip()
                            if u'°' in strLatLong:
                                strLatLong = unicode(strLatLong).replace(u'°','-')
                                strLatLong = strLatLong.encode('ascii', 'ignore')
    
                            strLatLong = str(strLatLong).strip().replace(u"'", u'-').replace(u' ',u'').replace(u'"',u'')
                            #print 'lat-long= '+ strLatLong
                            wayPointDict[column] = convertDegreeMinuteSecondToDecimal(strLatLong)
    
                        else:
                            wayPointDict[column] = str(rowValues[self.ColumnNames[column]]).strip()
    
                    ''' create a way point '''    
                    wayPoint = WayPoint(wayPointDict['WayPoint'],
                                        wayPointDict['Latitude'],
                                        wayPointDict['Longitude'])
                    self.WayPointsDict[WayPointName] = wayPoint
        return True

    
    def getWayPoint(self, Name):
        assert isinstance(Name, (str, unicode)) and len(Name)>0
        if str(Name).upper() in self.WayPointsDict.keys():
            return self.WayPointsDict[str(Name).upper()]
        else:
            print self.className + ': WARNING - way point= {0} not in the database !!!'.format(str(Name).upper())
            return None
    
    
    def hasWayPoint(self, Name):
        assert isinstance(Name, (str, unicode)) and len(Name)>0
        return self.WayPointsDict.has_key(str(Name).upper().strip())

    
    def getWayPoints(self):
        ''' Iterator '''
        for key in self.WayPointsDict.keys():
            yield self.WayPointsDict[key]


    def insertWayPoint(self, wayPointName, Latitude, Longitude):
        
        assert isinstance(wayPointName, (str, unicode)) and len(wayPointName)>0
        assert isinstance(Latitude, (str, unicode)) and len(Latitude)>0
        assert isinstance(Longitude, (str, unicode)) and len(Longitude)>0
        
        ''' re open the work book '''
        self.WayPointsDict.clear()
        readStatus = self.read()
        sheet = self.book.sheet_by_name('WayPoints')

        ''' read it again '''
        if readStatus and not(self.hasWayPoint(wayPointName)):
            ''' new workbook from scratch '''
            writableBook = Workbook()
            
            ''' Create the target worksheet and name it '''
            writableSheet = writableBook.add_sheet(sheet.name) 
     
            '''  Get number of rows and columns that contain data '''
            numRow = sheet.nrows 
            numCol = sheet.ncols 

            for row in xrange(numRow): 
                '''  Get all the rows in the sheet (each rows is a list) ''' 
                rowList = sheet.row_values(row) 
                for col in xrange(numCol): 
                    '''  Get all the values in each list ''' 
                    oneValue = rowList[col] 
                    '''  Copy the values to target worksheet ''' 
                    writableSheet.write(row, col, oneValue) 
            
            #print self.className + ' - sheet= {0} - number of rows= {1}'.format(writableSheet.get_name(), len(writableSheet.get_rows()))
            writableSheet.write(numRow , 0, wayPointName)
            writableSheet.write(numRow , 1, 'SomeWhere')
            writableSheet.write(numRow , 2, 'waypoint')
            writableSheet.write(numRow , 3, unicode(Latitude) )
            writableSheet.write(numRow , 4, unicode(Longitude) )
            
            writableBook.save(self.FilePath)
            return True
        return False


    def getNumberOfWayPoints(self):
        assert not(self.book is None)
        sheet = self.book.sheet_by_index(0)
        lastRow = sheet.nrows 
        return lastRow
    
class Test_Main(unittest.TestCase):

    def test_main(self):
    
        print '==================== Way-Points ===================='
        wayPointsDb = WayPointsDatabase()
        self.assertTrue( wayPointsDb.read() , 'way points DB correctly read')
            
        TOU = wayPointsDb.getWayPoint('tou')
        print TOU
        
        TouLatDegrees = TOU.getLatitudeDegrees()
        print 'TOU latitude= {0} degrees'.format(TouLatDegrees)
        print '==================== Way-Points ===================='
        for wayPoint in wayPointsDb.getWayPoints():
            print wayPoint
        print '==================== Way-Points ===================='
        NOT_EXISTING = wayPointsDb.getWayPoint('doesnotexist')
        print NOT_EXISTING
        
        print 'number of wayPoints= {0}'.format(wayPointsDb.getNumberOfWayPoints())
        ret = wayPointsDb.insertWayPoint('VALEK', u"N31°40'58.50" + '"', u"N31°40'58.50" + '"')
        if wayPointsDb.hasWayPoint('VALEK'):
            self.assertFalse(ret, 'insertion not done')
        else:
            self.assertTrue(ret, 'insertion correct')
    
        print 'number of wayPoints= {0}'.format(wayPointsDb.getNumberOfWayPoints())
    
    
if __name__ == '__main__':
    unittest.main()