import re

import pandas as pd
from paddleocr import PaddleOCR
from PyPDF2 import PdfReader


def shopee(pdf_file, df_day_du):
    reader = PdfReader(r"pdf_file\shopee1.pdf")
    result_dict = {
        'Mã vận đơn' : [],
        'Mã đơn hàng' : [],
        'Mã sản phẩm' : [],
        'Dòng máy' : []
    }
    ocr = PaddleOCR(show_log=False)
    file = open('result.txt', 'w', encoding='utf-8')
    for n, page in enumerate(reader.pages[:]):
        list_tsp = []
        page_text = page.extract_text().split('\n')
        for idx, i in enumerate(page_text):
            i = re.sub('\W+', '', i)
            if i.endswith('Mãđơnhàng') or i.endswith('Mãvậnđơn'):
                continue
            if 'Mãđơnhàng' in i:
                ma_van_don = i.split('Mãđơnhàng')[-1]
                for a in range(len(df_day_du['Mã vận đơn'])):
                    if df_day_du['Mã vận đơn'][a] == ma_van_don:
                        result_dict['Mã vận đơn'].append(ma_van_don)
                        result_dict['Mã đơn hàng'].append(df_day_du['Mã đơn hàng'][a])
                        result_dict['Mã sản phẩm'].append(df_day_du['Mã sản phẩm'][a])
                        result_dict['Dòng máy'].append(df_day_du['Dòng máy'][a])
                break
            if 'Mãvậnđơn' in i:
                ma_van_don = i.split('Mãvậnđơn')[-1]
                for a in range(len(df_day_du['Mã vận đơn'])):
                    if df_day_du['Mã vận đơn'][a] == ma_van_don:
                        result_dict['Mã vận đơn'].append(ma_van_don)
                        result_dict['Mã đơn hàng'].append(df_day_du['Mã đơn hàng'][a])
                        result_dict['Mã sản phẩm'].append(df_day_du['Mã sản phẩm'][a])
                        result_dict['Dòng máy'].append(df_day_du['Dòng máy'][a])
                break
            # break

    return pd.DataFrame(result_dict)

            
if __name__ == '__main__':
    shopee('a')

