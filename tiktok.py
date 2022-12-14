import pandas as pd
import re
import json
import numpy as np
import camelot
from pyzbar.pyzbar import decode
from PyPDF2 import PdfReader, PdfFileWriter
from pdf2image import convert_from_bytes

def check_msp(msp):
    if not msp.isalpha():
        if msp[0].isalpha():
            return True
    return False

def get_msp(s, maybe_msp, list_dong_may):
    for idx, char in enumerate(s):
        if idx > 0 and idx < len(s)-1:
            if char.isdigit() and s[idx-1].isdigit() and s[idx+1].isalpha():
                msp = s[:idx+1] 
                if 'a' == s[idx+1]:
                    msp += 'a'
                elif 'b' == s[idx+1]:
                    msp += 'b'
                elif 'c' == s[idx+1]:
                    msp += 'c'
                if ',' in msp :
                    msp = msp.split(',')[-1]
                if len(re.findall('\d+', msp)[-1]) > 4:
                    if (re.findall('\d+', msp)[-1][-2:] + maybe_msp[-1]).split(',')[0] in list_dong_may:
                        msp = msp[:-2]
                return msp
    return s

def tiktok(pdf_file):
    images = convert_from_bytes(pdf_file.read(), poppler_path=r'C:\Program Files (x86)\poppler-0.68.0\bin')
    reader = PdfReader(pdf_file)
    pdf_writer = PdfFileWriter()
    pdf_out = open(r'data\tiktok.pdf', 'wb')
    for pagenum in range(reader.numPages):
        page = reader.getPage(pagenum)
        pdf_writer.addPage(page)
        pdf_writer.write(pdf_out)
    pdf_out.close()
    result_dict = {
        'Mã đơn' : [],
        'Mã bắn vạch' : [],
        'Mã sản phẩm' : [],
        'Dòng máy' : []
    }
    with open(r'data\ignored_msp.json', 'r') as file:
        null_msp = json.load(file)['Mã sản phẩm']

    ma_ban_vach = ''
    for n, page in enumerate(reader.pages[:]):
        ma_don = ''
        page_text = page.extract_text()
        if page_text == '':
            image = images[n]
            detectedBarcodes = decode(images[n])
            ma_ban_vach = str(detectedBarcodes[0].data)[2:-1]
            continue
        
        list_msp = []
        list_dong_may = []
        list_so_luong = []
        if '[Seller SKU]' in page_text:
            table = camelot.read_pdf(r'data\tiktok.pdf', pages=str(n+1), flavor='stream')
            msp_dm = ''
            so_luong = 0
            add_msp_dm = True
            for index, row in table[0].df.iterrows():
                if index < 2:
                    continue
                if row[2].isdigit():
                    so_luong = int(row[2])

                if row[1] != '':
                    msp_dm += row[1]
                else:
                    if msp_dm != '':
                        msp_dm = msp_dm.split('[')[0].strip()
                        dong_may = msp_dm.split(',')[-1]
                        
                        maybe_msp = msp_dm.split(',')[0].split()
                        msp = 'null'
                        for m in maybe_msp:
                            if check_msp(m):
                                msp = m
                        if msp in null_msp:
                            msp = 'null'
                        list_msp.append(msp)
                        list_dong_may.append(dong_may)
                        msp_dm = ''
                    

        else:
            list_tsp = page_text.split('\n')
            qty_idx = list_tsp.index('Qty')
            for i in list_tsp:
                if 'Order ID:' in i:
                    ma_don = re.sub('\W+', '', i.replace('Order ID: ', ''))
                    break
            if qty_idx != len(list_tsp)-1:
                list_tsp = list_tsp[qty_idx+1:]
            else:
                list_tsp = list_tsp[:-4]
            one_num_idxes = []
            for idx, i in enumerate(list_tsp):
                if i.isdigit():
                    if int(i) < 5:
                        one_num_idxes.append(idx)
                        
            tsp_merge = []
            prev = 0
            

            for num_idx in one_num_idxes:
                temp_tsp = list_tsp[prev:num_idx]
                tsp_merge.append(temp_tsp)
                prev=num_idx
                dong_may = 'null'
                if ',' in temp_tsp[-1]:
                    dong_may = temp_tsp[-1].split(',')[-1]
                    if dong_may == 'x' and 'proma' in temp_tsp[-2]:
                        if temp_tsp[-2].split(',')[-1] != 'proma':
                            dong_may = temp_tsp[-2].split(',')[-1] + dong_may
                else:
                    dong_may = temp_tsp[-1]
                    if dong_may == 'x' and 'proma' in temp_tsp[-2]:
                        if temp_tsp[-2].split(',')[-1] != 'proma':
                            dong_may = temp_tsp[-2].split(',')[-1] + dong_may
                    elif ',' in temp_tsp[-2]:
                        dong_may = temp_tsp[-2].split(',')[-1] + dong_may
                list_so_luong.append(int(list_tsp[num_idx]))
                list_dong_may += [dong_may]*int(list_tsp[num_idx])
            list_maybe_msp = []
            for tsp in tsp_merge:
                maybe_msp = []
                for text in tsp:
                    if ' ' in text or len(text) > 20:
                        continue
                    else:
                        if not text.isalpha():
                            if text[0].isalpha():
                                maybe_msp.append(text)
                # print(str(n+1) + str(maybe_msp))
                list_maybe_msp.append(maybe_msp)

            for idx_m, maybe_msp in enumerate(list_maybe_msp):
                if len(maybe_msp) > 1:
                    dm = list_dong_may[idx_m]
                    maybe_msp = [k.replace(dm, '') if k.endswith(dm) and len(dm) > 2 else k for k in maybe_msp ]
                    if dm in (maybe_msp[-2] + maybe_msp[-1]):
                        if dm not in maybe_msp[-2] and dm not in maybe_msp[-1]:
                            if len(maybe_msp) == 2:
                                maybe_msp = [(maybe_msp[-2] + maybe_msp[-1]).replace(dm,'')]
                            else:
                                maybe_msp = maybe_msp[:-2] + [(maybe_msp[-2] + maybe_msp[-1]).replace(dm,'')]
                else:
                    for dm in list_dong_may:
                        if (dm + ',' + dm) in maybe_msp[0]:
                            if len(maybe_msp[0].replace((dm + ',' + dm), '')) >= 4:
                                maybe_msp = [maybe_msp[0].replace((dm + ',' + dm),'')]

                msp = 'null'
                for idx, text in enumerate(maybe_msp):
                    if ',' in text:
                        msp = text.split(',')[0]
                        if not check_msp(msp):
                            msp = 'null'
                        
                        for i in maybe_msp[idx+1:]:
                            if list_dong_may[idx_m] in i:
                                i = i.replace(list_dong_may[idx_m], '')
                            for c in i:
                                if c in 'abc':
                                    msp += c
                                    break
                            if msp[-1] in 'abc':
                                break
                        
                    else:
                        msp = text
                
                    num_in_msp = re.findall('\d+', msp.split(',')[0])
                    if len(num_in_msp) > 0:
                        if len(num_in_msp[-1]) > 3:
                            if len(num_in_msp[-1]) == 4:
                                check_num = num_in_msp[-1][-1]
                            else:
                                check_num = num_in_msp[-1][-2:]
                            if int(check_num) > 5 and check_num in list_dong_may[idx_m]:
                                msp = msp[:msp.rindex(check_num)]
                                
                    if msp != 'null' and msp != get_msp(msp, maybe_msp, list_dong_may):
                        msp = get_msp(msp, maybe_msp, list_dong_may)               
                        break
                        
                if msp.lower() in null_msp:
                    msp = 'null'
                    
                list_msp += [msp]*list_so_luong[idx_m]

        result_dict['Mã đơn'] += [str(ma_don)]*len(list_dong_may)
        result_dict['Mã bắn vạch'] += [str(ma_ban_vach)]*len(list_dong_may)
        result_dict['Mã sản phẩm'] += list_msp
        result_dict['Dòng máy'] += list_dong_may
        
    return pd.DataFrame(result_dict)

if __name__ == '__main__':
    tiktok(r'C:\Users\19522\Desktop\PDF\pdf_file\tt3.pdf').to_excel('output_tt3.xlsx')
	
	

	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
