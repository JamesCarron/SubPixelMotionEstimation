import PIL
from PIL.Image import Image
import numpy as np

def ImageSubtract(image1, image2):
    if type(image1) is PIL.Image.Image or type(image2) is PIL.Image.Image:
        # comes in as uint8 as in the image
        image1 = np.array(image1, dtype=np.int16)
        image2 = np.array(image2, dtype=np.int16)

    if image1.shape != image2.shape:
        raise ValueError("Images must be the same size")

    return image1 - image2

def SumRowsCols(image, absolute=False):
    if absolute:
        RowSumVals = [sum(abs(row)) for row in image]
        ColSumVals = [sum(abs(col)) for col in image.T]
    else:
        RowSumVals = [sum(row) for row in image]
        ColSumVals = [sum(col) for col in image.T]

    return RowSumVals, ColSumVals

def ProposedMethod(Im1, Im2, ErrorCheck = False):

    #Input Sanitisation
    if type(Im1) is PIL.Image.Image or type(Im2) is PIL.Image.Image:
        # comes in as uint8 as in the image
        Im1 = np.array(Im2, dtype=np.int16)
        Im1 = np.array(Im2, dtype=np.int16)
    if Im1.shape != Im2.shape:
        raise ValueError("Images must be the same size")

    #Compute Difference Matrix
    SubIm = Im1 - Im2

    #Calculate Row and Column totals
    RowSumVals = [sum(row) for row in SubIm]
    ColSumVals = [sum(col) for col in SubIm.T]

    RowTot = sum(map(abs,RowSumVals)); ColTot = sum(map(abs,ColSumVals)) #compute absolute sum of row & col sums

    if ErrorCheck:
        ErrorCheck = np.average(SubIm)
        return RowTot, ColTot, ErrorCheck

    return RowTot, ColTot

def plotProposedMethodResults(Tx, Results, fp=None):

    TxResults = [result[0] for result in Results]
    TyResults = [result[1] for result in Results]
    ECResults = [result[2] for result in Results]

    plt.plot(Tx, TxResults,label ="RowSums")
    plt.plot(Tx, TyResults,label ="ColSums")
    plt.title("Measuring Translation w/ Proposed Method")
    plt.xlabel("X Translation (px)")
    plt.ylabel("Translation Value output by method")
    plt.legend()
    if fp!= None:
        plt.savefig(fp.format("Trans"))
    plt.show()

    plt.plot(Tx, ECResults)
    plt.title("Error Check Value")
    plt.xlabel("X Translation (px)")
    plt.ylabel("Error Check Indicator")
    if fp!= None:
        plt.savefig(fp.format("EC"))
    plt.show()
