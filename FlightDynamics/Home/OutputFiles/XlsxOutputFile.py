'''
Created on 12 juil. 2014


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
        
@note:  create an Xlsx file

'''
import xlsxwriter
import os
from datetime import datetime
import unittest


class XlsxOutput():
    

    FileName = ""
    workbook = None
    worksheet = None
    RowIndex = 0
    
    def __init__(self, 
                 fileName, 
                 sheetName="Results"):
        
        self.className = self.__class__.__name__
        self.RowIndex = 0
        
        self.filePath = fileName
        
        self.FilesFolder = os.getcwd()
        if not('Home' in self.FilesFolder):
            self.FilesFolder = os.path.abspath(os.getcwd() + os.path.sep + 'Home' + os.path.sep + 'ResultsFiles')
        else:
            ''' case when the run is launched from Home/Tests '''
            self.FilesFolder = os.path.abspath(os.getcwd() + os.path.sep  + '..' + os.path.sep  + 'ResultsFiles')

        
        print self.className + ': file folder= {0}'.format(self.FilesFolder)
        self.filePath = os.path.abspath(self.FilesFolder+ os.path.sep + self.filePath)
        print self.className + ': file path= {0}'.format(self.filePath)

        self.filePath = self.filePath + '-{0}.xlsx'.format(datetime.now().strftime("%d-%b-%Y-%Hh%Mm%S"))
        print self.className + ': file path= {0}'.format(self.filePath)

        self.workbook = xlsxwriter.Workbook(self.filePath)
        self.worksheet = self.workbook.add_worksheet(sheetName)

    def writeHeaders(self, Headers):
        
        assert isinstance(Headers, list)
        self.RowIndex = 0
        ColumnIndex = 0
        for header in Headers:
            self.worksheet.write(self.RowIndex, ColumnIndex, header)
            ColumnIndex = ColumnIndex + 1
        
        self.RowIndex += 1
    
    def writeOneFloatValue(self,
                         time,
                         floatValue ):
        ColumnIndex = 0
        self.worksheet.write(self.RowIndex, ColumnIndex, time)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, floatValue)        
        self.RowIndex += 1
        
        
    def writeTwoFloatValues(self,
                        time,
                        firstFloatValue,
                        secondFloatValue):
        
        ColumnIndex = 0
        self.worksheet.write(self.RowIndex, ColumnIndex, time)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, firstFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, secondFloatValue)        
        self.RowIndex += 1
        
        
    def writeFourFloatValues(self, time,
                            firstFloatValue,
                            secondFloatValue,
                            thirdFloatValue,
                            fourthFloatValue):
        
        ColumnIndex = 0
        self.worksheet.write(self.RowIndex, ColumnIndex, time)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, firstFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, secondFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, thirdFloatValue)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, fourthFloatValue)        
        self.RowIndex += 1


    def writeSixFloatValues(self, time,
                            firstFloatValue, secondFloatValue, thirdFloatValue,
                            fourthFloatValue, fifthFloatValue, sixthFloatValue):
        
        ColumnIndex = 0
        self.worksheet.write(self.RowIndex, ColumnIndex, time)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, firstFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, secondFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, thirdFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, fourthFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, fifthFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, sixthFloatValue)        
        self.RowIndex += 1


    def writeSevenFloatValues(self, time,
                            firstFloatValue, secondFloatValue, thirdFloatValue,
                            fourthFloatValue, fifthFloatValue, sixthFloatValue, seventhFloatValue):
        
        ColumnIndex = 0
        self.worksheet.write(self.RowIndex, ColumnIndex, time)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, firstFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, secondFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, thirdFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, fourthFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, fifthFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, sixthFloatValue)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, seventhFloatValue)        
        self.RowIndex += 1
        
    def writeNineFloatValues(self, elapsedTimeSeconds,
                            firstFloatValue, secondFloatValue, thirdFloatValue,
                            fourthFloatValue, fifthFloatValue, sixthFloatValue, 
                            seventhFloatValue, eighthFloatValue, ninethFloatValue):
        
        ColumnIndex = 0
        self.worksheet.write(self.RowIndex, ColumnIndex, elapsedTimeSeconds)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, firstFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, secondFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, thirdFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, fourthFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, fifthFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, sixthFloatValue)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, seventhFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, eighthFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, ninethFloatValue)        
        self.RowIndex += 1

    def writeTenFloatValues(self, elapsedTimeSeconds,
                            firstFloatValue, secondFloatValue, thirdFloatValue,
                            fourthFloatValue, fifthFloatValue, sixthFloatValue, 
                            seventhFloatValue, eighthFloatValue, ninethFloatValue,
                            tenthFloatValue):
        
        ColumnIndex = 0
        self.worksheet.write(self.RowIndex, ColumnIndex, elapsedTimeSeconds)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, firstFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, secondFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, thirdFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, fourthFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, fifthFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, sixthFloatValue)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, seventhFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, eighthFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, ninethFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, tenthFloatValue)        
        self.RowIndex += 1
        
    def writeElevenFloatValues(self, elapsedTimeSeconds,
                            firstFloatValue, secondFloatValue, thirdFloatValue,
                            fourthFloatValue, fifthFloatValue, sixthFloatValue, 
                            seventhFloatValue, eighthFloatValue, ninethFloatValue,
                            tenthFloatValue, EleventhFloatValue):
        
        ColumnIndex = 0
        self.worksheet.write(self.RowIndex, ColumnIndex, elapsedTimeSeconds)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, firstFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, secondFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, thirdFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, fourthFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, fifthFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, sixthFloatValue)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, seventhFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, eighthFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, ninethFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, tenthFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, EleventhFloatValue)        
        self.RowIndex += 1    
        
    def writeFifteenFloatValues(self, elapsedTimeSeconds,
                            firstFloatValue, secondFloatValue, thirdFloatValue,
                            fourthFloatValue, fifthFloatValue, sixthFloatValue, 
                            seventhFloatValue, eighthFloatValue, ninethFloatValue,
                            tenthFloatValue, eleventhFloatValue,
                            twelvethFloatValue, thirdteenFloatValue, fourteenFloatValue , fifteenFloatValue):
        
        ColumnIndex = 0
        self.worksheet.write(self.RowIndex, ColumnIndex, elapsedTimeSeconds)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, firstFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, secondFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, thirdFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, fourthFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, fifthFloatValue)                
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, sixthFloatValue)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, seventhFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, eighthFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, ninethFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, tenthFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, eleventhFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, twelvethFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, thirdteenFloatValue)        
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, fourteenFloatValue)
        ColumnIndex += 1
        self.worksheet.write(self.RowIndex, ColumnIndex, fifteenFloatValue)        
        self.RowIndex += 1    
                                
    
    def close(self):
        self.workbook.close()
    
    
class Test_XlsxOutputFile(unittest.TestCase):

    def test_main(self):
        xlsxOutput = XlsxOutput(fileName = 'Xlsx-Output-tests', sheetName="Results")
        Headers = ['One', 'Two', 'Three']
        xlsxOutput.writeHeaders(Headers)
        xlsxOutput.writeTwoFloatValues(time=1.1,
                        firstFloatValue = 9.9,
                        secondFloatValue = 8.8)
        xlsxOutput.close()
        
if __name__ == '__main__':
    unittest.main()
        