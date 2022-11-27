
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from streamlit_option_menu import option_menu


from lazada_list import lazada_list
from lazada import lazada
from tiktok import tiktok
from shopee_list import shopee_list
from shopee import shopee
import streamlit as st
import pandas as pd
import json
import os

if not os.path.isdir('data'):
    os.makedirs('data')

from st_aggrid import GridUpdateMode, DataReturnMode

def show_table(shows, edit=False, title=''):
    gb = GridOptionsBuilder.from_dataframe(shows)
    gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
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



def button_update(data, df_day_du, df_don):
    reload = False
    for i in data.values:
        if i[-1] != 'null':
            so_don = i[0]
            for j in range(len(df_day_du['Số đơn'])):
                if str(df_day_du['Số đơn'][j]) == so_don and df_day_du['Tên sản phẩm'][j] == i[2]:
                    df_day_du['Số đơn'][j] = so_don
                    df_day_du['Mã sản phẩm'][j] = str(i[-1])

    df_don = lazada(df_don, df_day_du)
    # show_table(df_don, title='💡Thông tin đơn đã được cập nhật bên dưới')
    
with st.sidebar:
    selected = option_menu("Main Menu", ["Shopee đầy đủ", 'Shopee', 'Lazada', 'Tiktok', 'Thêm mã sản phẩm'], default_index=1)

if selected == 'Shopee đầy đủ':
    st.header("Shopee đầy đủ")
    uploaded_file_day_du = st.file_uploader(
        "File shopee đầy đủ.",
        key="1",
        help="'",
        type='pdf',
    )
    if st.button('Xử lý'):
        if uploaded_file_day_du is not None:
            shopee_list(uploaded_file_day_du)
            uploaded_file_day_du.seek(0)
        else:
            st.stop()
if selected == 'Shopee':
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
                show_table(shows, title='💡Thông tin đơn đã được trích xuất bên dưới', edit=True)
        else:
            st.stop()
        
elif selected == 'Lazada':
    st.header("Lazada")

    uploaded_file_day_du = st.file_uploader(
        "File lazada đầy đủ.",
        key="1",
        help="'",
        type='pdf',
        
    )
    uploaded_file = st.file_uploader(
        "File đơn lazada.",
        key="2",
        help="",
        type='pdf'
    )
    if st.button('Xử lý'):
        if uploaded_file is not None and uploaded_file_day_du is not None:
            df_day_du = lazada_list(uploaded_file_day_du)
            df_don, df_null = lazada(uploaded_file, df_day_du)
            show_table(df_don, title='💡Thông tin đơn đã được trích xuất bên dưới')
            # if len(df_null.index) > 0:
            #     show_table(df_null, edit=True, title='Sản phẩm không tìm thấy mã')
    #     if st.form_submit_button():
    #         if uploaded_file is not None and uploaded_file_day_du is not None:
    #             st.session_state.df_day_du = lazada_list(uploaded_file_day_du)
    #             st.session_state.df_don, st.session_state.df_null = lazada(uploaded_file, st.session_state.df_day_du)
    #             # show_table(df_don, title='💡Thông tin đơn đã được trích xuất bên dưới')
    #             # if len(df_null.index) > 0:
    #             #     st.session_state.response = show_table(df_null, edit=True, title='Thêm mã sản phẩm')
    #                 # st.session_state.data = pd.DataFrame(df_show['data'])
    #                 # st.button('Cập nhật', on_click=button_update, args=[data, df_day_du, df_don])
    # show_table(st.session_state.df_don, title='💡Thông tin đơn đã được trích xuất bên dưới')
    # if len(st.session_state.df_null.index) > 0:
    #     response = show_table(st.session_state.df_null, edit=True, title='Thêm mã sản phẩm')
    # if st.button
    # button_update(response['data'], st.session_state.df_day_du, st.session_state.df_don)
    # if st.button('Thống kê'):
    
        # if uploaded_file is not None and uploaded_file_day_du is not None:
        #     df_day_du = lazada_list(uploaded_file_day_du)
        #     df_don, df_null = lazada(uploaded_file, df_day_du)
        #     show_table(df_don, title='💡Thông tin đơn đã được trích xuất bên dưới')
        #     if len(df_null.index) > 0:
        #         df_show = show_table(df_null, edit=True, title='Thêm mã sản phẩm')
        #         data = pd.DataFrame(df_show['data'])
        #         st.button('Cập nhật', on_click=button_update, args=[data, df_day_du, df_don])
                    # show_table(df_null, edit=True, title='Thêm mã sản phẩm')
            
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
    if st.button('Thêm'):
        import json
        if os.path.exists(r'data\extra_data.json'):
            file =  open(r'data\extra_data.json', 'r', encoding='utf-8')
            d = json.load(file)
            d['Tên sản phẩm'].append(tsp)
            d['Mã sản phẩm'].append(msp)
            file.close()
            file =  open(r'data\extra_data.json', 'w', encoding='utf-8')
            json.dump(d, file)
            file.close()
        else:
            d = {
                'Tên sản phẩm' : [tsp],
                'Mã sản phẩm' : [msp]
            }
            file =  open(r'data\extra_data.json', 'w+', encoding='utf-8')
            json.dump(d, file)
            file.close()

    

