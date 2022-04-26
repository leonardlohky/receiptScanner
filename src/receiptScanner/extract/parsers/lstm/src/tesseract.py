# -*- coding: utf-8 -*-
import os
import cv2
import imutils
import numpy as np
import pytesseract as pya

from PIL import Image
from imutils.perspective import four_point_transform

kernel = np.array([[0, -1, 0],
                   [-1, 5,-1],
                   [0, -1, 0]])

def to_text_img(frame, debug=None):
    """Wraps Tesseract OCR. Extract text from frame that were originally non-PDF
    Parameters
    ----------
    frame : str
        path of electronic invoice in JPG or PNG format
    debug : 
        enables debug visualization
    Returns
    -------
    extracted_str : str
        returns extracted text from image in JPG or PNG format
    """
    
    image = frame.copy()
    image = imutils.resize(image, width=500)
    ratio = frame.shape[1] / float(image.shape[1])
    
    # convert the image to grayscale, blur it slightly, and then apply
    # edge detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5,), 0)
    edged = cv2.Canny(blurred, 75, 200)
    
    if debug:
        cv2.imshow("Input", image)
        cv2.imshow("Edged", edged)
        cv2.waitKey(0)
    
    # find contours in the edge map and sort them by size in descending
    # order
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    
    # initialize a contour that corresponds to the receipt outline
    receiptCnt = None
    # loop over the contours
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # if our approximated contour has four points, then we can
        # assume we have found the outline of the receipt
        if len(approx) == 4:
            receiptCnt = approx
            break
    # if the receipt contour is empty then our script could not find the
    # outline and we should be notified
    if receiptCnt is None:
        raise Exception(("Could not find receipt outline. "
            "Try debugging your edge detection and contour steps."))
    
    if debug:
        output = image.copy()
        cv2.drawContours(output, [receiptCnt], -1, (0, 255, 0), 2)
        cv2.imshow("Receipt Outline", output)
        cv2.waitKey(0)
        
    # apply a four-point perspective transform to the *original* image to
    # obtain a top-down bird's-eye view of the receipt
    receipt = four_point_transform(frame, receiptCnt.reshape(4, 2) * ratio)
    receipt = cv2.cvtColor(receipt, cv2.COLOR_BGR2RGB)
    
    if debug:
        # show transformed image
        cv2.imshow("Receipt Transform", imutils.resize(receipt, width=500))
        cv2.waitKey(0)

    pya.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"
    text = pya.image_to_string(receipt, config="--psm 4")
    # text = text.replace("\n", " ")
    
    return text
    
def to_text(frame, debug=None):
    """Wraps Tesseract OCR. Extract text from frame that were originally PDF
    Parameters
    ----------
    frame : str
        path of electronic invoice in JPG or PNG format
    debug : 
        enables debug visualization
    Returns
    -------
    extracted_str : str
        returns extracted text from image in JPG or PNG format
    """
    pya.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

    # first we need to convert the image from color to gray scale
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # sharpen text for OCR detection
    frame = cv2.filter2D(frame, ddepth=-1, kernel=kernel)
    #fliping the white and black helps with OCR Tesseract to be cleaner
    # frame = cv2.bitwise_not(frame)
    # #then we need to blur the image, using median blur was the best choice
    # frame = cv2.medianBlur(frame,5)
    
    if debug:
        cv2.imshow('processed_frame', frame)
        cv2.waitKey(0)
        
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, frame)
    text = pya.image_to_string(frame, config="--psm 4")
    # text = text.replace("\n", " ")
    os.remove(filename)

    return text

if __name__ == "__main__":
    import imageio
    from pdf2image import convert_from_path
    
    receipt_file = "C:/Users/Leonard/spyder-workspace/receiptScanner/docs/receipt1.pdf"
    images = convert_from_path(receipt_file)
     
    for idx, img in enumerate(images):
        images[idx] = np.array(img)
        
    extracted_txts = ""
    for img in images:
        detected_txts = to_text(img)
        extracted_txts += detected_txts