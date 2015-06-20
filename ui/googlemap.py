"""
Helper functions for ui.py
these functions generate the map image and directions xml text.
Save them in the local directory
API keys generated from Google API
"""

from geoip import geolite2
import urllib
from PIL import Image, ImageTk
import re
# https://pypi.python.org/pypi/google.directions

def makeMap(inputCoordinates):
    # given our location and input restaurant coordinates, make a map
    # save it as 'map.jpg'
    # use urllib to get the html file from the web
    API_KEY = 'AIzaSyBISQOWUrYa5SDzjUhNxMl-_kCB-pIIt-A'
    myLocation = geolite2.lookup_mine()
    myCoordinates = myLocation.location
    myCoordinates = str(myCoordinates).strip('()').replace(' ', '')
    inputCoordinates = str(inputCoordinates).strip('[]').replace(' ', '')
    dimensions = '200x200'
    url = ('https://maps.googleapis.com/maps/api/staticmap?center=' + 
           myCoordinates + '&zoom=11&size=' + dimensions + '&key=' + API_KEY + 
           '&path=color:0xff0000ff|weight:5|' + myCoordinates + '|' + 
           inputCoordinates + '&markers=color:red|' + myCoordinates + '|' + 
           inputCoordinates)
    #print url
    urllib.urlretrieve(url, 'map.jpg')

def directions(inputCoordinates):
    # get the directions from you to restaurant
    API_KEY = 'AIzaSyDSEAMt4OtBixRhTtgWMC2wkM5ZByFyT78'
    myLocation = geolite2.lookup_mine()
    myCoordinates = myLocation.location
    myCoordinates = str(myCoordinates).strip('()').replace(' ', '')
    inputCoordinates = str(inputCoordinates).strip('[]').replace(' ', '')
    url = ('https://maps.googleapis.com/maps/api/directions/xml?origin=' + 
            myCoordinates + '&destination=' + inputCoordinates + '&key=' + 
            API_KEY)
    urllib.urlretrieve(url, 'directions.txt')

def searchDirections():
    # clean up the directions output
    # it's saved as an xml file, so we need to clean out all the non-text
    # elements
    lines = []
    searchfile = open("directions.txt", "r")
    for line in searchfile:
        if "html_instructions" in line:
            lines.append(line)
    searchfile.close()
    cleaned = []
    for line in lines:
        # these are all non-text elements that should be removed
        clean = line.replace('<html_instructions>', '')
        clean = clean.replace('</html_instructions>', '')
        clean = clean.replace('&', '')
        clean = clean.replace('lt;', '')
        clean = clean.replace('/bgt', '')
        clean = clean.replace('bgt;', '')
        clean = clean.replace(';', '')
        clean = clean.replace('style=quotfont-size:0.9emquotgt', '')
        clean = clean.replace('/divgt', '')
        clean = clean.replace('div', '')
        clean = clean.replace('  ', '')
        cleaned.append(clean)
    return cleaned