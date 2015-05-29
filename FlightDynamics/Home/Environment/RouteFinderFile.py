# -*- coding: UTF-8 -*-
'''
Created on 7 mai 2015

@author: PASTOR Robert

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

see route finder website

'''
import time
import urllib2
import urllib
from HTMLParser import HTMLParser

from Home.Environment.WayPointsDatabaseFile import WayPointsDatabase

# create a subclass and override the handler methods
class HtmlParser(HTMLParser):
    
    def __init__(self, searchedTag):
        HTMLParser.__init__(self)

        self.searchedTag = searchedTag
        self.StartTagFound = False
        self.EndTagFound = False
        self.filteredData = ''
        
    
    def handle_starttag(self, tag, attrs):
        if tag == self.searchedTag:
            #print "Encountered a start tag:", tag
            self.StartTagFound = True
            
    def handle_endtag(self, tag):
        if tag == self.searchedTag:
            #print "Encountered an end tag :", tag
            self.EndTagFound = True
            
    def handle_data(self, data):
        if self.StartTagFound and not(self.EndTagFound):
            #print "Encountered some data  :", data
            self.filteredData += (data)
            
    def searchedTagFound(self):
        return self.StartTagFound and self.EndTagFound
            
    def getFilteredData(self):
        return self.filteredData


class RouteFinder(object):
    route = ''
    
    def __init__(self):
        self.className = self.__class__.__name__

        self.script_url = "http://rfinder.asalink.net/free/autoroute_rtx.php"
        self.base_url = "http://rfinder.asalink.net/free/"

        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = { 'User-Agent' : user_agent , 
               "Content-type": "application/x-www-form-urlencoded", 
               "Accept": "text/plain"}

    def isConnected(self):
        response = urllib2.urlopen(url = self.base_url)
        the_html_page = response.read()
        #print the_html_page
        htmlParser = HtmlParser(searchedTag = 'form')
        htmlParser.feed(the_html_page)
        return htmlParser.searchedTagFound()
    
    
    def findRoute(self, Adep, Ades, RFL):
        ''' query the route finder website and retrieve a route '''
        self.Adep = Adep
        self.Ades = Ades
        assert isinstance(RFL, (str,unicode)) and (len(RFL)>0) and str(RFL).startswith('FL')
        assert not(Adep is None) and isinstance(Adep,(str,unicode)) and (len(Adep)>0)
        assert not(Ades is None) and isinstance(Ades,(str,unicode)) and (len(Ades)>0)
        values = { 'id1': Adep,
                    'ic1':'',
                    'id2': Ades,
                    'ic2':'',
                    'minalt':'FL230',
                    'maxalt': RFL,
                    'lvl':'B',
                    'dbid': 1408,
                    'usesid':'Y',
                    'usestar':'Y',
                    'easet':'Y',
                    'rnav':'Y',
                    'nats':'',
                    'k':235644007           } 
        data = urllib.urlencode(values)
        response = urllib2.urlopen(url = self.script_url, data= data)
        
        #print 'encoding = {0}'.format(response.headers.getparam('charset'))
        encoding = response.headers.getparam('charset')
        the_html_page = response.read().decode(encoding)

        the_html_page= the_html_page.replace('&deg;', u'\xb0')
        
        htmlParser = HtmlParser(searchedTag = 'pre')
        htmlParser.feed(the_html_page)
        if (htmlParser.searchedTagFound()):
            self.route = htmlParser.getFilteredData()
            #print '{0}'.format(self.route)
            return True
        return False
            
            
    def getRouteAsList(self):
        ''' get a route as a list '''
        routeList = []
        fixIndex = 0
        for line in self.route.split('\n'):
            if 'Remarks' in line: continue
            if self.Adep in line or self.Ades in line: continue
            index = 0
            fixDict = {}
            for item in line.split(' '):
                item = unicode(item).strip()
                if len(item)==0: continue
                if index == 0 :
                    #print 'fix= {0}'.format(item)
                    fixDict['Name'] = item
                    index += 1
                if len(item)> 0 and (u'\xb0' in unicode(item).strip()):
                    if 'N' in item or 'S' in item :
                        #print 'latitude= {0}'.format( unicode(unicode(item).strip()))
                        fixDict['latitude'] = item
                    if 'W' in item or 'E' in item:
                        #print 'longitude= {0}'.format( unicode(unicode(item).strip()))
                        fixDict['longitude'] = unicode(item).strip()
                    ''' increment only if item len > 0 ''' 
                    index += 1
            if len(fixDict) > 0:
                routeList.append( fixDict )
                fixIndex += 1
        return routeList
    
    def insertWayPointsInDatabase(self, wayPointsDb):
        
        for fix in self.getRouteAsList():    
            wayPointsDb.insertWayPoint(fix['Name'], 
                                       fix['latitude'], 
                                       fix['longitude'])


#============================================
if __name__ == '__main__':
    
    wayPointsDb = WayPointsDatabase()
    assert ( wayPointsDb.read() )
    
    print "=========== Route Finder start  =========== " + time.strftime("%c")

    routeFinder = RouteFinder()
    if routeFinder.isConnected():
        print 'route finder is connected'
        
        print "=========== Route Finder start  =========== " + time.strftime("%c")
        Adep = 'LPPT'
        Ades = 'LFPG'
        RFL = 'FL360'
        
        if routeFinder.findRoute(Adep, Ades, RFL):
            routeList = routeFinder.getRouteAsList()
            print routeList
            routeFinder.insertWayPointsInDatabase(wayPointsDb)
    
    print "=========== Route Finder start  =========== " + time.strftime("%c")
