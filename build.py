import os
import subprocess
import sys

def build():
    print("🚀 Starting CCTV Manager Pro Build Process...")
    
    # Path to python executable
    python_exe = sys.executable
    
    # Files/folders to bundle
    add_data = "templates;templates"
    
    # PyInstaller command
    cmd = [
        python_exe, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--add-data", add_data,
        "--name", "CCTV_Manager_Pro",
        "--clean",
        "main.py"
    ]
    
    print(f"📦 Executing: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Build Successful!")
        print(f"📁 Find your executable in: {os.path.join(os.getcwd(), 'dist')}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build Failed with error: {e}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    build()
