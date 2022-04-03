
import cv2
import numpy as np
import math

def generatePixelArray():
    array = []
    floatArray = []

    img = cv2.imread('inputs/colors.png')
    labImg = convertToLABImg(img)

    for i in range(0,2532,100):
        pixel = img[0,i]
        fPixel = labImg[0,i]

        array.append(pixel)
        floatArray.append(fPixel)

    array.pop(19)
    array.pop(0)
    floatArray.pop(19)
    floatArray.pop(0)

    return [array, floatArray]

def convertToLABImg(img):
    floatImg = img.copy()
    floatImg = np.float32(floatImg)
    floatImg *= 1./255
    labImg = cv2.cvtColor(floatImg, cv2.COLOR_BGR2LAB)

    return labImg


def findNearestPixel(pixel, pixelArray):
    dists = []
    for p in pixelArray:
        dists.append((int(p[0])-int(pixel[0]))**2 + (int(p[1])-int(pixel[1]))**2 + (int(p[2])-int(pixel[2]))**2)
    
    return pixelArray[np.argmin(dists)]
    

def findNearestPixel2(pixel, fpixelArray):
    vals = []
    for p in fpixelArray:
        vals.append(CIEDE2000(pixel, p))

    idx = np.argmin(vals)

    return [fpixelArray[np.argmin(vals)],idx]


def main():
    pixelArray,fPixelArray = generatePixelArray()

    try:
        img = cv2.imread('inputs/input.png')
        cpy = img.copy()
    except:
        print("\n")
        print("please name the input image \"input.png\" and place it into the inputs folder")
        print("\n")
        return
    labImg = convertToLABImg(img)
    
    h,w, chn = labImg.shape
    

    pixels = [0]*24

    for i in range(h):
        for j in range(w):
            pixel = labImg[i,j]
            newPixel = findNearestPixel2(pixel, fPixelArray)
            pixels[newPixel[1]] += 1
            cpy[i,j] = pixelArray[newPixel[1]]

    #cv2.cvtColor(cpy, cv2.COLOR_LAB2BGR)
    cv2.imwrite("output.png", cpy)

    print(pixels)

# code taken from: https://github.com/lovro-i/CIEDE2000/blob/master/ciede2000.py
def CIEDE2000(Lab_1, Lab_2):
    '''Calculates CIEDE2000 color distance between two CIE L*a*b* colors'''
    C_25_7 = 6103515625 # 25**7
    
    L1, a1, b1 = Lab_1[0], Lab_1[1], Lab_1[2]
    L2, a2, b2 = Lab_2[0], Lab_2[1], Lab_2[2]
    C1 = math.sqrt(a1**2 + b1**2)
    C2 = math.sqrt(a2**2 + b2**2)
    C_ave = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(C_ave**7 / (C_ave**7 + C_25_7)))
    
    L1_, L2_ = L1, L2
    a1_, a2_ = (1 + G) * a1, (1 + G) * a2
    b1_, b2_ = b1, b2
    
    C1_ = math.sqrt(a1_**2 + b1_**2)
    C2_ = math.sqrt(a2_**2 + b2_**2)
    
    if b1_ == 0 and a1_ == 0: h1_ = 0
    elif a1_ >= 0: h1_ = math.atan2(b1_, a1_)
    else: h1_ = math.atan2(b1_, a1_) + 2 * math.pi
    
    if b2_ == 0 and a2_ == 0: h2_ = 0
    elif a2_ >= 0: h2_ = math.atan2(b2_, a2_)
    else: h2_ = math.atan2(b2_, a2_) + 2 * math.pi

    dL_ = L2_ - L1_
    dC_ = C2_ - C1_    
    dh_ = h2_ - h1_
    if C1_ * C2_ == 0: dh_ = 0
    elif dh_ > math.pi: dh_ -= 2 * math.pi
    elif dh_ < -math.pi: dh_ += 2 * math.pi        
    dH_ = 2 * math.sqrt(C1_ * C2_) * math.sin(dh_ / 2)
    
    L_ave = (L1_ + L2_) / 2
    C_ave = (C1_ + C2_) / 2
    
    _dh = abs(h1_ - h2_)
    _sh = h1_ + h2_
    C1C2 = C1_ * C2_
    
    if _dh <= math.pi and C1C2 != 0: h_ave = (h1_ + h2_) / 2
    elif _dh  > math.pi and _sh < 2 * math.pi and C1C2 != 0: h_ave = (h1_ + h2_) / 2 + math.pi
    elif _dh  > math.pi and _sh >= 2 * math.pi and C1C2 != 0: h_ave = (h1_ + h2_) / 2 - math.pi 
    else: h_ave = h1_ + h2_
    
    T = 1 - 0.17 * math.cos(h_ave - math.pi / 6) + 0.24 * math.cos(2 * h_ave) + 0.32 * math.cos(3 * h_ave + math.pi / 30) - 0.2 * math.cos(4 * h_ave - 63 * math.pi / 180)
    
    h_ave_deg = h_ave * 180 / math.pi
    if h_ave_deg < 0: h_ave_deg += 360
    elif h_ave_deg > 360: h_ave_deg -= 360
    dTheta = 30 * math.exp(-(((h_ave_deg - 275) / 25)**2))
    
    R_C = 2 * math.sqrt(C_ave**7 / (C_ave**7 + C_25_7))  
    S_C = 1 + 0.045 * C_ave
    S_H = 1 + 0.015 * C_ave * T
    
    Lm50s = (L_ave - 50)**2
    S_L = 1 + 0.015 * Lm50s / math.sqrt(20 + Lm50s)
    R_T = -math.sin(dTheta * math.pi / 90) * R_C

    k_L, k_C, k_H = 1, 1, 1
    
    f_L = dL_ / k_L / S_L
    f_C = dC_ / k_C / S_C
    f_H = dH_ / k_H / S_H
    
    dE_00 = math.sqrt(f_L**2 + f_C**2 + f_H**2 + R_T * f_C * f_H)
    return dE_00

main()