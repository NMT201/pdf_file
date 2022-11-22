
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



from st_aggrid import GridUpdateMode, DataReturnMode

def show_table(shows):
    gb = GridOptionsBuilder.from_dataframe(shows)
    gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
    gb.configure_side_bar()
    gridOptions = gb.build()

    st.success(
        f"""
            💡 Thông tin đơn đã được trích xuất bên dưới
            """
    )

    response = AgGrid(
        shows,
        gridOptions=gridOptions,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=False,
    )
# st.header("Đăng nhập")
# usr = st.text_input('', placeholder='Username')
# psw = st.text_input('', placeholder='Password', type='password')
# if st.button('Đăng nhập'):
# if usr == 'admin' and psw == '123':
with st.sidebar:
    selected = option_menu("Main Menu", ["Shopee đầy đủ", 'Shopee', 'Lazada', 'Tiktok'], default_index=1)

if selected == 'Shopee đầy đủ':
    st.header("Shopee đầy đủ")
    uploaded_file_day_du = st.file_uploader(
        "File shopee đầy đủ.",
        key="1",
        help="'",
        type='pdf',
    )
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

    if uploaded_file is not None:
        df_day_du = json.load(open('shopee_list.json', 'r'))
        shows = shopee(uploaded_file, df_day_du)
        uploaded_file.seek(0)
        show_table(shows)
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

    if uploaded_file is not None:
        df_day_du = lazada_list(uploaded_file_day_du)
        shows = lazada(uploaded_file, df_day_du)
        print(shows)
        uploaded_file.seek(0)
        show_table(shows)
    else:
        st.stop()
            
elif selected == 'Tiktok':
    st.header("Tiktok")
    uploaded_file = st.file_uploader(
        "File đơn tiktok.",
        key="2",
        help="",
        type='pdf'
    )

    if uploaded_file is not None:
        shows = tiktok(uploaded_file)
        print(shows)
        uploaded_file.seek(0)
        show_table(shows)
    else:
        st.stop()
# else:
#     st.warning('Sai tên đăng nhập hoặc mật khẩu')
    

