import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only

# base="Win32GUI" should be used only for Windows GUI app

setup(
    name="app",
    version="0.1",
    description="My GUI application!",
    executables=[Executable("run.py", target_name='',base="Win32GUI")],
    options = {'build_exe': {'include_files' : ['app.py', 'lazada_list.py', 'shopee_list.py', 'shopee.py', 'tiktok.py']
                             }}
)