import re
import json
import difflib
import numpy as np
import pandas as pd
from pyzbar.pyzbar import decode
from pdf2image import convert_from_bytes, convert_from_path

def lazada(pdf_file, df_day_du):
    with open(r'data\ignored_msp.json', 'r') as file:
        null_msp = json.load(file)['Mã sản phẩm']
    # images = convert_from_path(pdf_file)
    images = convert_from_bytes(pdf_file.read())#, poppler_path=r'C:\Program Files (x86)\poppler-0.68.0\bin')
    result_dict = {
        'Số đơn' : [],
        'Mã bắn vạch' : [],
        'Mã sản phẩm' : [],
        'Dòng máy' : []
    }
    
    null_dict = {
        'Số đơn' : [],
        'Mã bắn vạch' : [],
        'Tên sản phẩm' : [],
        'Mã sản phẩm' : [],
    }

    for idx, i in enumerate(images):
        ma_ban_vach = ''
        image = i.crop((0, 300, 3000, 600))
        detectedBarcodes = decode(image)
        if len(detectedBarcodes) > 0:
            ma_ban_vach = str(detectedBarcodes[0].data)[2:-1]
        extra_data = json.load(open(r'data\extra_data.json', 'r', encoding='utf-8'))
        if ma_ban_vach != '':
            for i in range(len(df_day_du['Mã bắn vạch'])):
                if str(df_day_du['Mã bắn vạch'][i]) == str(ma_ban_vach).strip(' '):
                    msp = df_day_du['Mã sản phẩm'][i]
                    if msp == 'null':
                        for j in range(len(extra_data['Tên sản phẩm'])):
                            if difflib.SequenceMatcher(None,extra_data['Tên sản phẩm'][j] ,df_day_du['Tên sản phẩm'][i]).ratio() > 0.9: 
                                msp = extra_data['Mã sản phẩm'][j]
                    if msp in null_msp:
                        msp = 'null'
                    result_dict['Số đơn'].append(df_day_du['Số đơn'][i])
                    result_dict['Mã bắn vạch'].append(df_day_du['Mã bắn vạch'][i])
                    result_dict['Mã sản phẩm'].append(msp)
                    result_dict['Dòng máy'].append(df_day_du['Dòng máy'][i])
    return pd.DataFrame(result_dict)

if __name__ == '__main__':
    from lazada_list import lazada_list
    
    df = lazada_list(r"C:\Users\19522\Desktop\PDF\pdf_file_1\lazada_list.pdf")
    lazada(r'C:\Users\19522\Desktop\PDF\pdf_file_1\lazada.pdf', df)