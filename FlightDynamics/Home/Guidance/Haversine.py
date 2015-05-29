# -*- coding: UTF-8 -*-

"""
  Python implementation of Haversine formula
  Copyright (C) <2009>  Bartek G�rny <bartek@gorny.edu.pl>

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import math
Meter2NauticalMiles = 0.000539956803

def LatitudeLongitudeAtDistanceBearing(StartLatitudeLongitudeDegrees, DistanceMeters, BearingDegrees):
    '''
    compute latitude and longitude of a point at a given distance and on a radial from a given point
    
    Destination point given distance and bearing from start point
    Given a start point, initial bearing, and distance, 
    this will calculate the destination point 
    and final bearing travelling along a (shortest distance) great circle arc.
    '''
    assert (isinstance(StartLatitudeLongitudeDegrees, list)) and (len(StartLatitudeLongitudeDegrees) == 2)
    
    assert (isinstance(StartLatitudeLongitudeDegrees[0], float))
    startLatitudeDegrees = StartLatitudeLongitudeDegrees[0]
    assert (startLatitudeDegrees <= 90.0) and (-90.0 <= startLatitudeDegrees)
        
    assert (isinstance(StartLatitudeLongitudeDegrees[1], float))
    startLongitudeDegrees = StartLatitudeLongitudeDegrees[1]
    assert (startLongitudeDegrees <= 180.0) and  (-180.0 <= startLongitudeDegrees)
        
    assert (isinstance(BearingDegrees, float))
    assert (BearingDegrees >= -360.0) and (BearingDegrees <= 360.0)
        
    start_latitude_radians = math.radians(StartLatitudeLongitudeDegrees[0])
    start_longitude_radians = math.radians(StartLatitudeLongitudeDegrees[1])
    bearing_radians = math.radians(BearingDegrees)
        
    '''
        Formula:     φ2 = asin( sin φ1 ⋅ cos δ + cos φ1 ⋅ sin δ ⋅ cos θ )
                    λ2 = λ1 + atan2( sin θ ⋅ sin δ ⋅ cos φ1, cos δ − sin φ1 ⋅ sin φ2 )
            where     φ is latitude, λ is longitude, 
            θ is the bearing (in radians, clockwise from north), 
            δ is the angular distance (in radians) d/R; d being the distance travelled, R the earth’s radius
            JavaScript:     

            var φ2 = Math.asin( Math.sin(φ1)*Math.cos(d/R) +
                    Math.cos(φ1)*Math.sin(d/R)*Math.cos(brng) );
            var λ2 = λ1 + Math.atan2(Math.sin(brng)*Math.sin(d/R)*Math.cos(φ1),
                         Math.cos(d/R)-Math.sin(φ1)*Math.sin(φ2));
                         
    '''
    earthRadiusMeters = 6378135.0 # earth’s radius in meters
    latitudeRadians = math.asin( math.sin(start_latitude_radians) * math.cos(DistanceMeters/earthRadiusMeters) 
                                     + math.cos(start_latitude_radians) * math.sin(DistanceMeters/earthRadiusMeters) * math.cos(bearing_radians)) 
    deltaLon = math.atan2( math.sin(bearing_radians) * math.sin(DistanceMeters/earthRadiusMeters) * math.cos(start_latitude_radians) , 
                               math.cos(DistanceMeters/earthRadiusMeters) - math.sin(start_latitude_radians) * math.sin(latitudeRadians))
    longitudeRadians = math.fmod ( start_longitude_radians + deltaLon + math.pi, 2 * math.pi ) - math.pi
        #longitudeRadians = start_longitude_radians + deltaLon
    latitudeDegrees = math.degrees(latitudeRadians)
    longitudeDegrees = math.degrees(longitudeRadians)
    #longitudeDegrees = math.fmod(longitudeDegrees + 180.0 , 360.0 ) - 180.0
    longitudeDegrees = ((longitudeDegrees + 180) % 360) - 180
        
    assert (latitudeDegrees <= 90.0) and (-90.0 <= latitudeDegrees)
    if (longitudeDegrees > 180.0) or (longitudeDegrees < -180.0):
        assert (longitudeDegrees <= 180.0) and (-180.0 <= longitudeDegrees)
#     if longitudeDegrees > 180.0:
#         longitudeDegrees = math.fmod(longitudeDegrees - 180.0, 360.0) + 180.0
#     if longitudeDegrees < -180.0:
#         longitudeDegrees = math.fmod(360.0 + longitudeDegrees , 360.0)
        
    return latitudeDegrees, longitudeDegrees
    
def points2bearingDegrees (startLatLongDegrees, endLatLongDegrees):
    '''
    In aerial terms, "bearing" means the actual compass direction of the forward course of our aircraft
    
    def calcBearing(lat1, lon1, lat2, lon2):
    dLon = lon2 - lon1
    y = sin(dLon) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon)
    return atan2(y, x)
    '''
    
    assert (isinstance(startLatLongDegrees, list)==True) 
    assert (isinstance(endLatLongDegrees, list)==True) 
    assert (len(startLatLongDegrees) == 2) 
    assert (len(endLatLongDegrees) == 2)
        
    start_latitude = math.radians(startLatLongDegrees[0])
    start_longitude = math.radians(startLatLongDegrees[1])
    end_latitude = math.radians(endLatLongDegrees[0])
    end_longitude = math.radians(endLatLongDegrees[1])
        
    y = math.sin(end_longitude-start_longitude)*math.cos(end_latitude)
    x = math.cos(start_latitude)*math.sin(end_latitude)-math.sin(start_latitude)*math.cos(end_latitude)*math.cos(end_longitude-start_longitude)
    
    bearingRadians = math.atan2(y,x) 
    bearingDegrees = math.degrees(bearingRadians)
    
    ''' bearing in the range 0..360 '''
    bearingDegrees = (bearingDegrees + 360) % 360

    return bearingDegrees


def points2distanceMeters(startLatLongDegrees,  endLatLongDegrees):
    """
    Calculate distance (in kilometers) between two points given as (longitude, latitude) pairs
    based on Haversine formula (http://en.wikipedia.org/wiki/Haversine_formula).
    Implementation inspired by JavaScript implementation from http://www.movable-type.co.uk/scripts/latlong.html
    Accepts coordinates as tuples (deg, min, sec), but coordinates can be given in any form - e.g.
    can specify only minutes:
    (0, 3133.9333, 0) 
    is interpreted as 
    (52.0, 13.0, 55.998000000008687)
    which, not accidentally, is the latitude of Warsaw, Poland.
    """

    assert isinstance(startLatLongDegrees, list) and len(startLatLongDegrees)==2 
    assert isinstance(endLatLongDegrees, list) and len(endLatLongDegrees)==2
        
    start_latitude_radians = math.radians(startLatLongDegrees[0])
    start_longitude_radians = math.radians(startLatLongDegrees[1])
        
    end_latitude_radians = math.radians(endLatLongDegrees[0])
    end_longitude_radians = math.radians(endLatLongDegrees[1])
        
    d_latitude = end_latitude_radians - start_latitude_radians
    d_longitude = end_longitude_radians - start_longitude_radians
    a = math.sin(d_latitude/2) ** 2 + math.cos(start_latitude_radians) * math.cos(end_latitude_radians) * math.sin(d_longitude/2)**2
    c = 2 * math.asin(math.sqrt(a))
        
    radiusMeters = 6378135.0 # earth’s radius in meters
    return radiusMeters * c

def distanceMeters(origin, destination):
    
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6378135.0 # meters

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

if __name__ == '__main__':
    # latitude longitude in degrees
    warsaw = [52.247142, 21.015244]
    cracow = [50.065073, 19.948311]
    
    print '========== distance ====='
    print "distance warsaw-cracow= {0} meters".format( points2distanceMeters(warsaw,  cracow))
    
    Orly = [48.726246, 2.365136]
    Toulouse = [43.629366, 1.367644]
    print "distance orly-toulouse= ", points2distanceMeters(Orly,  Toulouse), " meters"
    print "bearing orly-toulouse= ", points2bearingDegrees(Orly, Toulouse), " degrees"

    seattle = [47.621800, -122.350326]
    olympia = [47.041917, -122.893766]
    print 'distance Seattle Olympia= {0} meters'.format(distanceMeters(seattle, olympia))
    print 'distance Orly Toulouse= {0} meters'.format(distanceMeters(Orly, Toulouse))
    
    print '========== bearing ====='

    London = [ 51.5, 0.0 ]
    Orly = [ 48.726254, 2.365247 ]
    print "bearing London-Orly= ", points2bearingDegrees(London, Orly), " degrees"
    print "bearing Orly-London= ", points2bearingDegrees(Orly, London), " degrees"

    Osaka = [34.785528, 135.438222]
    ColdLake = [54.404999 , -110.279444]

    print "distance Osaka-Cold-Lake= {0} nautics".format( points2distanceMeters(Osaka,  ColdLake) * Meter2NauticalMiles)
    print "distance Cold-Lake-Osaka= {0} nautics".format( points2distanceMeters(ColdLake , Osaka) * Meter2NauticalMiles)

    Mazza = [11.708888888888888, 180.00]
    distanceMeters = 230.710159639
    bearingDegrees = -117.550571114
    print LatitudeLongitudeAtDistanceBearing(Mazza, distanceMeters, bearingDegrees)
#     bearingDegrees = 1.0
#     print LatitudeLongitudeAtDistanceBearing(Mazza, distanceMeters, bearingDegrees)
#     bearingDegrees = 90.0
#     print LatitudeLongitudeAtDistanceBearing(Mazza, distanceMeters, bearingDegrees)
#     bearingDegrees = 180.0
#     print LatitudeLongitudeAtDistanceBearing(Mazza, distanceMeters, bearingDegrees)
#     bearingDegrees = 270.0
#     print LatitudeLongitudeAtDistanceBearing(Mazza, distanceMeters, bearingDegrees)
#     bearingDegrees = 360.0
#     print LatitudeLongitudeAtDistanceBearing(Mazza, distanceMeters, bearingDegrees)
#     bearingDegrees = -1.0
#     print LatitudeLongitudeAtDistanceBearing(Mazza, distanceMeters, bearingDegrees)
#     bearingDegrees = -90.0
#     print LatitudeLongitudeAtDistanceBearing(Mazza, distanceMeters, bearingDegrees)
#     bearingDegrees = -180.0
#     print LatitudeLongitudeAtDistanceBearing(Mazza, distanceMeters, bearingDegrees)
#     bearingDegrees = -270.0
#     print LatitudeLongitudeAtDistanceBearing(Mazza, distanceMeters, bearingDegrees)
#     bearingDegrees = -360.0
#     print LatitudeLongitudeAtDistanceBearing(Mazza, distanceMeters, bearingDegrees)
    
