# -*- coding: utf-8 -*-
import os
import cv2
import shutil
import argparse
import imutils
import logging
import imageio
import numpy as np

from pdf2image import convert_from_path

from extract.loader import read_templates
from extract import extracter
from cleaner import cleaner
from receipt_input import tesseract

from output import to_csv
from output import to_json

logger = logging.getLogger(__name__)

output_mapping = {"csv": to_csv, "json": to_json, "none": None}

def create_parser():
    parser = argparse.ArgumentParser(description='Extract structured data from PDF files')
        
    parser.add_argument(
        "--output-format",
        choices=output_mapping.keys(),
        default="csv",
        help="Choose output format. Default: csv",
    )
        
    parser.add_argument(
        "--output-date-format",
        dest="output_date_format",
        default="%Y-%m-%d",
        help="Choose output date format. Default: %%Y-%%m-%%d (ISO 8601 Date)",
    )
        
    parser.add_argument(
        "--doc-type",
        dest="doc_type",
        default="receipt",
        help="Document type expected. Default: receipt",
    )
        
    parser.add_argument(
        "--output-name",
        "-o",
        dest="output_name",
        default="receipts-output",
        help="Custom name for output file. Extension is added based on chosen format.",
    )
        
    parser.add_argument(
        "--template-folder",
        "-t",
        dest="template_folder",
        help="Folder containing invoice templates in yml file. Always adds built-in templates.",
    )
       
    parser.add_argument(
        "--debug", dest="debug", action="store_true", help="Enable debug information."
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
        nargs="+",
        help="Files or directory to analyze.",
    )
        
    return parser

def pdf_to_img(filename):
    # Store Pdf with convert_from_path function
    images = convert_from_path(filename)
     
    for idx, img in enumerate(images):
        images[idx] = np.array(img)
        
    return images

def prepare_files(input_files):
    all_files = []
    
    for f in input_files:
        if os.path.isfile(f):
            all_files.append(f)
            logger.info("Detected file: %s" % f)
        elif os.path.isdir(f):
            for (dirpath, dirnames, filenames) in os.walk(f):
                for name in sorted(filenames):
                    all_files.append(os.path.join(dirpath, name))
                    logger.info("Detected file: %s" % os.path.join(dirpath, name))
                break
            
    return all_files

def extract_data(receipt_file, templates, doc_type):
    if not templates:
        templates = read_templates(None, doc_type)
    
    _, ext = os.path.splitext(receipt_file)
    if ext == ".pdf":
        imgs = pdf_to_img(receipt_file)
        
        extracted_txts = ""
        for img in imgs:
            detected_txts = tesseract.to_text(img)
            extracted_txts += detected_txts
    else:
        img = imageio.imread(receipt_file)
        img = np.array(img)
        
        extracted_txts = ""
        try:
            detected_txts = tesseract.to_text_img(img)
            extracted_txts += detected_txts
        except Exception:
            detected_txts = tesseract.to_text(img)
            extracted_txts += detected_txts
    
    if not extracted_txts:
        logger.error("No extractable text for %s", receipt_file)
        return False
    
    # clean extracted text
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
        
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        
    output_module = output_mapping[args.output_format]
            
    templates = []
    # Load templates from external folder if set.
    if args.template_folder:
        templates += read_templates(os.path.abspath(args.template_folder), args.doc_type)
    else:
        templates += read_templates(None, args.doc_type)
    
    output = []

    all_files = prepare_files(args.input_files)
    
    for f in all_files:
        res = extract_data(f, templates=templates, doc_type=args.doc_type)
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
        
    if output_module is not None and res:
        output_module.write_to_file(output, args.output_name, args.output_date_format)
    
if __name__ == "__main__":
    main()