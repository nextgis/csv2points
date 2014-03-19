# -*- coding: utf-8 -*-

import csv, os, copy

def recalculateCoordinates( (long,lat), (azGrad, dist) ):
    from math import cos, sin, acos, pi, asin, atan2

    #rad - радиус сферы (Земли)
    rad = 6372795.0

    azRadians = pi * azGrad / 180

    ilat = (180/pi) * asin( sin(lat*pi/180)*cos(dist/rad) + cos(lat*pi/180)*sin(dist/rad)*cos(azRadians) )

    ilong = long + asin(sin(azRadians) * sin(dist/rad) / cos(ilat*pi/180)) * 180/pi

    return (ilong, ilat)

class Csv2pointsModel(object):
    def __init__(self, ):
        self.__csvFilePath = None
        self.__csvDelimiter = "\t"

        self.__shpFilePath = None
        self.__shpFileEncoding = None

        self.__csvHeader = []
        self.__csvDataLineNum = 0
        self.__csvDataIterator = None

        self.__csvfile = None
        self.__csvfilereader = None

    def __del__(self):
        self.__csvfile.close()

    @property
    def csvFilePath(self):
        return self.__csvFilePath

    @csvFilePath.setter
    def csvFilePath(self, filePath):
        self.__csvFilePath = filePath
        self.__csvFileProcessing()
        self.modelChange()

    @property
    def csvDelimiter(self):
        return self.__csvDelimiter

    @csvDelimiter.setter
    def csvDelimiter(self, delimiter):
        self.__csvDelimiter = delimiter
        self.__csvFileProcessing()
        self.modelChange()

    @property
    def shpFileInfo(self):
        return (self.__shpFilePath, self.__shpFileEncoding)

    @shpFileInfo.setter
    def shpFileInfo(self, (filePath, Encoding)):
        (self.__shpFilePath, self.__shpFileEncoding) = (filePath, Encoding)
        #self.modelChange()

    @property
    def csvDataLineNum(self):
        return self.__csvDataLineNum

    @property
    def csvHeader(self):
        return self.__csvHeader

    @property
    def csvDataIterator(self):
        return self.__csvDataIterator

    def __csvFileProcessing(self):
        if (self.__csvfile != None):
            self.__csvfile.close()
        self.__csvfile = open( os.path.abspath(self.__csvFilePath) )
        self.__csvfilereader = csv.reader( self.__csvfile, delimiter=self.__csvDelimiter )

        self.__csvHeader = self.__csvfilereader.next()
        self.__csvDataLineNum = self.__csvfilereader.line_num
        print self.__csvDataLineNum

        self.__csvDataIterator = self.__createCSVDataIterator(self.__csvfilereader)

    def __createCSVDataIterator(self, csvfilereader):
        for data in csvfilereader:
                yield data

    def getGeoDataAttributes(self, xAttrIndex, yAttrIndex, azAttrIndex, distAttrIndex):
        #attributesIndexes = list(set(range(self.__csvHeader.__len__())) ^ set([xAttrIndex, yAttrIndex, azAttrIndex, distAttrIndex]))
        attributesIndexes = list(set(range(self.__csvHeader.__len__())) ^ set([]))
        return dict(zip(attributesIndexes,  [ self.__csvHeader[attrIndex] for attrIndex in attributesIndexes]))

    def getGeoDataIterator(self, xAttrIndex, yAttrIndex, azAttrIndex, distAttrIndex):
        self.__csvFileProcessing()
        for data in self.__csvfilereader:
            attributesIndexes = self.getGeoDataAttributes(xAttrIndex, yAttrIndex, azAttrIndex, distAttrIndex).keys()
            attributes = [data[attrIndex] for attrIndex in attributesIndexes]

            yield ((data[xAttrIndex],data[yAttrIndex]), (data[azAttrIndex],data[distAttrIndex]), attributes)

    def subscribToModelChange(self, func):
        self.__observFunc = func

    def modelChange(self):
        self.__observFunc()

if __name__ == '__main__':
    (long,lat) = (53.89045716729015, 27.555393604561687)

    print recalculateCoordinates( (long,lat), (0, 100) )
    print recalculateCoordinates( (long,lat), (90, 100) )

