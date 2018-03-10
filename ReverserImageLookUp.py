# Code partly inspired by this nice tutorial: https://www.youtube.com/watch?v=Myj8zbsfZBA

import urllib.request as urllib2
from urllib.request import urlopen
from http.cookiejar import CookieJar

cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17')]

def reverseImageLookup(imagepath):
    imagepath = 'http://mw2.google.com/mw-panoramio/photos/medium/55798137.jpg'
    lookuppath = 'https://www.google.com/searchbyimage?image_url='+imagepath
    sourceCode = opener.open(lookuppath).read()

    location = 'style="font-style:italic">'
    startName = str(sourceCode).find(location)+len(location)
    endName = str(sourceCode)[startName:].find('<')    
    return str(sourceCode)[startName:startName+endName]

imagepath = 'http://mw2.google.com/mw-panoramio/photos/medium/55798137.jpg'
code = reverseImageLookup(imagepath)
print(code)
