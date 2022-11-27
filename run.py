import subprocess

if __name__ == '__main__':
    subprocess.run(['python','-m','streamlit', 'run', 'app.py', '--server.port', '8201'])