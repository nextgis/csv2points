# -*- coding: utf-8 -*-

import csv, os

from PyQt4 import QtCore, QtGui

from qgis.core import *
from qgis.gui import *

from csv2points_dialog_view import Ui_Dialog
from csv2points_model import Csv2pointsModel, recalculateCoordinates

class Csv2pointsDialog( QtGui.QDialog, Ui_Dialog ):
    def __init__( self ):
        QtGui.QDialog.__init__( self )
        self.setupUi( self )

        self.__model = Csv2pointsModel();
        self.__model.subscribToModelChange(self.onUpdateModel)

        QtCore.QObject.connect( self.selectCSVFileButton, QtCore.SIGNAL( "clicked()" ), self.selectCSVFile )
        QtCore.QObject.connect( self.selectSHPFileButton, QtCore.SIGNAL( "clicked()" ), self.selectSHPFile )

        QtCore.QObject.connect(self.delimiterTabRadioButton, QtCore.SIGNAL( "clicked()" ), self.checkTabDelimiter )
        QtCore.QObject.connect(self.delimiterSpaceRadioButton, QtCore.SIGNAL( "clicked()" ), self.checkSpaceDelimiter )
        QtCore.QObject.connect(self.delimiterCommaRadioButton, QtCore.SIGNAL( "clicked()" ), self.checkCommaDelimiter )
        QtCore.QObject.connect(self.delimiterSemicolonRadioButton, QtCore.SIGNAL( "clicked()" ), self.checkSemicolonDelimiter )
        QtCore.QObject.connect(self.delimiterColonRadioButton, QtCore.SIGNAL( "clicked()" ), self.checkColonDelimiter )

    def checkTabDelimiter(self):
        self.__model.csvDelimiter = "\t"

    def checkSpaceDelimiter(self):
        self.__model.csvDelimiter = " "

    def checkCommaDelimiter(self):
        self.__model.csvDelimiter = ","

    def checkSemicolonDelimiter(self):
        self.__model.csvDelimiter = ";"

    def checkColonDelimiter(self):
        self.__model.csvDelimiter = ":"

    def accept( self ):
        if self.__model.shpFileInfo[0] == None:
            QtGui.QMessageBox.warning(self,
                                self.tr("File is not specified."),
                                self.tr("Please choose shape.")
                               )
            return

        outFile = QtCore.QFile( self.__model.shpFileInfo[0] )
        if outFile.exists():
            if not QgsVectorFileWriter.deleteShapeFile( self.__model.shpFileInfo[0] ):
                QtGui.QMessageBox.warning( self, self.tr("Delete error"), self.tr("Can't delete file: " + self.__model.shpFileInfo[0] ) )
                return

        xAttrIndex = self.attrXCoordComboBox.currentIndex()
        yAttrIndex = self.attrYCoordComboBox.currentIndex()
        azAttrIndex = self.attrAzCoordComboBox.currentIndex()
        distAttrIndex = self.attrDistCoordComboBox.currentIndex()

        geoDataAttributes = self.__model.getGeoDataAttributes(xAttrIndex, yAttrIndex, azAttrIndex, distAttrIndex)

        shapeFields = QgsFields()
        for  attrName in geoDataAttributes.values():
            shapeFields.append(QgsField(attrName, QtCore.QVariant.String, u"", 255))

        crs = QgsCoordinateReferenceSystem( 4326 )

        shapeFileWriter = QgsVectorFileWriter( self.__model.shpFileInfo[0], self.__model.shpFileInfo[1], shapeFields, QGis.WKBPoint, crs )

        skipAllBadPointFlag = False
        for (coord, displacement, attributes) in self.__model.getGeoDataIterator(xAttrIndex, yAttrIndex, azAttrIndex, distAttrIndex):
            try:
                (x,y) = recalculateCoordinates(
                                        map(lambda x: float(x), coord),
                                        map(lambda x: float(x), displacement))
                feature = QgsFeature()
                feature.initAttributes(geoDataAttributes.__len__())

                geometry = QgsGeometry()
                point = QgsPoint( x, y )
                feature.setGeometry( geometry.fromPoint( point ) )


                for attrCounter in range(geoDataAttributes.__len__()):
                    feature.setAttribute(attrCounter, attributes[attrCounter])

                shapeFileWriter.addFeature( feature )

            except ValueError as ex:
                if skipAllBadPointFlag == False:
                    msgBox = QtGui.QMessageBox(self)
                    msgBox.setWindowTitle(self.tr("Wrong attribute type"))
                    msgBox.setText("Point has incorrect attribute type. Poit's attributes: " + str(coord) + str(displacement))
                    ignorethisButton = msgBox.addButton(self.tr("Ignore this"), QtGui.QMessageBox.ActionRole)
                    ignoreallButton = msgBox.addButton(self.tr("Ignore all"), QtGui.QMessageBox.ActionRole)
                    msgBox.exec_()
                    if (msgBox.clickedButton() == ignorethisButton):
                        pass
                    elif (msgBox.clickedButton() == ignoreallButton):
                        skipAllBadPointFlag = True
                else:
                    pass

        del shapeFileWriter

        newLayer = QgsVectorLayer(self.__model.shpFileInfo[0], QtCore.QFileInfo( self.__model.shpFileInfo[0] ).baseName(), "ogr" )
        QgsMapLayerRegistry.instance().addMapLayer( newLayer )

        self.close()

    def selectCSVFile(self):
        csvFilter = u"CSV files (*.csv *.CSV)";
        fileDialog = QgsEncodingFileDialog( self, self.tr( "Select input csv file" ), u"", csvFilter, u"")
        fileDialog.setDefaultSuffix( u"csv" )
        fileDialog.setFileMode( QtGui.QFileDialog.AnyFile )

        if not fileDialog.exec_() == QtGui.QDialog.Accepted:
            return

        self.__model.csvFilePath = unicode( QtCore.QFileInfo( fileDialog.selectedFiles()[0] ).absoluteFilePath() )


        self.groupBox.setEnabled(True)
        self.groupBox_2.setEnabled(True)
        self.groupBox_3.setEnabled(True)

    def selectSHPFile(self):
        shpFilter = u"Shapefiles (*.shp *.SHP)";
        fileDialog = QgsEncodingFileDialog( self, self.tr( "Select output shapefile" ), u"", shpFilter, u"" )
        fileDialog.setDefaultSuffix( u"shp" )
        fileDialog.setFileMode( QtGui.QFileDialog.AnyFile )
        fileDialog.setAcceptMode( QtGui.QFileDialog.AcceptSave )
        fileDialog.setConfirmOverwrite( True )

        if not fileDialog.exec_() == QtGui.QDialog.Accepted:
            return

        self.__model.shpFileInfo = (fileDialog.selectedFiles()[0], fileDialog.encoding())

        self.shpFileEdit.setText( self.__model.shpFileInfo[0] )

    def onUpdateModel(self):
        print "onUpdateModel"
        self.csvFileEdit.setText(self.__model.csvFilePath)

        if (self.__model.csvDelimiter == "\t"):
            self.delimiterTabRadioButton.setChecked(True)
        elif (self.__model.csvDelimiter == " "):
            self.delimiterSpaceRadioButton.setChecked(True)
        elif (self.__model.csvDelimiter == ","):
            self.delimiterCommaRadioButton.setChecked(True)
        elif (self.__model.csvDelimiter == ";"):
            self.delimiterSemicolonRadioButton.setChecked(True)
        elif (self.__model.csvDelimiter == ":"):
            self.delimiterColonRadioButton.setChecked(True)

        self.tableWidget.clear()
        self.attrXCoordComboBox.clear()
        self.attrYCoordComboBox.clear()
        self.attrAzCoordComboBox.clear()
        self.attrDistCoordComboBox.clear()

        csvAttrCount = self.__model.csvHeader.__len__()

        self.tableWidget.setColumnCount(csvAttrCount)

        listOfLables = [lable for lable in self.__model.csvHeader]
        self.tableWidget.setHorizontalHeaderLabels ( listOfLables)

        self.attrXCoordComboBox.insertItems ( 0, listOfLables )
        self.attrYCoordComboBox.insertItems ( 0, listOfLables )
        self.attrAzCoordComboBox.insertItems ( 0, listOfLables )
        self.attrDistCoordComboBox.insertItems ( 0, listOfLables )

        previewNumOfDataRows = 2
        if self.__model.csvDataLineNum < previewNumOfDataRows:
          previewNumOfDataRows =  self.__model.csvDataLineNum
          
        self.tableWidget.setRowCount(previewNumOfDataRows)
        for rowCounter in range(previewNumOfDataRows):
            dataRow = self.__model.csvDataIterator.next()
            for colCounter in range(self.__model.csvHeader.__len__()):
                self.tableWidget.setItem(rowCounter, colCounter, QtGui.QTableWidgetItem(dataRow[colCounter]) )

