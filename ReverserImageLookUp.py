#Import dependencies
import urllib.request as urllib2
from urllib.request import urlopen
from http.cookiejar import CookieJar
from icrawler.builtin import GoogleImageCrawler
import sys
from io import StringIO
import os
from os import walk
from difflib import SequenceMatcher
import re
import urllib
import pandas as pd


cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17')]

def reverseImageLookup(imagepath):
    # Code partly inspired by this nice tutorial: https://www.youtube.com/watch?v=Myj8zbsfZBA
    # Looks up content of the image via Google image reverse search
    unavailable = True
    while(unavailable):#Check that Google services are available. Otherwise try again every couple seconds.
        try:
            unavailable = False
            lookuppath = 'https://www.google.com/searchbyimage?image_url='+imagepath#link to image reverse search
            sourceCode = opener.open(lookuppath).read()#get sourcecode of result page from google image search
            #extract name of the object depected in the image
            location = 'style="font-style:italic">'
            startName = str(sourceCode).find(location)+len(location)
            endName = str(sourceCode)[startName:].find('<')
        except (urllib2.HTTPError) as err: 
            unavailable = True
            print('Unavailable Google Image Request service, waiting for further responses')
    return str(sourceCode)[startName:startName+endName]

def CrawlSimilarImages(imagepath,directory,numSimilar):
    unavailable = True
    allLinks = []
    while(unavailable): 
        try:
            unavailable = False
            # The first part of the link we want to open is always the same
            lookuppathOriginalImage = 'https://www.google.com/searchbyimage?image_url='+imagepath
            sourceCodeOriginalImage = opener.open(lookuppathOriginalImage).read()
            # Extract the link that is looking for similar images:
            location = 'class="iu-card-header" href="'
            startName = str(sourceCodeOriginalImage).find(location)+len(location)
            endName = str(sourceCodeOriginalImage)[startName:].find('">') 
            # The link that leads to similar images usually contains substrings we want to get rid of:
            lookuppathSimilarImages = ('https://www.google.de'+str(sourceCodeOriginalImage)[startName:startName+endName]).replace('amp;','')
            sourceCodeSimilarImages = opener.open(lookuppathSimilarImages).read()
            # The part where the intersting images are starts with '"ou":' in the source code 
            allLinksToSimilarImages = str(re.findall(r'(?:http\:|https\:)?\/\/.*\.(?:png|jpg)', str(sourceCodeSimilarImages))).split('"ou":')[1:]
            # Remove the end of the strings to only get the links of all single images
            # TODO: maybe remove shutterstock and alamy and other stocks?
            allLinksToSimilarImages = [str(str(linkToOneImage).split(',"ow"')[0]).replace('"','').replace('\']','') for linkToOneImage in allLinksToSimilarImages]
            # Download images and save them in the directory
            counter = 0
            for similarImageIndex in range(len(allLinksToSimilarImages)):
                if(counter >= numSimilar):
                    break
                else:
                    try:
                        # Download the image
                        urllib.request.urlretrieve(allLinksToSimilarImages[similarImageIndex],directory+ "similarImage_"+str(counter)+".jpg")
                        allLinks.append(allLinksToSimilarImages[similarImageIndex])
                    except (urllib2.HTTPError,urllib2.URLError) as err:
                        print('error in image number '+str(similarImageIndex))
                counter = counter+1
        except (urllib2.HTTPError) as err: 
            unavailable = True
            print('Unavailable Google Image Request service, waiting for further responses')                    
    return allLinks

def CrawlByName(name,numPictures,savedir):
    #Crawls numPictures amount of images from Goggle images with given search term
    print('Start Crawling...')
    capture = StringIO()
    sys.stderr = capture
    google_crawler = GoogleImageCrawler(parser_threads=2, downloader_threads=4,storage={'root_dir': str(savedir)})
    google_crawler.crawl(keyword=str(name),max_num=numPictures,date_min=None, date_max=None)
    return(capture.getvalue())#Return output with image links (needed later for crossvalidation)

def getPictureLinks(stdout,numPictures):
    #Extract the links of all images from complex output
    remainder = stdout
    links = []
    for i in range(numPictures):
        start = remainder.find('#')
        end = remainder[start:].find('\n')
        links.append(remainder[start+3:start+end])
        remainder = remainder[start+end:]
    return links

def CrossCheckImages(name,Links,savedir):
    #Put crawled images back into Google image reverse search to check if they depect the right object
    #Images which get a lable which is very different to the desired lable (eg: 'statue of liberty'
    #instead of 'federal hall national memorial' the images are deleted from the folder.
    #Images which are >50% similar (eg: 'federal hall new york' instead of 'federal hall national memorial'
    #are kept in the respective folder.
    print('Crosscheck Images...')
    f=[]
    finalLinks = pd.DataFrame(columns = ['Link','ImageName'])
    for (dirpath, dirnames, filenames) in walk(str(savedir)):
        f.extend(filenames)
    for j,link in enumerate(Links):
        lookup = str(reverseImageLookup(link.strip()))
        similarity = SequenceMatcher(None, lookup, name).ratio()#Check how similar the target string (name) and predicted string (lookup) are
        if similarity<0.50:#If similarity<50 delete the image
            os.remove(savedir+f[j])
        else:
            finalLinks = finalLinks.append({'Link':link,'ImageName':str(f[j])},ignore_index=True)
        print(str(f[j])+": "+lookup+"  -  "+str(similarity))
    finalLinks.to_csv(savedir+str(name)+'_Links.csv',encoding='latin1')
    
def MagicPictureMultiplier(imagepath,savedir,numPictures=2,numSimilar=5,SetName=None):
    #imagepath: link to your image of object of which you want to have more images
    #savedir: where the multiplied images should be saved
    #(optional):
    #   numSimilarPictures: How many visually similar pictures do you want (max 100)
    #   numPictures: amount of images that you want to download from this object (may be less after cross validation)
    #   SetName: define which object is depicted in your image (eg: if the Google image detection is faulty)
    if (SetName==None):
        name = reverseImageLookup(imagepath)#Get name of the object depicted in the image
        print('Image recognized as '+str(name))
    else:
        name = SetName
        print('Object in image defined as '+str(SetName))
    text = CrawlByName(name,numPictures,savedir)#Download images of this object from normal google images search
    save_stderr = sys.stderr#just for extracting shell output
    links = getPictureLinks(text,numPictures)#Get links of downloaded images
    sys.stderr = save_stderr
    SimilarLinks = CrawlSimilarImages(imagepath,savedir,numSimilar)
    CrossCheckImages(name,links+SimilarLinks,savedir)#Crosscheck downloaded images and delete wrone images

MagicPictureMultiplier('http://lh6.ggpht.com/-qgyDi-Y1qKM/RscL96Mvx5I/AAAAAAAAAlg/IF5A8dD_cCU/s1600/','./CrawledImages/', numPictures = 10, numSimilar=10)
