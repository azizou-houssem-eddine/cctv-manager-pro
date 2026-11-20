import os
import subprocess
import sys

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def build():
    print("[*] Starting CCTV Manager Pro Build Process (pywebview + PyMuPDF)...")
    
    python_exe = sys.executable
    
    # 0. Ensure icons are generated with Windows DIB compatibility
    try:
        from tools.generate_icons import generate_icons
        generate_icons()
    except Exception as e:
        print(f"[!] Warning: Icon generation failed: {e}")

    # PyInstaller command
    cmd = [
        python_exe, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--icon=app_icon.ico",
        "--add-data", "app_icon.ico;.",
        "--add-data", "web;web",
        "--add-data", "templates_pdf;templates_pdf",
        "--collect-all", "arabic_reshaper",
        "--collect-all", "bidi",
        "--collect-all", "openpyxl",
        "--collect-all", "cryptography",
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

        # Invalidate Windows Shell Icon Cache to display the new icon immediately
        try:
            import ctypes
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)
            print("[+] Windows Shell icon cache invalidated.")
        except Exception as e:
            print(f"[!] Shell cache notify skipped: {e}")
    except subprocess.CalledProcessError as e:
        print(f"\n[-] Build Failed with error: {e}")
    except Exception as e:
        print(f"\n[-] An unexpected error occurred: {e}")

if __name__ == "__main__":
    build()
