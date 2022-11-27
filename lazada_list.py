import pandas as pd
from PyPDF2 import PdfReader
import re

ignore_list = ['Salework', 'salework', 'THÔNG TIN', 'Ngày đặt hàng', 'Đơn vị vận chuyển', 'Tên khách hàng', 'SĐT', 'Địa chỉ', 'Ghi chú khách hàng', 'STT', 
            'Tên Sản phẩm', 'Phân loại', 'Số lượng', 'Thành tiền', 'Thông tin']

dong_may_sep = ['Iphone:', 'Dòng máy:', 'Variation1:', 'Dòng sản phẩm tương thích:', 'iphone:', 'iP ', 'MÃ MÁY :']
msp_sep = ['Variation3:', 'KIỂU:', 'Nhóm Màu:', 'Màu:', 'Mẫu:']

def lazada_list(pdf_file):
    reader = PdfReader(pdf_file)
    result_dict = {
        'Số đơn' : [],
        'Mã bắn vạch' : [],
        'Mã sản phẩm' : [],
        'Dòng máy' : [],
        'Tên sản phẩm' : []
    }

    for n, page in enumerate(reader.pages[:]):
        
        list_text = page.extract_text().split('\n')
        list_tsp = list_text.copy()
        if 'Mã đơn hàng:' not in page.extract_text():
            list_tsp = page.extract_text().split('\n')[1:-1]
            list_tsp[0] = list_tsp[0].replace('https://stock.salework.net/orders ', '')
            list_tsp = [' ', ' '] + list_tsp

        else:
            for idx, text in enumerate(list_text):
                for ignore in ignore_list:
                    if ignore in text:
                        if text in list_tsp:
                            list_tsp.remove(text)
                        if ignore == 'Địa chỉ':
                            list_tsp.remove(list_text[idx+1])
                        break
        so_don = re.sub('\W+', '',list_tsp[0].replace('Mã đơn hàng:', '')) if list_tsp[0] != ' ' else result_dict['Số đơn'][-1]
        
        ma_ban_vach = re.sub('\W+', '',list_tsp[1]) if list_tsp[1] != ' ' else result_dict['Mã bắn vạch'][-1]
        merge_tsp = []
        temp = []
        for text in list_tsp[2:]:
            temp.append(text.replace('1 1', '11').replace('VND', '').replace('VN', ''))
            if 'VND' in text:
                merge_tsp.append(' '.join(temp))
                temp = []
        
        list_dong_may = []
        list_msp = []
        list_tsp = []
        
        idx_dong_may = []
        idx_msp = []

        for text in merge_tsp:
            none_dong_may = -1      
            none_msp = -1
            for i in dong_may_sep:
                if i in text:
                    none_dong_may = (text.rindex(i), i)
                    break
            idx_dong_may.append(none_dong_may)
            
            for j in msp_sep:
                if j in text:
                    none_msp = (text.rindex(j), j)
                    break
            idx_msp.append(none_msp)
        # print(str(n+1), idx_dong_may, idx_msp)
        for i in range(len(idx_dong_may)):
            dong_may = 'null'
            msp = 'null'
            tsp = 'null'
            if idx_dong_may[i] != -1 and idx_msp[i] != -1:
                if idx_dong_may[i][0] < idx_msp[i][0]:
                    tsp = merge_tsp[i].split(idx_dong_may[i][1])[0][1:] 
                    
                    dong_may = merge_tsp[i].split(idx_dong_may[i][1])[-1].split(',')[0]
                    
                    msp =  merge_tsp[i].split(idx_msp[i][1])[-1].split(' ')[0][:-1]
                    if msp.isalpha() or not msp[0].isalpha():
                        msp = merge_tsp[i].split(idx_dong_may[i][1])[0]
                        msp = re.sub('\W+', ' ', msp).split()[-1]
                        if msp.isalpha():
                            if not msp[0].isalpha():
                                msp = 'null'
                        else:
                            for n in 'abc':
                                if msp + n in merge_tsp[i]:
                                    msp += n
                                    break
                else:
                    tsp = merge_tsp[i].split(idx_msp[i][1])[0][1:] 
                    
                    dong_may = merge_tsp[i].replace('pro max', 'promax1 ').split(idx_dong_may[i][1])[-1].split(' ')
                    dong_may = ''.join(dong_may)
                    
                    msp = merge_tsp[i].split(idx_msp[i][1])[-1].split(',')[0]
                    maybe_msp = re.sub('\W+', ' ', msp).split()
                    t = re.sub('\W+', ' ', merge_tsp[i].split(idx_msp[i][1])[0]).split()
                    for word in maybe_msp:
                        if not word.isalpha():
                            if word[0].isalpha():
                                msp = word
                                break
                        elif len(word) == 1:
                            if word.lower() in 'abc':
                                if t[-1][0].isalpha() and not t[-1].isalpha():
                                    msp =  t[-1] + word
                                    break
                        else:
                            msp = 'null'
                    if msp == 'null':
                        if t[-1][0].isalpha() and not t[-1].isalpha():
                            msp = t[-1]
            elif idx_dong_may[i] != -1:
                tsp = merge_tsp[i].split(idx_dong_may[i][1])[0][1:] 
                dong_may = merge_tsp[i].split(idx_dong_may[i][1])[-1].split(' ')[0][:-1]
                t = re.sub('\W+', ' ', merge_tsp[i].split(idx_dong_may[i][1])[0]).split()
                if t[-1][0].isalpha() and not t[-1].isalpha():
                    msp =  t[-1]
            elif idx_msp[i] != 1:
                tsp = merge_tsp[i].split(idx_msp[i][1])[0][1:] 
                msp = merge_tsp[i].split(idx_msp[i][1])[-1]
                if 'ngẫu nhiên' in msp.lower():
                    msp = 'null'
                else:
                    msp =  msp.split(' ')[0][:-1]
            if '.' in dong_may:
                dong_may = dong_may.split('.')[0]
            all_num_dm = re.findall('\d+', dong_may)
            if len(all_num_dm) > 0:
                last_num = all_num_dm[-1]
                
                if last_num == dong_may:
                    dong_may = dong_may[:2]
                else:
                    idx_before_last_num = dong_may.rindex(last_num)-1
                    if dong_may[idx_before_last_num] == '/':
                        dong_may = dong_may[:idx_before_last_num+2]
                    else:
                        if dong_may.endswith(last_num):
                            if last_num.startswith('2020'):
                                dong_may = dong_may[:idx_before_last_num+5]
                            else:
                                dong_may = dong_may[:idx_before_last_num+1]
                    
            list_dong_may.append(dong_may)
            list_msp.append(msp)
            list_tsp.append(tsp)
        
        result_dict['Số đơn'] += [so_don] * len(list_msp)
        result_dict['Mã bắn vạch'] += [ma_ban_vach] * len(list_msp)
        result_dict['Mã sản phẩm'] += list_msp
        result_dict['Dòng máy'] += list_dong_may
        result_dict['Tên sản phẩm'] += list_tsp

    return result_dict

if __name__ == '__main__':
    lazada_list('pdf_file_1\lazada_list.pdf')