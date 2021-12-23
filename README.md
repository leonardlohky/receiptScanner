# receiptScanner

## About
Almost all of us have gone through the tedious process of filing expense claims,
which involves copying over information from the receipt to the claims form. Not
only is this process painstaking, but made even worse when you cannot simply Ctrl-C
and Ctrl-V information from the receipt because the file is an image.

I myself have been through this before, as such I decided to make receiptScanner; An
Automatic Receipt Parser to address this. receiptScanner is able to extract necessary
information from a receipt that you will most likely need to file for expense claims,
such as "Receipt No, Total Amount Paid, Date of Expense made" etc. This information
will be saved as a .csv file

## Acknowledgement
This repo's source code is heavily based on the [invoice2data](https://github.com/invoice-x/invoice2data),
so I would like to thank the authors for creating the original package.

## Getting Started
### 1. Requirements.
Install the necessary required packages through the provided `requirements.txt`
file using Anaconda prompt.
```
pip install -r requirements.txt
```

This repo uses Tesseract-OCR, to install Tesseract-OCR for Windows, visit the 
following [link](https://github.com/UB-Mannheim/tesseract/wiki) and download the 
appropriate  Tesseract installer .exe depending on your computer specs. If 
Tesseract-OCR is successfully installed, you should find a folder labelled 
`Tesseract-OCR` under `C:\Program Files\Tesseract-OCR`.

Note that some have reported it being found under `C:\Program Files (x86)` or
`C:\Users\USER\AppData\Local\Tesseract-OCR` instead. Do take note if you are
unable to locate it under `C:\Program Files` as originally expected.

### 2. Installation.
- Clone this repo:
```
git clone https://github.com/leonardlohky/receiptScanner
```

## Usage
Similar to the original `invoice2data` package, receipt scanner extracts texts
from receipt PDF files or images using Tesseract. After that, it searches for
regex in the extracted text using a YAML-based template system to extract the
necessary field data. It then saves the result as a CSV file.

To run the application, navigate to the location of `main.py` script and type 
in the following in an Anaconda prompt.
```
cd src\receiptScanner
python main.py <INPUT_FILES_OR_FOLDER>

#Example
python main.py .../docs/receipt1.pdf
python main.py .../doc/receipts_folder
```

## License
Distributed under the [MIT License](LICENSE)