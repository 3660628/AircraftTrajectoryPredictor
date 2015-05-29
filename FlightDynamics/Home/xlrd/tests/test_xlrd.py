'''
Created on Mar 31, 2015

@author: t0007330
'''
from Home.xlrd import open_workbook

if __name__ == "__main__":

    WayPointsDict = {}
    ColumnNames = []
    
    fileName = 'WayPoints.xls'
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
    for key in WayPointsDict.keys():
        print key, WayPointsDict[key]
