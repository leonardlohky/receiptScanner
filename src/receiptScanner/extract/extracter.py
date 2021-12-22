# -*- coding: utf-8 -*-

import re

def find_amounts(text):
    amounts = re.findall(r'\d+\.\d{2}\b', text)
    floats = [float(amount) for amount in amounts]
    unique_amts = list(dict.fromkeys(floats))
    
    return unique_amts

def find_names(text):
    nameExp = r"^[\w'\-,.][^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:[\]]{2,}"
    names = re.findall(nameExp, text)
    
    return names

def find_emails(text):
    emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text)
    unique_emails = list(dict.fromkeys(emails))
    
    return unique_emails

def find_reeipt_ID(text):
    return re.findall(r":([^,]*)", text)
    