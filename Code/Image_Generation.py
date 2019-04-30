from PIL import Image #for importing and exporting images
import numpy as np #to deal with images as arrays of pixel values
from numpy import ceil
import tqdm #progress bar

import multiprocessing
import functools #needed for passing additional parameters to the map function for multiprocessing
import os #to allow us to create folders for output on the fly
import sys #to allow us to exit gracefully upon catching an error
import time #to allow timing execution

from SubPixelTranslate import *

def image_gen(translation, testImage, window_size, SILENT, DEBUG, out_folder, out_filename, save='BOTH'):
    tx,ty = translation

    out_filename = out_filename.format(tx,ty).replace(".", ",") #change 0.00 to 0,00 to prevent fileextension conflicts

    translated_testImage = subPixelTranslate(translation, testImage, window_size, SILENT, DEBUG) #translate the image by tx
    if save == 'BOTH' or 'NP':
        np.save(out_folder+'NP/'+out_filename.format(tx,ty),translated_testImage) #save the image without compression
        if DEBUG:
            print('Successfully saved as NPArray')
    if save == 'BOTH' or 'IM':
        new_im = Image.fromarray(translated_testImage,mode='L')
        new_im.save(out_folder+'IM/'+out_filename+'.png')
        if DEBUG:
            print('Successfully saved as Image')
    if DEBUG:
        print("Tx: {:.3f}, Ty: {:.3f}, COMPLETE".format(tx,ty))

if IMAGE == "USAF_FHD":

    #OUTPUT DIRECTORY COMMANDS
    Test_Images_dir = "/run/media/james/linuxstorage/Thesis/Code/Test_Images/USAF/"
    fname = "USAF-1951_FullHD"
    out_folder = Test_Images_dir+"USAF_FHD/"
    out_filename = fname+"_{:+.3f}x_{:+.3f}y"

    window_size = (1400,1400)

    #TRANSLATION PARAMETERS
    ty = 0
    tx_step = 0.004 # 1/256= 0.00390625
    tx_min = -10
    tx_max = 10
    t_vals = [(tx,ty) for tx in np.arange(tx_min,tx_max+tx_step,tx_step)]
    #Finished, Image Generation took: 05:23:38, averaged 4s per image

if __name__ == "__main__":
    NUMBER_OF_THREADS = 8
    #DEBUG COMMANDS
    SILENT = True
    DEBUG = False

    testImage = importImage(Test_Images_dir+fname+".jpg",DEBUG=False)

    #check if output folders exists, if not create them
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    if not os.path.exists(out_folder+'NP/'):
        os.makedirs(out_folder+'NP/')
    if not os.path.exists(out_folder+'IM/'):
        os.makedirs(out_folder+'IM/')

    print("Generating {} Images with translations {:+.2f}px to {:+.2f}px in steps of {:+.3f}px".format(len(t_vals), tx_min, tx_max, tx_step))
    print("and saving to '{}''".format(out_folder))
    print("fname_format = ",out_filename)
    print("Window Size: {}px x {}px\n".format(window_size[0],window_size[1]))

    start = time.time()

    pool = multiprocessing.Pool(processes = NUMBER_OF_THREADS)
    func = functools.partial(image_gen, testImage=testImage, window_size=window_size, SILENT=SILENT, DEBUG=DEBUG, out_folder=out_folder, out_filename=out_filename, save='BOTH')
    for _ in tqdm.tqdm(pool.imap_unordered(func, t_vals), total=len(t_vals)):
        pass
    pool.close()

    elapsed = time.time()-start
    elapsed_string = time.strftime("%H:%M:%S", time.gmtime(elapsed))

    print("Finished, Image Generation took: {}, averaged {:.0f}s per image".format(elapsed_string,elapsed/len(t_vals)))
