'''
Created on Mar 31, 2015

@author: t0007330
'''
import unittest
import os
from Home.xlrd import open_workbook

class Test_xlrd(unittest.TestCase):

    def test_xlrd(self):

        WayPointsDict = {}
        ColumnNames = []
        
        fileName = 'WayPoints.xls'
        if ('FlightDynamics' in os.getcwd()) and not('Home' in os.getcwd()):
            fileName = os.getcwd() + os.path.sep + 'Home' + os.path.sep + 'xlrd' + os.path.sep + 'tests' + os.path.sep + fileName
        else:
            ''' case when the run is launched from Home '''
            fileName = os.getcwd() + os.path.sep + fileName

        print 'file name= {0}'.format(fileName)
        book = open_workbook(fileName)
        sheet = book.sheet_by_index(0)
        for row in range(sheet.nrows): 
            rowValues = sheet.row_values(row, start_colx=0, end_colx=sheet.ncols)
            # Print the values of the row formatted to 10 characters wide
            if row == 0:
                ColumnNames = list(rowValues)
                print ColumnNames
            else:
                if rowValues[0] in WayPointsDict.keys():
                    raise ValueError ('key- {0} already existing'.format(rowValues[0]))
                WayPointsDict[rowValues[0]] = rowValues
                
            print  tuple(rowValues)
        print '==================='
        print ColumnNames
        print '==================='
        self.assertTrue(len(WayPointsDict)>0)
        for key in WayPointsDict.keys():
            print key, WayPointsDict[key]


if __name__ == '__main__':
    unittest.main()