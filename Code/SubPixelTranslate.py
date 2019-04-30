# # Dependencies

#import PIL #for importing and exporting images
from PIL import Image

import random
import sys #to allow us to exit gracefully upon catching an error

import numpy as np #to deal with images as arrays of pixel values

import itertools# to use itertools.product

from fractions import Fraction #for float to numerator/denominator conversion

def importImage(Imfp, convert="L", DEBUG = False, NP = True):
    try:
        image = Image.open(Imfp)

    except Exception as err:
        print("Unable to load image, Exception:", err)
        sys.exit()

    #image.show()

    #working with pngs with transparency will be interpreted as black when we convert to BW later,
    #instead we explicitly set it to white now.
    if Imfp[-4:] == ".png":
        image.convert("RGBA") # Convert this to RGBA if possible
        pixel_data = image.load()

        if image.mode == "RGBA":
          # If the image has an alpha channel, convert it to white
          # Otherwise we'll get weird pixels
          for y in range(image.size[1]): # For each row ...
            for x in range(image.size[0]): # Iterate through each column ...
              # Check if it's opaque
              if pixel_data[x, y][3] < 255:
                # Replace the pixel data with the colour white
                pixel_data[x, y] = (255, 255, 255, 255)
    #image.show()
    if convert != "None":
        #When translating a color image to black and white (mode “L”), the library uses the ITU-R 601-2 luma transform:
        #L = R * 299/1000 + G * 587/1000 + B * 114/1000
        image = image.convert(convert)
    if DEBUG:
        print(Imfp)
        print("Format: {0}\tSize: {1}\nMode: {2}\t\tMaxVal: {3}\t MinVal:{4}\n".format(image.format,
                image.size, image.mode, image.getextrema()[0], image.getextrema()[1]))

    if NP:
        return np.array(image, dtype=np.uint8)#=np.int16) #convert to np array and return
    else:
        return image

def GenRandImage(dims=(16, 16), minval = 0, maxval=255, dtype=np.uint8):
    lenx, leny = dims
    randvals = np.random.randint(minval, maxval, size=lenx*leny, dtype=dtype)#np.int16)
    image = randvals.reshape((lenx, leny))

    return image

def NPtoPIL(array, ignore = False):
    if type(array) is not np.ndarray:
        raise ValueError("Array must be a numpy array")

    flag = False

    #Check array is suitable
    if array.min() < 0:
        if ignore:
            print("IGNORED - Warning: Array contains values below 0")
            flag = True
        else:
            raise ValueError("Array contains values below 0")
    if array.max() > 255:
        if ignore:
            print("IGNORED - Warning: Array contains values above 255")
            flag = True
        else:
            raise ValueError("Array contains values above 255")

    #if array is not suitable but ignore flag is given fix issues
    if flag:
        array.clip(0,255)

    return Image.fromarray(np.uint8(array))

def floatToFrac(val, output = False):
    fract = Fraction(val).limit_denominator()
    num = fract.numerator;     den = fract.denominator
    if output:
        string = r'\frac{' + str(num) + r'}{' + str(den) + r'}'
        display(Math(string))
    return num,den

def window_on_centre(Im, window_size, SILENT = True):

#     if not all(np.array(Im.shape)%2==window%2): #elegant oneliner I'm proud of

    if not Im.shape[0]%2 == window_size[0]%2: #xdims are both even or both odd
        window_size[0]+=1 #increase window size so they are both even or both odd
    if not Im.shape[1]%2 == window_size[1]%2: #xdims are both even or both odd
        window_size[1]+=1 #increase window size so they are both even or both odd

    if window_size[0]>Im.shape[0] or window_size[1]>Im.shape[1]: #check window is smaller then image
        raise ValueError("Window is larger then image")

    #determine the border length for each dimension
    #border_len = (int((Im.shape[0]-window_size[0])/2), int((Im.shape[1]-window_size[1])/2))
    border_len = [int((im_s-win_s)/2) for im_s,win_s in zip(Im.shape,window_size)]

    return Im[border_len[0]:border_len[0]+window_size[0], border_len[1]:border_len[1]+window_size[1]]

def averageSubArrayArea(Im, Area, DEBUG = False):
    '''
    Takes an array and averages over a square area,
    ie pass a 16x16 Image, with Area = 2 outputs a 8x8 Image
    '''

    Area_x, Area_y = Area

    if not all(np.array(Im.shape)%(Area_y, Area_x)==0): #check all dimensions are evenly divided

        raise ValueError("""Pixel Area doesn't evenly divide Image\n
        Im.shape={}, Area={}, np.array(Im.shape)%Area==0: {}""".format(Im.shape,Area, np.array(Im.shape)%Area==0))

    j_max, i_max  = map(int,np.array(Im.shape)/(Area_y, Area_x)) #extract the final image size ie (16,16)/(4,2)=(4,8)
    #casting to avoid packages complaining, should already be ints

    if DEBUG:
        print("Px Size: {}, \tAveraged Array Shape: [{},{}]".format(Area, i_max, j_max))

    Averaged_Array = np.empty((j_max, i_max), dtype=np.uint8) #initialise array to shape

    for i,j in itertools.product(range(i_max), range(j_max)): #iterate through subarrays
    #product creates all permutations ie (0,0) (0,1) (0,2) (1,0) (1,1) (1,2) (2,0) (2,1) (2,2)
        if False: #print out each subarray and average value as we go
            print("SubArray[{}][{}] = [{:d}:{:d},{:d}:{:d}]".format(j,i,Area_x*i,Area_x*(i+1),Area_y*j,Area_y*(j+1))) #print subarray params
        Averaged_Array[j][i] = np.average(Im[Area_y*j:Area_y*(j+1),Area_x*i:Area_x*(i+1)])

    return Averaged_Array

