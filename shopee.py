import re
import json
import difflib
import pandas as pd
from pyzbar.pyzbar import decode
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes


def shopee(pdf_file, df_day_du):
    images = convert_from_bytes(pdf_file.read(), poppler_path=r'C:\Program Files (x86)\poppler-0.68.0\bin')
    with open(r'data\ignored_msp.json', 'r') as file:
        null_msp = json.load(file)['Mã sản phẩm']
    reader = PdfReader(pdf_file)
    
    result_dict = {
        'Mã vận đơn' : [],
        'Mã đơn hàng' : [],
        'Mã sản phẩm' : [],
        'Dòng máy' : []
    }
    for n, page in enumerate(reader.pages):
        list_tsp = []
        page_text = page.extract_text().split('\n')
        extra_data = json.load(open(r'data\extra_data.json', 'r', encoding='utf-8'))
        detectedBarcodes = decode(images[n])
        ma_don_hang = str(detectedBarcodes[0].data)[2:-1]
        for a in range(len(df_day_du['Mã vận đơn'])):
            if df_day_du['Mã đơn hàng'][a] == ma_don_hang:
                msp = df_day_du['Mã sản phẩm'][a]
                if msp == 'null':
                    for j in range(len(extra_data['Tên sản phẩm'])):
                        if difflib.SequenceMatcher(None,extra_data['Tên sản phẩm'][j] ,df_day_du['Tên sản phẩm'][a]).ratio() > 0.9: 
                            msp = extra_data['Mã sản phẩm'][j]
                if msp.lower() in null_msp:
                    msp = 'null'
                result_dict['Mã vận đơn'].append(df_day_du['Mã vận đơn'][a])
                result_dict['Mã đơn hàng'].append(ma_don_hang)
                result_dict['Mã sản phẩm'].append(msp)
                result_dict['Dòng máy'].append(df_day_du['Dòng máy'][a])

                        
             
    return pd.DataFrame(result_dict)

            
if __name__ == '__main__':
    shopee('a')

