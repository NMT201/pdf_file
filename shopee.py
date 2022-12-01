import re
import json
import difflib
import pandas as pd
from paddleocr import PaddleOCR
from PyPDF2 import PdfReader


def shopee(pdf_file, df_day_du):
    reader = PdfReader(pdf_file)
    result_dict = {
        'Mã vận đơn' : [],
        'Mã đơn hàng' : [],
        'Mã sản phẩm' : [],
        'Dòng máy' : []
    }
    ocr = PaddleOCR(show_log=False)
    for n, page in enumerate(reader.pages[:]):
        list_tsp = []
        page_text = page.extract_text().split('\n')
        extra_data = json.load(open(r'data\extra_data.json', 'r', encoding='utf-8'))
        
        for idx, i in enumerate(page_text):
            i = re.sub('\W+', '', i)
            if i.endswith('Mãđơnhàng') or i.endswith('Mãvậnđơn'):
                continue
            if 'Mãđơnhàng' in i:
                ma_don_hang = i.split('Mãđơnhàng')[-1]
                for a in range(len(df_day_du['Mã vận đơn'])):
                    if df_day_du['Mã đơn hàng'][a] == ma_don_hang:
                        msp = df_day_du['Mã sản phẩm'][a]
                        if msp == 'null':
                            for j in range(len(extra_data['Tên sản phẩm'])):
                                if difflib.SequenceMatcher(None,extra_data['Tên sản phẩm'][j] ,df_day_du['Tên sản phẩm'][a]).ratio() > 0.9: 
                                    msp = extra_data['Mã sản phẩm'][j]
                        
                        result_dict['Mã vận đơn'].append(df_day_du['Mã vận đơn'][a])
                        result_dict['Mã đơn hàng'].append(ma_don_hang)
                        result_dict['Mã sản phẩm'].append(msp)
                        result_dict['Dòng máy'].append(df_day_du['Dòng máy'][a])
                break
            if 'Mãvậnđơn' in i:
                ma_don_hang = i.split('Mãvậnđơn')[-1]
                for a in range(len(df_day_du['Mã vận đơn'])):
                    if df_day_du['Mã đơn hàng'][a] == ma_don_hang:
                        msp = df_day_du['Mã sản phẩm'][a]
                        if msp == 'null':
                            for j in range(len(extra_data['Tên sản phẩm'])):
                                if difflib.SequenceMatcher(None,extra_data['Tên sản phẩm'][j] ,df_day_du['Tên sản phẩm'][a]).ratio() > 0.9: 
                                    msp = extra_data['Mã sản phẩm'][j]
                        result_dict['Mã vận đơn'].append(df_day_du['Mã vận đơn'][a])
                        result_dict['Mã đơn hàng'].append(ma_don_hang)
                        result_dict['Mã sản phẩm'].append(df_day_du['Mã sản phẩm'][a])
                        result_dict['Dòng máy'].append(df_day_du['Dòng máy'][a])
                break
            # break
    return pd.DataFrame(result_dict)

            
if __name__ == '__main__':
    shopee('a')

