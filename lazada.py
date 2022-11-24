import re
import numpy as np
import pandas as pd
from paddleocr import PaddleOCR
from pdf2image import convert_from_bytes, convert_from_path

def lazada(pdf_file, df_day_du):
    ocr = PaddleOCR(use_gpu=True, show_log=False) # The model file will be downloaded automatically when executed for the first time
    
    images = convert_from_bytes(pdf_file.read(), poppler_path=r'C:\Program Files (x86)\poppler-0.68.0\bin')
    result_dict = {
        'Số đơn' : [],
        'Mã bắn vạch' : [],
        'Mã sản phẩm' : [],
        'Dòng máy' : []
    }

    for i in images:
        image = np.array(i)
        result = ocr.ocr(image)
        so_don = ''
        for line in result[0]:
            text = re.sub('\W+', '', line[1]).lower()
            if 'sodon' in text[0]:
                so_don = text[0].split(':')[-1]
                break
        if so_don != '':
            for i in range(len(df_day_du['Số đơn'])):
                if str(df_day_du['Số đơn'][i]) == str(so_don).strip(' '):
                    result_dict['Số đơn'].append(df_day_du['Số đơn'][i])
                    result_dict['Mã bắn vạch'].append(df_day_du['Mã bắn vạch'][i])
                    result_dict['Mã sản phẩm'].append(df_day_du['Mã sản phẩm'][i])
                    result_dict['Dòng máy'].append(df_day_du['Dòng máy'][i])
    
    return pd.DataFrame(result_dict)

if __name__ == '__main__':
    from lazada_list import lazada_list
    
    df = lazada_list(r"C:\Users\19522\Desktop\PDF\pdf_file_1\lazada_list.pdf")
    lazada(r'C:\Users\19522\Desktop\PDF\pdf_file_1\lazada.pdf', df)