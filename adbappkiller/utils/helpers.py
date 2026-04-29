import os
import sys
import re
import unicodedata
import platform
import logging

def is_valid_package_name(pkg):
    if not isinstance(pkg, str) or not pkg:
        return False
    return re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)*', pkg) is not None

def safe_str(s):
    if not isinstance(s, str):
        s = str(s)
    return ''.join(c for c in s if unicodedata.category(c)[0] != 'C')

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)

def set_app_id():
    if platform.system() != "Windows":
        return
    try:
        import ctypes
        myappid = 'ADBAppKiller.QWERTYASERTY.v03.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        logging.warning(f"No se pudo establecer AppUserModelID: {e}")
