from PyPDF2 import PdfReader, PdfFileWriter
import json
import re
import camelot

ignore_list = ['Salework', 'salework', 'THÔNG TIN', 'Ngày đặt hàng', 'Đơn vị vận chuyển', 'Tên khách hàng', 'SĐT', 'Địa chỉ', 'Ghi chú khách hàng', 'STT', 
               'Tên Sản phẩm', 'Phân loại', 'Số lượng', 'Thành tiền', 'Thông tin', 'Lưu ý:']

ignore_msp = ['max', 'pro', 'xs', 'plus', 'se', 'iphone']


def remove_last(s, rmv):
    if s.endswith(rmv):
       s = s[:s.rindex(rmv)]
    return s
def repeats(string):
    for x in range(3, len(string)):
        substring = string[:x]

        if substring == string[x:x+len(substring)]:
            return substring
def get_msp(str):
    if not str.isalpha():
        if str[0].isalpha():
            if repeats(str) is not None:
                if str[-1] == 'a':
                    return repeats(str)+'a'
                elif str[-1] == 'b':
                    return repeats(str)+'b'
                elif str[-1] == 'c':
                    return repeats(str)+'c'
                else:
                    return repeats(str)
            else:
                prev_char = ''
                for idx, i in  enumerate(list(str)):
                    if i.isalpha() and prev_char.isdigit():
                        res = str[:idx]
                        if str[-1] == 'a':
                            return res + 'a' 
                        elif str[-1] == 'b':
                            return res +'b'
                        elif str[-1] == 'c':
                            return res +'c'
                        else:
                            return res
                    prev_char = i
                return str
    return 'null'
result_dict = {
    'Mã vận đơn' : [],
    'Mã đơn hàng' : [],
    'Mã sản phẩm' : [],
    'Dòng máy' : []
}
def shopee_list(pdf_file):
    reader = PdfReader(pdf_file)
    pdf_writer = PdfFileWriter()
    pdf_out = open('shopee.pdf', 'wb')
    for pagenum in range(reader.numPages):
        page = reader.getPage(pagenum)
        pdf_writer.addPage(page)
        pdf_writer.write(pdf_out)
    pdf_out.close()
    print('Saved pdf')
    tables = camelot.read_pdf('shopee.pdf', pages='all')
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
        ma_don_hang = re.sub('\W+', '', list_tsp[0]).replace('Mãđơnhàng', '')
        ma_van_don = re.sub('\W+', '', list_tsp[1])
        for text in list_tsp[2:]:
            temp.append(text.replace('1 1', '11').lower())
            if 'VND' in text:
                merge_tsp.append(' '.join(temp))
                temp = []
        list_msp = []
        list_dong_may = []
        table = tables[n]
        for index, row in table.df.iterrows():
            
            if row[0] == 'STT':
                continue
            # file.write(row[1].replace('\n', '') + '\n' + row[2].replace('\n', ' ') + '\n')
            msp = 'null'
            dong_may = 'null'
            if ',' not in row[2]:
                dong_may = row[2].replace('\n', ' ')
                msp = re.sub('\W+', ' ', row[1]).split(' ')[-1]
            else:
                if len(row[2].split(',')[-1]) < 4:
                    dong_may = ','.join(row[2].split(',')[1:]).replace('\n', '')
                else:
                    dong_may = row[2].split(',')[-1].replace('\n', '')
                maybe_msp = [re.sub('\W+', ' ',row[1].replace('\n', ' ')).split(), re.sub('\W+', ' ',row[2].replace('\n', ' ')).split()]
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
                if msp == 'null' or msp == 'se2020':
                    for i in maybe_msp[1]:
                        if not i.isalpha():
                            if i[0].isalpha():
                                msp = i
                                break
            if msp in 'ngẫu nhiên':
                msp = 'null'
            list_msp.append(msp)
            list_dong_may.append(dong_may)
                
        result_dict['Mã vận đơn'] += [ma_van_don]*len(list_msp)
        result_dict['Mã đơn hàng'] += [ma_don_hang]*len(list_msp)
        result_dict['Mã sản phẩm'] += list_msp
        result_dict['Dòng máy'] += list_dong_may
    with open('shopee_list.json', 'w+', encoding='utf-8') as file:
        json.dump(result_dict, file)
if __name__ == '__main__':
    shopee_list(r'pdf_file\shopee.pdf').to_excel('output.xlsx')
