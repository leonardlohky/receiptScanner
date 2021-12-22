# -*- coding: utf-8 -*-
import os
import cv2
import shutil
import argparse
import imutils
import logging
import numpy as np

from pdf2image import convert_from_path

from extract.loader import read_templates
from extract import extracter
from cleaner import cleaner
from receipt_input import tesseract

logger = logging.getLogger(__name__)

def create_parser():
    parser = argparse.ArgumentParser(description='Extract structured data from PDF files')
        
    parser.add_argument(
        "--template-folder",
        "-t",
        dest="template_folder",
        help="Folder containing invoice templates in yml file. Always adds built-in templates.",
    )
        
    parser.add_argument(
        "--copy",
        "-c",
        dest="copy",
        help="Copy and rename processed PDFs to specified folder.",
    )

    parser.add_argument(
        "--move",
        "-m",
        dest="move",
        help="Move and rename processed PDFs to specified folder.",
    )
    
    parser.add_argument(
        "input_files",
        type=argparse.FileType("r"),
        nargs="+",
        help="File or directory to analyze.",
    )
        
    return parser

def pdf_to_img(filename):
    # Store Pdf with convert_from_path function
    images = convert_from_path(filename)
     
    for idx, img in enumerate(images):
        images[idx] = np.array(img)
        
    return images
    
def extract_data(receipt_file, templates):
    if not templates:
        templates = read_templates()
    
    imgs = pdf_to_img(receipt_file)
    
    extracted_txts = ""
    for img in imgs:
        detected_txts = tesseract.to_text(img)
        extracted_txts += detected_txts
    
    extracted_str = cleaner.clean_text(extracted_txts)
    
    for t in templates:
        optimized_str = t.prepare_input(extracted_str)

        if t.matches_input(optimized_str):
            logger.info("Using %s template", t["template_name"])
            return t.extract(optimized_str)
        
    logger.error("No template for %s", receipt_file)
    return False

def main(args=None):
    if args is None:
        parser = create_parser()
        args = parser.parse_args()
        
    templates = []
    # Load templates from external folder if set.
    if args.template_folder:
        templates += read_templates(os.path.abspath(args.template_folder))
    
    output = []
    for f in args.input_files:
        res = extract_data(f.name, templates=templates)
        if res:
            logger.info(res)
            output.append(res)
            if args.copy:
                filename = args.filename.format(
                    date=res["date"].strftime("%Y-%m-%d"),
                    invoice_number=res["invoice_number"],
                    desc=res["desc"],
                )
                shutil.copyfile(f.name, os.path.join(args.copy, filename))
            if args.move:
                filename = args.filename.format(
                    date=res["date"].strftime("%Y-%m-%d"),
                    invoice_number=res["invoice_number"],
                    desc=res["desc"],
                )
                shutil.move(f.name, os.path.join(args.move, filename))
        f.close()

    print(output[0])
    
if __name__ == "__main__":
    main()