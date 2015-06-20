"""
Find the location of the user (state, latitude/longitude, city)
We use this to target the recommendation to the user's area

from terminal: 
pip install python-geoip
pip install python-geoip-geolite2

We have data on six cities in the United States:
Pittsburgh, Charlotte, Urbana-Champaign, Phoenix, Las Vegas, Madison

We need to know their coordinates, since we want to only recommend
restaurants to users in the city they are closest to.
"""

from geoip import geolite2

# Sample code:
# location = geolite2.lookup_mine()
# location now has dot attributes like ip, country, state, and coordinates

def distance(a, b):
    # basic math distance formula
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

def findClosestCity(cities, user=""):
    if not user: user = geolite2.lookup_mine().location
    # use a distance function to find closest city
    for index, city in enumerate(cities):
        dist = distance(user, city[1:])
        if index == 0 or dist < closest[1]:
            closest = (city[0], dist)
    city = closest[0]
    return city

def testFindClosestCity():
    print 'testing findClosestCity...',
    # (Latitude, Longitude)
    pittsburgh = ('pittsburgh', 40.4397, 79.9764)
    charlotte = ('charlotte', 35.2269, 80.8433)
    urbana = ('urbana', 40.1150, 88.2728)
    phoenix = ('phoenix', 33.4500, 112.0667)
    vegas = ('vegas', 36.1215, 115.1739)
    madison = ('madison', 43.0667, 89.4000)
    # only works if run from pittsburgh area
    assert(findClosestCity([pittsburgh, charlotte, urbana, phoenix, vegas, 
           madison]) == 'pittsburgh')
    assert(findClosestCity([pittsburgh, charlotte, urbana, phoenix, vegas, 
           madison], (36.1215, 115.1739)) == 'vegas')
    print "passed!"

if __name__ == '__main__':
    testFindClosestCity()

