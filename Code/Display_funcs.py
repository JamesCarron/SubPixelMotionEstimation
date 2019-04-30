#from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt #for plotting graphs
import matplotlib.ticker as plticker
import numpy as np
import PIL
from PIL import Image

import matplotlib as mpl
import matplotlib.ticker as ticker #for modifying graph ticks
from mpl_toolkits.mplot3d import Axes3D #for plotting 3D graphs
import matplotlib.pyplot as plt #for plotting graphs
mpl.rcParams['figure.figsize'] = (10, 3)

from IPython.display import display, Math, Latex  # allow latex output from Python

def printImDetails(Im):
         print("Format: {0}\tSize: {1}\nMode: {2}\t\tMaxVal: {3}\t MinVal:{4}\n".format(Im.format,
     Im.size, Im.mode, Im.getextrema()[0], Im.getextrema()[1]))

def ImPlot2D3D(img, step=False, ratio=50, cmap=plt.cm.jet, DEBUG=False):

    if type(img) is PIL.Image.Image:
        img = np.array(img, dtype=np.int16)
        if DEBUG:
            print("Passed PIL Image Object")

    Z = img[::1, ::1]

    fig = plt.figure(figsize=(14, 7))

    # 2D Plot
    ax1 = fig.add_subplot(1, 2, 1)
    im = ax1.imshow(Z, cmap=cmap)
    plt.colorbar(im) #add a colorbar legend
    ax1.set_title('2D')
    ax1.grid(False)

    # 3D Plot
    if step:
        img = (img.repeat(ratio, axis=0)).repeat(ratio, axis=1)
        Z = img[::1, ::1]

    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    X, Y = np.mgrid[:Z.shape[0], :Z.shape[1]]
    ax2.plot_surface(X, Y, Z, cmap=cmap)
    ax2.set_title('3D')

    # Scale the ticks back down to original values
    if step:
        ticks_x = ticker.FuncFormatter(
            lambda x, pos: '{0:g}'.format(x / ratio))
        ticks_y = ticker.FuncFormatter(
            lambda y, pos: '{0:g}'.format(y / ratio))

        ax2.xaxis.set_major_formatter(ticks_x)
        ax2.yaxis.set_major_formatter(ticks_y)

    plt.show()

# ### ShowIm
def showIm(image, invert=False, disp_dim=100, cmap=None, axes=False, scale=1, grid=False, grid_interval=1.0, fp=None, ffolder = "/home/james/GoogleDrive/College/Thesis/Code/Sim_Results/"):

    # if image is actually a numpy array display with matplotlib
    if type(image) is np.ndarray:
        if cmap == None:
            if invert:
                cmap = plt.cm.gist_yarg
            else:
                cmap = plt.cm.gist_gray

        Z = image[::1, ::1]

        sizes = np.shape(Z)
        fig = plt.figure(figsize=(1*scale,1*scale))
        ax=fig.add_subplot(111)
        # Remove whitespace from around the image
        fig.subplots_adjust(left=0,right=1,bottom=0,top=1)

        if not axes: #remove the axes from the plot
            #ax = plt.Axes(fig, [0., 0., 1., 1.])
            ax.set_axis_off()
            #fig.add_axes(ax)


        if grid:
            # Set the gridding interval: here we use the major tick interval
            loc = plticker.MultipleLocator(base=grid_interval)
            ax.xaxis.set_major_locator(loc)
            ax.yaxis.set_major_locator(loc)

            # Add the grid
            ax.grid(which='major', axis='both', linestyle='-')
            # # Add the image
            # ax.imshow(image)

            # Find number of gridsquares in x and y direction
            nx=abs(int(float(ax.get_xlim()[1]-ax.get_xlim()[0])/float(grid_interval)))
            ny=abs(int(float(ax.get_ylim()[1]-ax.get_ylim()[0])/float(grid_interval)))

            # Add the values to the gridsquares
            for j in range(ny):
                y=grid_interval/2+j*grid_interval
                for i in range(nx):
                    x=grid_interval/2.+float(i)*grid_interval
                    ax.text(x,y,'{:d}'.format(image[i][j]),color='r',ha='l',va='l')



        if fp != None:
            fig.savefig(ffolder+fp)
        plt.show()

    # if image is actually a PIL Image Object display with jupyter
    if type(image) is PIL.Image.Image:
        if invert:
            image = ImOps.invert(image)
        if image.width < disp_dim and image.height < disp_dim:
            if image.width > image.height:
                scale = int(np.ceil(disp_dim / image.height))
            else:
                scale = int(np.ceil(disp_dim / image.width))

            dims = map(int, ((image.width * scale), (image.height * scale)))
            display(image.resize(dims, 0))
        else:
            display(image)

def FracToString(num,den):
    return r'\frac{' + str(num) + r'}{' + str(den) + r'}'

def ImageTExample(image, tx, ty=0,R=False):
    num, den = floatToFrac(tx)
    string = r'Translated: ' + "{:.2f}".format(tx) + r'px=\frac{' + "{:.0f}".format(num) + r'}{' + "{:.0f}".format(den) + r'}px'
    #print(string)
    print("-"*40)
    display(Math(string))
    translated_testImage = subPixelTranslate(image, [(tx,ty)] ) #translate the image by 1/4 of a pixel
    showIm(translated_testImage)
    if R:
        return translated_testImage
