apt update 
apt install freeglut3-dev libgtk2.0-dev libgl1-mesa-glx ffmpeg libsm6 libxext6 ghostscript poppler-utils
mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"trdt0210@gmail.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
