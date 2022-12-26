import os
import json
import re

import camelot
import matplotlib.pyplot as plt
from pdf2image import convert_from_path
from PyPDF2 import PdfReader, PdfFileWriter

ignore_list = ['Salework', 'salework', 'THÔNG TIN', 'Ngày đặt hàng', 'Đơn vị vận chuyển', 'Tên khách hàng', 'SĐT', 'Địa chỉ', 'Ghi chú khách hàng', 'STT', 
            'Tên Sản phẩm', 'Phân loại', 'Số lượng', 'Thành tiền', 'Thông tin']

def check_msp(msp):
    if not msp.isalpha():
        if msp[0].isalpha():
            return True
    return False

def get_dm(msp_dm, dong_may_available):
    msp_dm = msp_dm.lower()
    dong_may = 'null'
    maybe_msp = 'null'
    for dm in dong_may_available:
        if dm in msp_dm.replace(' ', ''):
            dong_may = dm
            if ',' in msp_dm:
                maybe_msp = msp_dm.split(',')[0] if dong_may in msp_dm.split(',')[1] else msp_dm.split(',')[1]
            return dong_may, maybe_msp
    return dong_may, maybe_msp
    
def get_msp(maybe_msp, tsp):
    maybe_msp = re.sub('\W+', ' ', maybe_msp).split()
    msp = 'null'
    for word in maybe_msp:
        if check_msp(word):
            msp = word
            break
    if len(msp) < 3:
        msp = "null"
    if msp == "null":
        if check_msp(re.sub('\W+', ' ', tsp).split()[-1]):
            msp = re.sub('\W+', ' ', tsp).split()[-1]
            for i in ['a', 'b', 'c']:
                if i in maybe_msp:
                    msp += i
                    break
    return msp
    
def lazada_list(pdf_file):
    reader = PdfReader(pdf_file)
    pdf_writer = PdfFileWriter()
    pdf_out = open(r'data\lazada.pdf', 'wb')
    for pagenum in range(reader.numPages):
        page = reader.getPage(pagenum)
        pdf_writer.addPage(page)
        pdf_writer.write(pdf_out)
    pdf_out.close()
    result_dict = {
        'Số đơn' : [],
        'Mã bắn vạch' : [],
        'Mã sản phẩm' : [],
        'Dòng máy' : [],
        'Tên sản phẩm' : []
    }
    with open(r'data\ignored_msp.json', 'r') as file:
        null_msp = json.load(file)['Mã sản phẩm']
        
    with open(r'data\dong_may.txt', 'r') as file:
        dong_may_available = file.read().split('\n')
    
    for p_idx, page in enumerate(reader.pages):
        list_text = page.extract_text().split('\n')
        list_avai_text = list_text.copy()
        if len(list_text) > 1:
            if 'Mã đơn hàng:' not in page.extract_text():
                list_avai_text = page.extract_text().split('\n')[1:-1]
                if len(list_avai_text) > 0: 
                    list_avai_text[0] = list_avai_text[0].replace('https://stock.salework.net/orders ', '')
                    list_avai_text = [' ', ' '] + list_avai_text
                else:
                    continue
            else:
                for idx, text in enumerate(list_text):
                    for ignore in ignore_list:
                        if ignore in text:
                            if text in list_avai_text:
                                list_avai_text.remove(text)
                            if ignore == 'Địa chỉ':
                                list_avai_text.remove(list_text[idx+1])
                            break
        so_don = re.sub('\W+', '',list_avai_text[0].replace('Mã đơn hàng:', '')) if list_avai_text[0] != ' ' else result_dict['Số đơn'][-1]
        ma_ban_vach = re.sub('\W+', '',list_avai_text[1]) if list_avai_text[1] != ' ' else result_dict['Mã bắn vạch'][-1]
        
        table = camelot.read_pdf(r'data\lazada.pdf', pages=str(p_idx+1))
        
        list_dong_may = []
        list_msp = []
        list_tsp = []
        
        if len(table) > 0:
            for index, row in table[0].df.iterrows():
                if row[0] == 'STT':
                    continue
                tsp = row[1].replace('\n', ' ')
                msp_dm =  row[2].replace('\n', ' ')
                
                dong_may, maybe_msp = get_dm(msp_dm, dong_may_available)
                msp = get_msp(maybe_msp, tsp)
                so_luong = int(row[3]) 
                
                list_dong_may += [dong_may] * so_luong
                list_msp += [msp] * so_luong
                list_tsp += [tsp] * so_luong
        else:
            continue
        
        result_dict['Số đơn'] += [so_don] * len(list_msp)
        result_dict['Mã bắn vạch'] += [ma_ban_vach] * len(list_msp)
        result_dict['Mã sản phẩm'] += list_msp
        result_dict['Dòng máy'] += list_dong_may
        result_dict['Tên sản phẩm'] += list_tsp
        
    if not os.path.exists(r'data\lazada_list.json'):
        with open(r'data\lazada_list.json', 'w+', encoding='utf-8') as file:
            json.dump(result_dict, file)
    else:
        with open(r'data\lazada_list.json', 'r', encoding='utf-8') as file:
            exists_data = json.load(file)
            if str(result_dict['Số đơn'])[1:-1] not in str(exists_data['Số đơn']):
                exists_data['Số đơn'] += result_dict['Số đơn']
                exists_data['Mã bắn vạch'] += result_dict['Mã bắn vạch']
                exists_data['Mã sản phẩm'] += result_dict['Mã sản phẩm']
                exists_data['Dòng máy'] += result_dict['Dòng máy']
                exists_data['Tên sản phẩm'] += result_dict['Tên sản phẩm']
                with open(r'data\lazada_list.json', 'w', encoding='utf-8') as file:
                    json.dump(exists_data, file)

if __name__ == "__main__":
    lazada_list(r"C:\Users\19522\Desktop\New folder\pdf_file\pdf_file_1\lazada_list.pdf")