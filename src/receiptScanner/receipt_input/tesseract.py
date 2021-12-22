# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
import pytesseract as pya

from PIL import Image

kernel = np.array([[0, -1, 0],
                   [-1, 5,-1],
                   [0, -1, 0]])

def to_text(frame):
    """Wraps Tesseract OCR.
    Parameters
    ----------
    frame : str
        path of electronic invoice in JPG or PNG format
    Returns
    -------
    extracted_str : str
        returns extracted text from image in JPG or PNG format
    """
    pya.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

    #first we need to convert the image from color to gray scale
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # sharpen text for OCR detection
    frame = cv2.filter2D(frame, ddepth=-1, kernel=kernel)
    #fliping the white and black helps with OCR Tesseract to be cleaner
    frame = cv2.bitwise_not(frame)
    # #then we need to blur the image, using median blur was the best choice
    # frame = cv2.medianBlur(frame,5)

    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, frame)
    text = pya.image_to_string(frame, config="--psm 4")
    text = text.replace("\n", " ")
    os.remove(filename)
    # print(text)

    return text