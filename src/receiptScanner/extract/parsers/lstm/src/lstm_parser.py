# -*- coding: utf-8 -*-
import regex
import argparse
import torch
from my_data import MyDataset, VOCAB
from my_models import MyModel0
from my_utils import pred_to_dict
from collections import OrderedDict
import json

class LSTMParser():
    def __init__(self, hidden_size=256, device='cpu'):
        self.device = device
        
        self.model = MyModel0(len(VOCAB), 16, hidden_size).to(self.device)
        self.model.load_state_dict(torch.load("model.pth"))
        
    def prepare_input(self, text):
        text_tensor = torch.zeros(len(text), 1, dtype=torch.long)
        text_tensor[:, 0] = torch.LongTensor([VOCAB.find(c) for c in text])

        text_tensor[text_tensor < 0] = 0
        return text_tensor.to(self.device)
    
    def parse(self, text):
        with torch.no_grad():
            text_tensor = self.prepare_input(text)
            oupt = self.model(text_tensor)
            prob = torch.nn.functional.softmax(oupt, dim=2)
            prob, pred = torch.max(prob, dim=2)
    
            prob = prob.squeeze().cpu().numpy()
            pred = pred.squeeze().cpu().numpy()
            
            result = pred_to_dict(text, pred, prob)
            
            return result

    def clean_company(self, textline: str):
        """
        Given a string line, this function will attempt to remove unwanted string that lowers the F1-score.
        Args:
            textline: The string line.
        Returns:
            A cleaned company.
            
        """
        
        # Take only unique words in a given text line.
        # If this text line contains the character ', it is replaced by an empty space.
        textline = " ".join(OrderedDict.fromkeys(textline.replace("'", "").strip().split()))
        
        # A case where the regex below will fail.
        cond = bool(regex.search(r"[A-Z]+[0-9]+", textline.strip()))
        if cond:
            return textline
        
        matched = regex.search(r"(\d+[^0-9]*[A-Z]+)$", textline.strip())
        if matched is None:
            matched = regex.search(r"\(\d+[^0-9]*[A-Z]+\)$", textline.strip())
            if matched is None:
                matched = regex.search(r"\([A-Z]{1,}$", textline.strip())
                if matched is None:
                    return textline.strip()
        idx = textline.find(matched.group())
        textline = textline[:idx]
        return textline.strip()

if __name__ == "__main__":
    import imageio
    import numpy as np
    from pdf2image import convert_from_path
    from tesseract import to_text, to_text_img
    
    receipt_file = "C:/Users/Leonard/spyder-workspace/receiptScanner/docs/007.jpg"
    img = imageio.imread(receipt_file)
    img = np.array(img)
    
    extracted_txts = to_text(img)
    extracted_txts = "".join([s for s in extracted_txts.strip().splitlines(True) if s.strip()])
    
    # images = convert_from_path(receipt_file)
     
    # for idx, img in enumerate(images):
    #     images[idx] = np.array(img)
        
    # extracted_txts = ""
    # for img in images:
    #     detected_txts = to_text(img)
    #     extracted_txts += detected_txts
        
    # extracted_txts = "".join([s for s in extracted_txts.strip().splitlines(True) if s.strip()])
    
    parser = LSTMParser()
    res = parser.parse(extracted_txts)