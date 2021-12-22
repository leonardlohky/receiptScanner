# -*- coding: utf-8 -*-
import re

def remove_url(text):
    return re.sub(r'https\S+', '', text)

def remove_emails(text):
    return re.sub(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+', '', text)

def remove_phone_nums(text):
    return re.sub(r'@"[^\d]"', '', text)
                  
def clean_text(text):
    text = remove_url(text)
    text = remove_emails(text)
    # text = remove_phone_nums(text)
    
    return text