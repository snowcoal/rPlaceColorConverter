# rPlaceColorConverter
converts images from default colors to r/place colors using CIEDE2000 algorithm

input image must be in the inputs folder and must be named "input.png"

requires openCV, numpy, and math to be installed and imported

findNearestPixel is deprecated and replaced with findNearestPixel2 but it can
be used in case you want to do euclidean pixel distance

code becomes VERY slow with large images