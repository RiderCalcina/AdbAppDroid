import os
import urllib.request
import zipfile
import shutil
import json
import tempfile
import time
import sys

class Downloader:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback

    def _log(self, msg):
        if self.log_callback:
            self.log_callback(msg)

    def install_adb_locally(self):
        url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
        zip_name = "platform-tools.zip"
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            zip_path = os.path.join(base_dir, zip_name)
            self._log("🌐 Descargando ADB...")
            urllib.request.urlretrieve(url, zip_path)
            self._log("📦 Extrayendo archivos...")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(base_dir)
            os.remove(zip_path)
            return True
        except Exception as e:
            self._log(f"❌ Error ADB: {str(e)}")
            return False

    def get_latest_scrcpy_version(self):
        try:
            url = "https://api.github.com/repos/Genymobile/scrcpy/releases/latest"
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get("tag_name", "").lstrip("v")
        except Exception:
            return None

    def install_scrcpy_locally(self):
        version = self.get_latest_scrcpy_version()
        if not version: return False
        url = f"https://github.com/Genymobile/scrcpy/releases/download/v{version}/scrcpy-win64-v{version}.zip"
        zip_name = f"scrcpy-win64-v{version}.zip"
        try:
            temp_dir = os.path.join(tempfile.gettempdir(), f"scrcpy_temp_{int(time.time())}")
            os.makedirs(temp_dir, exist_ok=True)
            zip_path = os.path.join(temp_dir, zip_name)
            self._log(f"🌐 Descargando scrcpy v{version}...")
            urllib.request.urlretrieve(url, zip_path)
            self._log("📦 Extrayendo archivos...")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(temp_dir)
            
            extracted_folder = None
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                if os.path.isdir(item_path):
                    extracted_folder = item_path
                    break
            
            if not extracted_folder: return False
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            final_dir = os.path.join(base_dir, "scrcpy")
            if os.path.exists(final_dir):
                shutil.rmtree(final_dir)
            shutil.move(extracted_folder, final_dir)
            shutil.rmtree(temp_dir, ignore_errors=True)
            self._log(f"✅ scrcpy v{version} instalado.")
            return True
        except Exception as e:
            self._log(f"❌ Error scrcpy: {str(e)}")
            return False
