from PyPDF2 import PdfReader, PdfFileWriter
import json
import re
import camelot
import os
import tabula

ignore_list = ['Salework', 'salework', 'THÔNG TIN', 'Ngày đặt hàng', 'Đơn vị vận chuyển', 'Tên khách hàng', 'SĐT', 'Địa chỉ', 'Ghi chú khách hàng', 'STT', 
               'Tên Sản phẩm', 'Phân loại', 'Số lượng', 'Thành tiền', 'Thông tin', 'Lưu ý:']

ignore_msp = ['max', 'pro', 'xs', 'plus', 'se', 'iphone']

def check_msp(msp):
    if not msp.isalpha():
        if msp[0].isalpha():
            return True
    return False

def get_msp_dm(tsp, msp_dm, null_msp):
    msp = 'null'
    dong_may = 'null'
    if 'ngẫu nhiên' not in re.sub('\W+', ' ',msp_dm):
        if ',' not in msp_dm:
            dong_may = msp_dm.replace('\n', ' ')
            msp = re.sub('\W+', ' ', tsp).split(' ')[-1]
            if msp in null_msp or msp.isalpha():
                msp = 'null'
        else:
            if len(msp_dm.split(',')[-1]) < 4:
                dong_may = ','.join(msp_dm.split(',')[1:]).replace('\n', '')
            else:
                dong_may = msp_dm.split(',')[-1].replace('\n', '')
            maybe_msp = [re.sub('\W+', ' ',tsp.replace('\n', ' ')).split(), re.sub('\W+', ' ',msp_dm.replace('\n', ' ')).split()]
            for i in maybe_msp[1]:
                if check_msp(i):
                    msp = i
                    break
            if msp == 'null':
                if maybe_msp[0][-1] not in null_msp:
                    if not maybe_msp[0][-1].isalpha() and maybe_msp[0][-1][0].isalpha():
                        for i in maybe_msp[1]:
                            if i in 'abc':
                                msp = maybe_msp[0][-1] + i
                                break
                            else:
                                msp = maybe_msp[0][-1]
                                for c in 'abc':
                                    if msp + c in msp_dm:
                                        msp += c
                                        break
    else:
        if ',' not in msp_dm:
            dong_may = msp_dm.replace('\n', ' ')
        else:
            if len(msp_dm.split(',')[-1]) < 4:
                dong_may = ','.join(msp_dm.split(',')[1:]).replace('\n', '')
            else:
                dong_may = msp_dm.split(',')[-1].replace('\n', '')
    if 'pko' in dong_may or 'ngẫu nhiên' in dong_may.lower():
        dong_may = 'null'
    if msp == 'null':
        msp = tsp.split()[-1]
        if not check_msp(msp):
            msp = 'null'
    
    if msp.lower() in null_msp or len(msp) < 3:
        msp = 'null'
            
    return msp, dong_may

def shopee_list(pdf_file):
    result_dict = {
    'Mã vận đơn' : [],
    'Mã đơn hàng' : [],
    'Mã sản phẩm' : [],
    'Dòng máy' : [],
    'Tên sản phẩm' : []
    }
    reader = PdfReader(pdf_file)
    pdf_writer = PdfFileWriter()
    pdf_out = open(r'data\shopee.pdf', 'wb')
    for pagenum in range(reader.numPages):
        page = reader.getPage(pagenum)
        pdf_writer.addPage(page)
        pdf_writer.write(pdf_out)
    pdf_out.close()
    with open(r'data\ignored_msp.json', 'r') as file:
        null_msp = json.load(file)['Mã sản phẩm']

    for n, page in enumerate(reader.pages):
        list_text = page.extract_text().split('\n')
        list_tsp = list_text.copy()
        for text in list_text:
            for ignore in ignore_list:
                if ignore in text:
                    if ignore == 'Địa chỉ':
                        list_tsp.remove(list_text[list_text.index(text)+1])
                    if text in list_tsp:
                        list_tsp.remove(text)
                    break
        merge_tsp = []
        temp = []

        if 'Mã đơn hàng' in page.extract_text():
            ma_don_hang = re.sub('\W+', '', list_tsp[0]).replace('Mãđơnhàng', '')
            ma_van_don = re.sub('\W+', '', list_tsp[1])
            for text in list_tsp:
                temp.append(text.replace('1 1', '11').lower())
                if 'VND' in text:
                    merge_tsp.append(' '.join(temp))
                    temp = []
        else:
            ma_don_hang = result_dict['Mã vận đơn'][-1]
            ma_van_don = result_dict['Mã đơn hàng'][-1]
            for text in list_tsp:
                temp.append(text.replace('1 1', '11'))
                if 'VND' in text:
                    merge_tsp.append(' '.join(temp))
                    temp = []
        list_msp = []
        list_dong_may = []
        list_tsp_right = []
        
        table = camelot.read_pdf(r'data\shopee.pdf', pages=str(n+1))
            
        if len(table) > 0:
            for index, row in table[0].df.iterrows():
                if row[0] == 'STT':
                    continue
                
                msp, dong_may = get_msp_dm(row[1], row[2], null_msp)
                so_luong = int(row[3])
                
                list_tsp_right += [row[1]] * so_luong
                list_msp += [msp] * so_luong
                list_dong_may += [dong_may] * so_luong
        else:
            table = camelot.read_pdf(r'data\shopee.pdf', pages=str(n+1), flavor='stream', table_areas=['0,700,840,200'])
            if len(table) > 0:
                if len(table[0].df.index) <= 4:
                    tsp = ''
                    msp_dm = ''
                    so_luong = ''
                    for index, row in table[0].df.iterrows():
                        tsp += ' ' + row[1]
                        msp_dm += ' ' + row[2]
                        if row[3].isdigit():
                            so_luong = int(row[3])
                        
                    msp, dong_may = get_msp_dm(tsp, msp_dm, null_msp)
                    
                    list_tsp_right += [tsp] * so_luong
                    list_msp += [msp] * so_luong
                    list_dong_may += [dong_may] * so_luong

        result_dict['Mã đơn hàng'] += [ma_van_don]*len(list_msp)
        result_dict['Mã vận đơn'] += [ma_don_hang]*len(list_msp)
        result_dict['Mã sản phẩm'] += list_msp
        result_dict['Dòng máy'] += list_dong_may
        result_dict['Tên sản phẩm'] += list_tsp_right

    if not os.path.exists(r'data\shopee_list.json'):
        with open(r'data\shopee_list.json', 'w+', encoding='utf-8') as file:
            json.dump(result_dict, file)
    else:
        with open(r'data\shopee_list.json', 'r', encoding='utf-8') as file:
            exists_data = json.load(file)
            if str(result_dict['Mã đơn hàng'])[1:-1] not in str(exists_data['Mã đơn hàng']):
                exists_data['Mã đơn hàng'] += result_dict['Mã đơn hàng']
                exists_data['Mã vận đơn'] += result_dict['Mã vận đơn']
                exists_data['Mã sản phẩm'] += result_dict['Mã sản phẩm']
                exists_data['Dòng máy'] += result_dict['Dòng máy']
                exists_data['Tên sản phẩm'] += result_dict['Tên sản phẩm']
            with open(r'data\shopee_list.json', 'w', encoding='utf-8') as file:
                json.dump(exists_data, file)
    os.remove(r'data\shopee.pdf')
    
# if __name__ == '__main__':
#     shopee_list(r'pdf_file_1\2.pdf').to_excel('output.xlsx')
