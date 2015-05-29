# -*- coding: UTF-8 -*-
'''
@since: Created on Dec 19, 2014

@author: Robert PASTOR


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

creates an xlsx output file with 
 1) WayPoint Latitude 
 2) Longitude 
 3) and altitude above sea level in meters
 
'''
import os
import xlsxwriter

Meter2Feet = 3.2808399 # feet (3 feet 3⅜ inches)
Meter2NauticalMiles = 0.000539956803 # nautical miles

class GroundTrackOutput(object):
    
    Headers = ['Elapsed Time Seconds', 
               'Way Point',
               
               'longitude-degrees', 
               'latitude-degrees' , 
               
               'altitude-meters',
               'altitude-feet',
               'delta-distance-meters',
               'delta-distance-nautic',
               'cumulated-distance-nautic',
               'course-angle-degrees']
    RowIndex = 0
    fileName = ''
    
    def __init__(self, fileName='Test', sheetName='Results'):
        self.className = self.__class__.__name__
        self.RowIndex = 0
        
        self.fileName = str(fileName).replace('/', '-')
        ''' all output files redirected in a specific folder '''
        self.filePath =  self.fileName
        
        if not('Home' in os.getcwd()):
            self.FilesFolder = os.path.abspath(os.getcwd() + os.path.sep + 'Home' + os.path.sep + 'ResultsFiles' )
        else:
            self.FilesFolder = os.path.abspath(os.getcwd() + os.path.sep + '..' + os.path.sep + 'ResultsFiles' )

        self.filePath = self.FilesFolder + os.path.sep + self.filePath
        self.workbook = xlsxwriter.Workbook(self.filePath)
        self.worksheet = self.workbook.add_worksheet(sheetName)

    def writeHeaders(self):
        self.RowIndex = 0
        ColumnIndex = 0
        for header in self.Headers:
            self.worksheet.write(self.RowIndex,ColumnIndex, header)
            ColumnIndex = ColumnIndex + 1
        
        self.RowIndex += 1
        
    def write(self, ElapsedTimeSeconds, 
              WayPointName,
              
              LongitudeDegrees,
              LatitudeDegrees, 
              
              AltitudeAboveSeaLevelMeters,
              deltaDistanceMeters,
              cumulatedDistanceMeters,
              courseAngleDegrees
              ):
        
        assert isinstance(LongitudeDegrees, float)
        assert isinstance(LatitudeDegrees, float)
        assert isinstance(AltitudeAboveSeaLevelMeters, float)
        
        ColumnIndex = 0
        self.worksheet.write(self.RowIndex, ColumnIndex, ElapsedTimeSeconds)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, WayPointName)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, LongitudeDegrees )
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, LatitudeDegrees)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, AltitudeAboveSeaLevelMeters )
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, AltitudeAboveSeaLevelMeters * Meter2Feet)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, deltaDistanceMeters)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, deltaDistanceMeters * Meter2NauticalMiles)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, cumulatedDistanceMeters * Meter2NauticalMiles)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, courseAngleDegrees )
        
        # next row
        self.RowIndex += 1
    
    def close(self):
        self.workbook.close()