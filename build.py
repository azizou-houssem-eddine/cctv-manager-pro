import os
import subprocess
import sys

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def build():
    print("[*] Starting CCTV Manager Pro Build Process (pywebview + PyMuPDF)...")
    
    python_exe = sys.executable
    
    # PyInstaller command
    cmd = [
        python_exe, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--add-data", "web;web",
        "--add-data", "templates_pdf;templates_pdf",
        "--collect-all", "arabic_reshaper",
        "--collect-all", "bidi",
        "--collect-all", "openpyxl",
        "--name", "CCTV_Manager_Pro",
        "--clean",
        "--exclude-module", "PyQt5",
        "--exclude-module", "PyQt6",
        "main.py"
    ]
    
    print(f"[*] Executing: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n[+] Build Successful!")
        print(f"[+] Find your executable in: {os.path.join(os.getcwd(), 'dist')}")
    except subprocess.CalledProcessError as e:
        print(f"\n[-] Build Failed with error: {e}")
    except Exception as e:
        print(f"\n[-] An unexpected error occurred: {e}")

if __name__ == "__main__":
    build()
