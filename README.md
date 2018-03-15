# IncreaseYourTrainingData
*This is a collaborative project by Falk Heuer, Viviane Kakerbeck, Johannes Schrumpf and Justine Winkler.*

Increase the amount of image training data for your network training by finding more images of the same object/scene online. This is done by using
google image reverse search to extract the content in an image and then by crawling google images (and potentially other sources) for similar images.

This was written as a one day project and intended as a help for anybody who needs a lot of image data. If there are any errors or problems
just contact us. We would love to make this code as usefriendly as possible.

## Usage:
 To extract 20 images of an object in image x at fileURLx and save them in savedirx run the following command:
 
 `MagicPictureMultiplier('fileURLx', 'savedirx', numPictures = 10, numSimilar=10)`
 
 `numPictures` specifies how many images should be extracted from the google search results of the detected objects name. `numSimilar` specifies how many similar looking images should be extracted from the google similar image search results. Similar images may potentially 
 show different objects which look similar to the original one while results of the google search for the term may show sketches or unwanted views on the object (eg: search for a building can yeild photos from the inside of the building and not just images of the facade). The ratio of numPictures and numSimilar therefore specifies what you want to emphasise more. It may happen that in the end you get less images in your savedir than numPictures+numSimilar. This happens when we crosscheck the downloaded images and find that some images depict a different object than the original image. These downloaded pictures are then deleted.
 
In case the object detector detects the wrong object in your image there is an option to overwrite this. If you know what is depicted in your image you can specify this with `SetName='YourObjectsName'` in the MagicPictureMultiplier call.
