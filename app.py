
import streamlit as st
import pandas as pd
import json
import os
import re

from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from streamlit_option_menu import option_menu


from lazada_list import lazada_list
from lazada import lazada
from tiktok import tiktok
from shopee_list import shopee_list
from shopee import shopee


if not os.path.isdir('data'):
    os.makedirs('data')
if not os.path.exists(r'data\extra_data.json'):
    with open(r'data\extra_data.json', 'a', encoding='utf-8') as file:
        json.dump({'Tên sản phẩm': [], 'Mã sản phẩm': []}, file)
if not os.path.exists(r'data\ignored_msp.json'):
    with open(r'data\ignored_msp.json', 'a', encoding='utf-8') as file:
        json.dump({'Mã sản phẩm': []}, file)

from st_aggrid import GridUpdateMode, DataReturnMode

def show_table(shows, edit=False, title=''):
    gb = GridOptionsBuilder.from_dataframe(shows)
    gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True, editable=edit)
    gb.configure_side_bar()
    gridOptions = gb.build()

    st.success(title)

    response = AgGrid(
        shows,
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.MANUAL,
        # data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=False,
        reload_data=True
    )
    
    return response
    
with st.sidebar:
    selected = option_menu("Main Menu", ["Shopee đầy đủ", 'Shopee', 'Lazada đầy đủ', 'Lazada', 'Tiktok', 'Thêm mã sản phẩm', 'Gán null'], default_index=1)

if selected == 'Shopee đầy đủ':
    st.header("Shopee đầy đủ")
    uploaded_file_day_du = st.file_uploader(
        "File shopee đầy đủ.",
        key="1",
        help="'",
        type='pdf',
        accept_multiple_files=True
    )
    if st.button('Xử lý'):
        if uploaded_file_day_du is not None:
            for u in uploaded_file_day_du:
                shopee_list(u)
            st.success('Thêm dữ liệu file đầy đủ thành công')
        else:
            st.stop()
    # if st.button('Xoá dữ liệu cũ'):
        
elif selected == 'Shopee':
    st.header("Shopee")
    uploaded_file = st.file_uploader(
        "File đơn shopee.",
        key="2",
        help=".",
        type='pdf'
    )
    if st.button('Xử lý'):
        if uploaded_file is not None:
            if not os.path.exists(r'data\shopee_list.json'):
                st.warning('Chưa nhập file shopee đầy đủ')
            else:
                df_day_du = json.load(open(r'data\shopee_list.json', 'r'))
                shows = shopee(uploaded_file, df_day_du)
                uploaded_file.seek(0)
                show_table(shows, title='💡Thông tin đơn đã được trích xuất bên dưới')
        else:
            st.stop()
            
elif selected == 'Lazada đầy đủ':
    st.header("Lazada đầy đủ")
    uploaded_file_day_du = st.file_uploader(
        "File lazada đầy đủ.",
        key="1",
        help="'",
        type='pdf',
        accept_multiple_files=True
    )
    if st.button('Xử lý'):
        if uploaded_file_day_du is not None:
            for u in uploaded_file_day_du:
                lazada_list(u)
            st.success('Thêm dữ liệu file đầy đủ thành công')
        else:
            st.stop()            
        
elif selected == 'Lazada':
    st.header("Lazada")
    
    uploaded_file = st.file_uploader(
        "File đơn lazada.",
        key="2",
        help="",
        type='pdf'
    )
    if st.button('Xử lý'):
        if not os.path.exists(r'data\lazada_list.json'):
            st.warning('Chưa nhập file lazada đầy đủ')
        else:
            if uploaded_file is not None:
                df_day_du = json.load(open(r'data\lazada_list.json', 'r'))
                df_don, df_null = lazada(uploaded_file, df_day_du)
                show_table(df_don, title='💡Thông tin đơn đã được trích xuất bên dưới')
            
            
elif selected == 'Tiktok':
    st.header("Tiktok")
    uploaded_file = st.file_uploader(
        "File đơn tiktok.",
        key="2",
        help="",
        type='pdf'
    )
    if st.button('Xử lý'):
        if uploaded_file is not None:
            shows = tiktok(uploaded_file)
            uploaded_file.seek(0)
            show_table(shows)
        else:
            st.stop()
            
elif selected == 'Thêm mã sản phẩm':
    tsp = st.text_input('Tên sản phẩm')
    msp = st.text_input('Mã sản phẩm')
    with open(r'data\extra_data.json', 'r', encoding='utf-8') as file:  
        extra_data = json.load(file)
    if st.button('Thêm'):
        extra_data['Tên sản phẩm'].append(tsp)
        extra_data['Mã sản phẩm'].append(msp)
        with open(r'data\extra_data.json', 'w', encoding='utf-8') as file:
            json.dump(extra_data, file)
        
    extra_data_df = show_table(pd.DataFrame(extra_data), edit=True, title='Danh sách đã thêm')['data']

    if extra_data_df['Mã sản phẩm'].to_list() != extra_data['Mã sản phẩm'] or extra_data_df['Tên sản phẩm'].to_list() != extra_data['Tên sản phẩm']:
        extra_data = {
            'Tên sản phẩm': list(set([i for i in extra_data_df['Tên sản phẩm'].to_list() if i != ''])),
            'Mã sản phẩm': list(set([i for i in extra_data_df['Mã sản phẩm'].to_list() if i != '']))
            }
        with open('data\extra_data.json', 'w', encoding='utf-8') as file:
            json.dump(extra_data, file)         
    
elif selected == 'Gán null':
    msp = st.text_input('Thêm một hoặc nhiều mã sản phẩm ngăn cách nhau bằng dấu phẩy')
    list_msp = [re.sub('\W+', '', i) for i in msp.split(',')]
    with open('data\ignored_msp.json', 'r', encoding='utf-8') as file:
        ignored_msp = json.load(file)
    if st.button('Thêm') and msp is not None:
        ignored_msp['Mã sản phẩm'] += list_msp 
        ignored_msp['Mã sản phẩm'] = list(set(ignored_msp['Mã sản phẩm']))
        with open('data\ignored_msp.json', 'w', encoding='utf-8') as file:
            json.dump(ignored_msp, file)
        st.success('Đã thêm thành công')
    
    ignored_msp_df = show_table(pd.DataFrame(ignored_msp), edit=True, title='Danh sách mã sản phẩm đã thêm')['data']

    if ignored_msp_df['Mã sản phẩm'].to_list() != ignored_msp['Mã sản phẩm']:
        ignored_msp = ignored_msp_df['Mã sản phẩm'].to_list()
        with open('data\ignored_msp.json', 'w', encoding='utf-8') as file:
            json.dump({'Mã sản phẩm': [i for i in ignored_msp if i != '']}, file)
