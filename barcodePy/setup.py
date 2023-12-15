import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"  # 이 부분이 콘솔 없이 실행하는 옵션입니다.

options = {
    "build_exe": {
        "include_files": ["qrbarcode_beep.mp3", "barcode.ui"],
    }
}

setup(
    name="barcode",
    version="1.0",
    description="scanning of barcode",
    executables=[Executable("barcode.py")],
)
