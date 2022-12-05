from PyPDF2 import PdfReader, PdfFileWriter
import json
import re
import camelot
import os

ignore_list = ['Salework', 'salework', 'THÔNG TIN', 'Ngày đặt hàng', 'Đơn vị vận chuyển', 'Tên khách hàng', 'SĐT', 'Địa chỉ', 'Ghi chú khách hàng', 'STT', 
               'Tên Sản phẩm', 'Phân loại', 'Số lượng', 'Thành tiền', 'Thông tin', 'Lưu ý:']

ignore_msp = ['max', 'pro', 'xs', 'plus', 'se', 'iphone']


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
    
    tb_minus = 0

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
        if len(list_tsp) == 0:
            tb_minus += 1
            continue
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
                temp.append(text.replace('1 1', '11').lower())
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

                msp = 'null'
                dong_may = 'null'
                
                if 'ngẫu nhiên' not in re.sub('\W+', ' ',row[2]):
                    if ',' not in row[2]:
                        dong_may = row[2].replace('\n', ' ')
                        msp = re.sub('\W+', ' ', row[1]).split(' ')[-1]
                        if msp in null_msp or msp.isalpha():
                            msp = 'null'
                    else:
                        if len(row[2].split(',')[-1]) < 4:
                            dong_may = ','.join(row[2].split(',')[1:]).replace('\n', '')
                        else:
                            dong_may = row[2].split(',')[-1].replace('\n', '')
                        maybe_msp = [re.sub('\W+', ' ',row[1].replace('\n', ' ')).split(), re.sub('\W+', ' ',row[2].replace('\n', ' ')).split()]
                        for i in maybe_msp[1]:
                            if not i.isalpha():
                                if i[0].isalpha():
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
                                                if msp + c in row[2]:
                                                    msp += c
                                                    break
                else:
                    if ',' not in row[2]:
                        dong_may = row[2].replace('\n', ' ')
                    else:
                        if len(row[2].split(',')[-1]) < 4:
                            dong_may = ','.join(row[2].split(',')[1:]).replace('\n', '')
                        else:
                            dong_may = row[2].split(',')[-1].replace('\n', '')
                if 'pko' in dong_may or 'ngẫu nhiên' in dong_may.lower():
                    dong_may = 'null'
                if msp.lower() in null_msp or len(msp) < 3:
                    msp = 'null'
                so_luong = int(row[3])
                
                list_tsp_right += [row[1]] * so_luong
                list_msp += [msp] * so_luong
                list_dong_may += [dong_may] * so_luong
        else:
            continue

        
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
