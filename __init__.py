def name():
  return "CSV2Points"

def description():
  return "This plugin has no real use."

def category():
    return "Vector"

def version():
  return "Version 0.9"

def qgisMinimumVersion():
  return "2.0"

def authorName():
  return "Alexander Lisovenko"

def classFactory(iface):
  from csv2points import Csv2PointsPlugin
  return Csv2PointsPlugin(iface)