def subPixelTranslate(translation, Im, window_size, SILENT = True, DEBUG = False, max_scale=100):
    """
    Im - Image to be translated - numpy array or PIL Image
    translation - (tx,ty), tuple describing translation in pixels, can be float
    window_size - (winx,winy), tuple describing the windowed image size, output image size,
    SILENT - output operation printImDetails, default = True
    max_scale - max supersampling value, default = 100
    DEBUG - output debug info, default = False
    """

    if type(Im) is not np.ndarray:
        Im = np.array(image, dtype=np.uint8)

    if DEBUG:
        print("subPixelTranslate: Im.shape: ",Im.shape)
        test_name = "Imported"
        new_im = Image.fromarray(Im,mode='L')
        new_im.save("Test_Images/TEST/test_{}.png".format(test_name))

    winx, winy = map(int,window_size)
    tx,ty = translation

    # Window around centre, size N+2*np.ceil(translation)
    x_border = np.ceil(abs(tx))
    y_border = np.ceil(abs(ty))
    interWin_size= list(map(int,[winy+2*np.ceil(abs(y_border)), winx+2*np.ceil(abs(x_border))]))
    if DEBUG:
        print("subPixelTranslate: Xborder: {}, YBorder: {}".format(x_border, y_border))

    Im = window_on_centre(Im, interWin_size)
    if DEBUG:
        print("subPixelTranslate: Windowed Im.shape: ",Im.shape)
        test_name = "Windowed"
        new_im = Image.fromarray(Im,mode='L')
        new_im.save("Test_Images/TEST/test_{}.png".format(test_name))

    #SuperSample
    px_tx, SupScale_x = floatToFrac(tx)
    px_ty, SupScale_y = floatToFrac(ty)

    if not SILENT or DEBUG:
        print("subPixelTranslate: Tx: {:.4f}, Ty: {:.4f},\t Supersampled: {}x, Translated: {}px".format(tx,ty, (SupScale_x, SupScale_y),(px_tx, px_ty)))

    #axis=1 -> cols (xdim), axis=0 -> rows (ydim)
    Im = (Im.repeat(SupScale_x, axis=1)).repeat(SupScale_y, axis=0)

    if DEBUG:
        print("subPixelTranslate: Supersampled Windowed Im.shape: ",Im.shape)
        test_name = "UpScaled"
        new_im = Image.fromarray(Im,mode='L')
        new_im.save("Test_Images/TEST/test_{}.png".format(test_name))

    """translate using slice Im[scale*t:scale(t+N)] and simultaneously window to final size
    Image moving right (pos tx), window moves left (neg x)
    Image moving left (neg tx), window moves right (pos x)
    Image moving up (pos ty), window moves down (pos y)
    Image moving down (neg ty), window moves up (neg y)"""


    x1 = round(SupScale_x*(np.ceil(abs(tx)))-px_tx)
    x2 = round(SupScale_x*(np.ceil(abs(tx))+winx)-px_tx)
    y1 = round(SupScale_y*(np.ceil(abs(ty)))+px_ty)
    y2 = round(SupScale_y*(np.ceil(abs(ty))+winy)+px_ty)


    #WINDOWING
    if DEBUG:
        print("subPixelTranslate: Windowing: [{}:{},{}:{}]".format(x1,x2,y1,y2))
    #x and y are flipped because of the weird notation of numpy slicing, rows(y) then cols(x)
    Im = Im[int(y1):int(y2), int(x1):int(x2)]


    if DEBUG:
        print("subPixelTranslate: Translated Im.shape: ",Im.shape)
        test_name = "Translated"
        new_im = Image.fromarray(Im,mode='L')
        new_im.save("Test_Images/TEST/test_{}.png".format(test_name))

    #AVERAGING OVER AREA
    Im = averageSubArrayArea(Im, (SupScale_x, SupScale_y), DEBUG)
    if DEBUG:
        print("subPixelTranslate: Returned Im.shape: ",Im.shape)
        print("subPixelTranslate: Tx: {:.3f}, Ty: {:.3f}, COMPLETE\n".format(tx,ty))
        test_name = "Averaged_back-FINAL"
        new_im = Image.fromarray(Im,mode='L')
        new_im.save("Test_Images/TEST/test_{}.png".format(test_name))

    return Im
