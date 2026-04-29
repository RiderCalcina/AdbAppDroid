import os
import subprocess
import time
import logging
import re
import signal
import adbutils
from ..utils.helpers import is_valid_package_name

class ADBController:
    def __init__(self, adb_path=None):
        self._adb_executable = adb_path
        self.dumpsys_cache = {}
        self.cache_ttl = 2.0
        # Iniciar servidor ADB automáticamente
        self._ensure_adb_server()

    def get_adb_executable(self):
        if self._adb_executable and os.path.isfile(self._adb_executable):
            return self._adb_executable
        
        # Búsqueda local dinámica
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            local_adb = os.path.join(base_dir, "platform-tools", "adb.exe")
            if os.path.isfile(local_adb):
                self._adb_executable = local_adb
                return self._adb_executable
        except Exception:
            pass
        return None

    def _ensure_adb_server(self):
        """Inicia el servidor ADB si no está ejecutándose"""
        adb_path = self.get_adb_executable()
        if not adb_path:
            return
        
        try:
            # Intentar iniciar el servidor ADB de forma silenciosa
            subprocess.run(
                [adb_path, "start-server"],
                capture_output=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            logging.info("Servidor ADB iniciado correctamente")
        except Exception as e:
            logging.warning(f"No se pudo iniciar el servidor ADB: {e}")

    def run_adb(self, args, timeout=5, retry_count=2):
        adb_path = self.get_adb_executable()
        if not adb_path:
            return -2, "", "ADB no encontrado"
        
        for attempt in range(retry_count):
            try:
                result = subprocess.run(
                    [adb_path] + args,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    encoding='utf-8',
                    errors='replace',
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return result.returncode, result.stdout, result.stderr
            except subprocess.TimeoutExpired:
                if attempt == retry_count - 1:
                    return -1, "", "Timeout"
                time.sleep(1)
            except Exception as e:
                if attempt == retry_count - 1:
                    return -1, "", str(e)
                time.sleep(1)
        return -1, "", "Error tras reintentos"

    def get_connected_devices(self):
        try:
            # Usar adbutils para una detección más rápida por sockets
            devices = []
            for d in adbutils.adb.device_list():
                serial = d.serial
                status = d.info.get('state', 'unknown')
                # Detectar tipo: WiFi suele tener formato IP:Puerto
                is_wifi = ":" in serial and "." in serial
                devices.append({
                    "serial": serial,
                    "status": status,
                    "type": "WiFi" if is_wifi else "USB"
                })
            return devices
        except Exception as e:
            logging.error(f"Error listing devices with adbutils: {e}")
            # Fallback al método original por subprocess si falla adbutils
            code, out, _ = self.run_adb(["devices"], timeout=5)
            if code != 0:
                return []
            devices = []
            for line in out.splitlines()[1:]:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        serial, status = parts[0], parts[1]
                        is_wifi = ":" in serial and "." in serial
                        devices.append({
                            "serial": serial,
                            "status": status,
                            "type": "WiFi" if is_wifi else "USB"
                        })
            return devices

    def connect_wireless(self, ip_port):
        return self.run_adb(["connect", ip_port])

    def disconnect_wireless(self, ip_port=None):
        args = ["disconnect"]
        if ip_port:
            args.append(ip_port)
        return self.run_adb(args)


    def get_foreground_app(self, serial=None):
        # Desactivamos adbutils por reportes de inconsistencia en WiFi/Samsung
        # try:
        #     # Intentar con adbutils (extremadamente rápido)
        #     d = adbutils.adb.device(serial=serial) if serial else adbutils.adb.device()
        #     app_info = d.app_current()
        #     if app_info and app_info.package:
        #         pkg = app_info.package
        #         if is_valid_package_name(pkg) and \
        #            "launcher" not in pkg.lower() and \
        #            "systemui" not in pkg.lower():
        #             return pkg
        # except Exception:
        #     pass

        # Fallback al método robusto de múltiples comandos
        methods = [
            ["shell", "dumpsys", "window", "windows"],
            ["shell", "cmd", "activity", "top-activities"],
            ["shell", "dumpsys", "activity", "activities"]
        ]
        patterns = [
            r"mCurrentFocus=Window\{.*\s([a-zA-Z0-9._]+)/", # Formato detallado de Android 10+
            r"(?:mCurrentFocus|mFocusedApp).*?([a-zA-Z0-9._]+)/", # Formato clásico
            r"ACTIVITY ([a-zA-Z0-9._]+)/",  # Regex más estricto para evitar falsos positivos
            r"(?:ResumedActivity|mResumedActivity).*?([a-zA-Z0-9._]+)/"
        ]
        
        # Aplanar patterns para iterar
        # Ajuste: El primer método usa los dos primeros patrones, etc.
        # Mejor estrategia: probar todos los patrones en la salida
        
        for cmd in methods:
            try:
                run_args = (["-s", serial] + cmd) if serial else cmd
                code, out, _ = self.run_adb(run_args, timeout=5)
                if code == 0 and out.strip():
                    for pattern in patterns:
                        match = re.search(pattern, out)
                        if match:
                            pkg = match.group(1)
                            if is_valid_package_name(pkg) and \
                               "launcher" not in pkg.lower() and \
                               "systemui" not in pkg.lower() and \
                               "recents" not in pkg.lower(): # Evitar panel de recientes
                                return pkg
            except Exception:
                continue
        return None

    def is_system_app_robust(self, pkg, apk_path, installer, uid, flags):
        if apk_path and (apk_path.startswith("/system/") or apk_path.startswith("/product/") or apk_path.startswith("/system_ext/")):
            return True
        if apk_path and apk_path.startswith("/data/app/"):
            return False
        try:
            uid_val = int(uid) if uid and uid.isdigit() else None
            if uid_val is not None and uid_val < 10000:
                return True
        except Exception:
            pass
        if flags and "SYSTEM" in flags.upper():
            return True
        user_installers = ["com.android.vending", "com.google.android.packageinstaller", "com.mi.global.shop"]
        if installer in user_installers:
            return False
        if not installer or installer.lower() in ("null", "desconocida"):
            return True
        return False

    def get_device_info(self, serial=None):
        """Obtiene información detallada del hardware del dispositivo"""
        info = {
            "brand": "Desconocida",
            "model": "Desconocido",
            "ram": "Desconocida",
            "cpu": "Desconocida",
            "screen": "Desconocida",
            "android_version": "Desconocida",
            "android_sdk": 0
        }
        try:
            d = adbutils.adb.device(serial=serial) if serial else adbutils.adb.device()
            
            # 1. Marca y Modelo
            info["brand"] = d.prop.get("ro.product.brand") or d.prop.get("ro.product.manufacturer") or "Desconocida"
            info["model"] = d.prop.get("ro.product.model") or "Desconocido"
            
            # 2. RAM (Total de /proc/meminfo)
            mem_out = d.shell("cat /proc/meminfo")
            match_ram = re.search(r"MemTotal:\s+(\d+)\s+kB", mem_out)
            if match_ram:
                ram_kb = int(match_ram.group(1))
                ram_gb = round(ram_kb / (1024 * 1024))
                info["ram"] = f"{ram_gb} GB"

            # 3. CPU (Chipset Info)
            soc_model = d.prop.get("ro.soc.model")
            platform = d.prop.get("ro.board.platform")
            hardware = d.prop.get("ro.hardware")
            
            # Buscar el nombre en clave en este orden de prioridad
            chip_key = soc_model or platform or hardware
            
            # Si no hay propiedades, recurrimos a /proc/cpuinfo
            if not chip_key:
                try:
                    cpu_info = d.shell("cat /proc/cpuinfo")
                    match_cpu = re.search(r"Hardware\s*:\s*(.*)", cpu_info)
                    if match_cpu:
                        chip_key = match_cpu.group(1).strip()
                except Exception:
                    pass
            
            # Si a pesar de todo falla (algo muy poco probable), se usa un identificador genérico del procesador principal si es posible
            if not chip_key:
                 try:
                    cpu_info = d.shell("cat /proc/cpuinfo")
                    # Busca el modelo de CPU, como AArch64 Processor...
                    match_model = re.search(r"model name\s*:\s*(.*)", cpu_info)
                    if match_model:
                        chip_key = match_model.group(1).strip()
                 except Exception:
                     pass

            info["cpu"] = chip_key.upper() if chip_key else "PROCESADOR GENÉRICO"

            # 4. Resolución de pantalla
            screen_out = d.shell("wm size")
            match_screen = re.search(r"Override size: (\d+x\d+)", screen_out) or re.search(r"Physical size: (\d+x\d+)", screen_out)
            if match_screen:
                info["screen"] = match_screen.group(1)
            
            # 5. Versión de Android y SDK
            info["android_version"] = d.prop.get("ro.build.version.release") or "Desconocida"
            try:
                info["android_sdk"] = int(d.prop.get("ro.build.version.sdk") or 0)
            except:
                info["android_sdk"] = 0

            # 6. Batería
            batt_out = d.shell("dumpsys battery")
            match_batt = re.search(r"level:\s+(\d+)", batt_out)
            info["battery"] = f"{match_batt.group(1)}%" if match_batt else "??%"

            # 7. Almacenamiento (Data partition)
            storage_out = d.shell("df -h /data")
            # Salida típica: Filesystem Size Used Avail Use% Mounted on /dev/block/... 110G 50G 60G 46% /data
            lines = storage_out.splitlines()
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 4:
                    # Normalizar unidades (G -> GB, M -> MB) para mayor claridad
                    def format_size(s):
                        s = s.upper()
                        if s.endswith(("G", "M", "K", "T")):
                            return s + "B"
                        return s
                    
                    used = format_size(parts[2])
                    total = format_size(parts[1])
                    info["storage"] = f"{used} / {total}" # Usado / Total
                else:
                    info["storage"] = "Desconocido"
            else:
                info["storage"] = "Desconocido"

        except Exception as e:
            logging.error(f"Error getting device info: {e}")
            
        return info

    def get_app_details(self, serial, pkg):
        if not pkg or not is_valid_package_name(pkg):
            return {}
        
        # Uso de caché básico
        now = time.time()
        if pkg in self.dumpsys_cache:
            cache_time, data = self.dumpsys_cache[pkg]
            if now - cache_time < self.cache_ttl:
                return data

        code, out, _ = self.run_adb(["-s", serial, "shell", f"dumpsys package {pkg}"] if serial else ["shell", f"dumpsys package {pkg}"])
        if code != 0: return {}

        installer_match = re.search(r"installerPackageName=([^\s]+)", out)
        installer = installer_match.group(1) if installer_match else "Desconocida"
        flags_match = re.search(r"flags=\[([^\]]+)\]", out)
        flags_str = flags_match.group(1) if flags_match else ""
        uid = re.search(r"userId=(\d+)", out).group(1) if "userId" in out else "Unknown"

        code_p, out_p, _ = self.run_adb(["-s", serial, "shell", f"pm path {pkg}"] if serial else ["shell", f"pm path {pkg}"])
        apk_paths = [line.replace("package:", "").strip() for line in out_p.splitlines() if "package:" in line]
        
        is_system = self.is_system_app_robust(pkg, apk_paths[0] if apk_paths else "", installer, uid, flags_str)

        # Extraer todos los permisos solicitados
        # El bloque 'requested permissions:' suele listar todo
        requested_section = re.search(r"requested permissions:(.*?)(?:\w+ permissions:|$)", out, re.DOTALL)
        requested_perms = []
        if requested_section:
            requested_perms = re.findall(r"android\.permission\.([A-Z_][A-Z0-9_]*)", requested_section.group(1))

        # Extraer permisos concedidos (activos)
        # Buscamos 'granted=true' en los bloques de install y runtime permissions
        granted_perms = []
        # Pattern: android.permission.NAME: granted=true
        granted_matches = re.finditer(r"android\.permission\.([A-Z_][A-Z0-9_]*): [^g]*granted=true", out)
        for match in granted_matches:
            granted_perms.append(match.group(1))
        
        # Eliminar duplicados manteniendo orden
        requested_perms = list(dict.fromkeys(requested_perms))
        granted_perms = list(dict.fromkeys(granted_perms))

        details = {
            "name": re.search(r"applicationLabel='([^']+)'", out).group(1) if "applicationLabel" in out else pkg,
            "package": pkg,
            "version": re.search(r"versionName=([^\s]+)", out).group(1) if "versionName" in out else "Unknown",
            "install_time": re.search(r"firstInstallTime=(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", out).group(1) if "firstInstallTime" in out else "Unknown",
            "uid": uid,
            "is_system": is_system,
            "installer": installer,
            "apk_paths": apk_paths,
            "requested_permissions": requested_perms,
            "granted_permissions": granted_perms
        }
        
        self.dumpsys_cache[pkg] = (now, details)
        return details

    def uninstall_app(self, serial, pkg):
        return self.run_adb(["-s", serial, "uninstall", pkg] if serial else ["uninstall", pkg], timeout=20)

    def install_app(self, serial, apk_path):
        return self.run_adb(["-s", serial, "install", "-r", apk_path] if serial else ["install", "-r", apk_path], timeout=60)

    def clear_app_data(self, serial, pkg):
        return self.run_adb(["-s", serial, "shell", "pm", "clear", pkg] if serial else ["shell", "pm", "clear", pkg])

    def disable_app(self, serial, pkg):
        return self.run_adb(["-s", serial, "shell", "pm", "disable-user", "--user", "0", pkg] if serial else ["shell", "pm", "disable-user", "--user", "0", pkg])

    def pull_file(self, serial, remote, local):
        return self.run_adb(["-s", serial, "pull", remote, local] if serial else ["pull", remote, local], timeout=60)

    def take_screenshot(self, serial, local_path):
        remote_path = "/data/local/tmp/screen.png"
        args_cap = ["-s", serial, "shell", "screencap", "-p", remote_path] if serial else ["shell", "screencap", "-p", remote_path]
        code, out, err = self.run_adb(args_cap, timeout=10)
        if code == 0:
            code_p, out_p, err_p = self.pull_file(serial, remote_path, local_path)
            self.run_adb(["-s", serial, "shell", "rm", remote_path] if serial else ["shell", "rm", remote_path])
            return code_p, out_p, err_p
        return code, out, err

    def start_recording(self, serial, local_path, record_audio=True):
        """Usa scrcpy para grabar en un solo proceso con parámetros universales (scrcpy 2.0+)."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        scrcpy_path = os.path.join(base_dir, "scrcpy", "scrcpy.exe")
        
        if not os.path.exists(scrcpy_path):
            logging.error(f"Scrcpy no encontrado: {scrcpy_path}")
            return None

        # Forzar MKV para robustez (permite reproducir si hay cierre inesperado)
        if not local_path.lower().endswith('.mkv'):
            local_path = os.path.splitext(local_path)[0] + ".mkv"

        log_path = os.path.join(base_dir, "cache", "scrcpy_error.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        # Obtener marca para ajustes específicos
        info = self.get_device_info(serial)
        brand = info.get("brand", "").lower()

        # Argumentos de MÁXIMA COMPATIBILIDAD UNIVERSAL (scrcpy 2.0+ / 3.0+)
        # Dejamos que scrcpy elija los encoders automáticamente para permitir auto-retry
        args = [
            scrcpy_path,
            "--no-video-playback",                     # No mostrar video duplicado en PC
            "--no-window",
            "--record", local_path,
            "--stay-awake",
            "--video-codec=h264",
            "--audio-codec=aac",
            "--max-size=1280",                         # Límite de seguridad
            "--video-bit-rate=4M",
            "--audio-bit-rate=128K"
        ]

        # PARCHE ESPECÍFICO PARA XIAOMI / HYPEROS
        if "xiaomi" in brand or "redmi" in brand or "poco" in brand:
            args.extend([
                "--audio-source=playback", 
                "--audio-codec=raw",       # EL SONIDO SE ENVÍA PURO A LA PC (La PC hace el trabajo de comprimirlo)
                "--audio-buffer=100",      # Raw es más estable, no necesita tanto buffer
                "--max-size=1280",         # Podemos subir un poco la resolución ya que el celular trabaja menos en audio
                "--video-bit-rate=4M"
            ])
        else:
            # Para el resto (Samsung, etc), mantenemos calidad estándar
            args.extend(["--max-size=1280"])
        
        if serial:
            args.extend(["-s", serial])
            
        if not record_audio:
            args.append("--no-audio")
            
        # Configurar ADB_PATH para scrcpy
        adb_path = self.get_adb_executable()
        env = os.environ.copy()
        if adb_path:
            env["ADB"] = adb_path

        try:
            log_file = open(log_path, "a", encoding="utf-8")
            # Añadir separador en el log para identificar nueva sesión
            log_file.write(f"\n--- INICIO GRABACIÓN SCRCPY: {time.ctime()} ---\n")
            process = subprocess.Popen(
                args,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP,
                env=env
            )
            logging.info(f"Grabación universal iniciada: {local_path}")
            return process
        except Exception as e:
            logging.error(f"Error al iniciar scrcpy: {e}")
            return None

    def start_mirroring(self, serial, window_title="SCRCPY - AdbAppDroid", x=None, y=None, max_size=1024):
        """Lanza scrcpy para espejo/control capturando errores en log."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        scrcpy_path = os.path.join(base_dir, "scrcpy", "scrcpy.exe")
        
        if not os.path.exists(scrcpy_path):
            logging.error(f"Scrcpy no encontrado: {scrcpy_path}")
            return None

        log_path = os.path.join(base_dir, "cache", "scrcpy_error.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        args = [
            scrcpy_path,
            "--stay-awake",
            f"--max-size={max_size}",
            "--video-bit-rate=4M",
            "--video-buffer=0",
            f"--window-title={window_title}",
            "--audio-buffer=100",  # Aumentar buffer para estabilidad
            "--audio-codec=raw"    # Raw suele ser más compatible con drivers de audio de PC (WASAPI)
        ]

        if serial:
            args.extend(["-s", serial])
        
        if x is not None: args.append(f"--window-x={x}")
        if y is not None: args.append(f"--window-y={y}")

        # Configurar ADB_PATH para scrcpy
        adb_path = self.get_adb_executable()
        env = os.environ.copy()
        if adb_path:
            env["ADB"] = adb_path

        try:
            log_file = open(log_path, "a", encoding="utf-8")
            log_file.write(f"\n--- INICIO ESPEJO SCRCPY: {time.ctime()} ---\n")
            process = subprocess.Popen(
                args,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW,
                env=env
            )
            return process
        except Exception as e:
            logging.error(f"Error al iniciar scrcpy espejo: {e}")
            return None

    def stop_recording(self, process):
        """Detiene el proceso de scrcpy de forma graciosa y rápida."""
        if not process:
            return 0

        # Si nos pasan una lista, tomamos el primero
        if isinstance(process, list):
            process = process[0] if process else None
            if not process: return 0

        try:
            if process.poll() is None:
                # Enviamos señal de interrupción para que scrcpy finalice el contenedor (MKV/MP4)
                os.kill(process.pid, signal.CTRL_C_EVENT)
                try:
                    # Espera corta de 2 segundos para cierre gracioso
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    # Si tarda más, forzamos terminación (MKV es resistente a esto)
                    process.terminate()
                    process.wait(timeout=1)
        except Exception:
            try: process.terminate()
            except: pass
        return 0


    def get_app_icon(self, serial, pkg, callback=None):
        """
        Versión optimizada: Si no está en caché, lo añade a una cola para 
        procesamiento secuencial en segundo plano.
        """
        if not pkg: return None
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cache_dir = os.path.join(base_dir, "cache", "icons")
        os.makedirs(cache_dir, exist_ok=True)
        
        icon_path = os.path.join(cache_dir, f"{pkg}.png")
        if os.path.exists(icon_path):
            if callback: self._run_callback(callback, icon_path)
            return icon_path

        # Si no hay callback, es una llamada síncrona (no recomendada para listas)
        if not callback:
            return self._extract_icon_logic(serial, pkg, icon_path)

        # Añadir a la cola si hay callback
        if not hasattr(self, '_icon_queue'):
            import queue
            import threading
            self._icon_queue = queue.Queue()
            threading.Thread(target=self._icon_worker, daemon=True).start()
        
        self._icon_queue.put((serial, pkg, icon_path, callback))
        return None

    def _icon_worker(self):
        """Worker que procesa iconos uno por uno"""
        while True:
            serial, pkg, icon_path, callback = self._icon_queue.get()
            try:
                # Si otra tarea ya lo extrajo mientras esperábamos en la cola
                if os.path.exists(icon_path):
                    self._run_callback(callback, icon_path)
                else:
                    result = self._extract_icon_logic(serial, pkg, icon_path)
                    if result:
                        self._run_callback(callback, result)
            except Exception:
                pass
            finally:
                self._icon_queue.task_done()
                time.sleep(0.1) # Pausa mínima para no saturar ADB

    def _run_callback(self, cb, val):
        try:
            cb(val)
        except Exception:
            pass

    def _extract_icon_logic(self, serial, pkg, icon_path):
        """Lógica interna de extracción (la original)"""
        # 1. Obtener ruta del APK
        code, out, _ = self.run_adb(["-s", serial, "shell", "pm", "path", pkg] if serial else ["shell", "pm", "path", pkg])
        if code != 0 or not out.strip(): return None
        apk_p = out.split(":")[1].strip()

        # 2. Intentar encontrar el path del icono dentro del APK
        code, out, _ = self.run_adb(["-s", serial, "shell", "unzip", "-l", apk_p] if serial else ["shell", "unzip", "-l", apk_p])
        if code != 0: return None
        
        patterns = [
            r"res/mipmap-xhdpi.*/ic_launcher\.(?:png|webp)",
            r"res/drawable-xhdpi.*/ic_launcher\.(?:png|webp)",
            r"res/mipmap.*/ic_launcher\.(?:png|webp)",
            r"res/drawable.*/ic_launcher\.(?:png|webp)",
            r".*ic_launcher\.(?:png|webp)",
            r".*icon\.(?:png|webp)"
        ]
        
        inner_path = None
        for p in patterns:
            match = re.search(p, out)
            if match:
                inner_path = match.group(0)
                break
        
        if not inner_path: return None

        # 3. Extraer el icono
        try:
            tmp_remote = f"/data/local/tmp/{pkg}_icon.png"
            # Redirigir unzip a un archivo temporal en el dispositivo
            self.run_adb(["-s", serial, "shell", f"unzip -p {apk_p} {inner_path} > {tmp_remote}"] if serial else ["shell", f"unzip -p {apk_p} {inner_path} > {tmp_remote}"])
            self.pull_file(serial, tmp_remote, icon_path)
            self.run_adb(["-s", serial, "shell", "rm", tmp_remote] if serial else ["shell", "rm", tmp_remote])
            
            if os.path.exists(icon_path) and os.path.getsize(icon_path) > 0:
                return icon_path
        except Exception:
            pass
        return None


    # ========== MÉTODOS DE USB TETHERING ==========
    
    def enable_usb_tethering(self, serial=None):
        """Activa USB Tethering (Android → PC)"""
        args = ["-s", serial, "shell", "svc", "usb", "setFunctions", "rndis"] if serial else ["shell", "svc", "usb", "setFunctions", "rndis"]
        code, out, err = self.run_adb(args, timeout=10)
        # En Samsung modernos, opId:1 indica que la operación se inició asíncronamente
        if "opId" in out or "opId" in err:
            return 0, out, err
        return code, out, err

    def disable_usb_tethering(self, serial=None):
        """Desactiva USB Tethering y restaura modo MTP"""
        args = ["-s", serial, "shell", "svc", "usb", "setFunctions", "mtp"] if serial else ["shell", "svc", "usb", "setFunctions", "mtp"]
        code, out, err = self.run_adb(args, timeout=10)
        if "opId" in out or "opId" in err:
            return 0, out, err
        return code, out, err

    def enable_reverse_tethering(self, serial=None, proxy_ip="127.0.0.1", proxy_port="8888"):
        """Activa Reverse Tethering (PC → Android)
        La PC comparte su internet con el dispositivo Android
        NOTA: Requiere un servidor proxy HTTP ejecutándose en la PC"""
        proxy_setting = f"{proxy_ip}:{proxy_port}"
        args = ["-s", serial, "shell", "settings", "put", "global", "http_proxy", proxy_setting] if serial else ["shell", "settings", "put", "global", "http_proxy", proxy_setting]
        return self.run_adb(args)

    def disable_reverse_tethering(self, serial=None):
        """Desactiva Reverse Tethering eliminando la configuración de proxy"""
        args = ["-s", serial, "shell", "settings", "delete", "global", "http_proxy"] if serial else ["shell", "settings", "delete", "global", "http_proxy"]
        return self.run_adb(args)

    def get_tethering_status(self, serial=None):
        """Obtiene el estado actual de las funciones de tethering"""
        # Verificar USB function actual
        args_usb = ["-s", serial, "shell", "getprop", "sys.usb.config"] if serial else ["shell", "getprop", "sys.usb.config"]
        code_usb, out_usb, _ = self.run_adb(args_usb)
        
        is_rndis = "rndis" in out_usb.lower()
        if not is_rndis and code_usb == 0:
            # Check alternativo
            args_state = ["-s", serial, "shell", "getprop", "sys.usb.state"] if serial else ["shell", "getprop", "sys.usb.state"]
            _, out_state, _ = self.run_adb(args_state)
            is_rndis = "rndis" in out_state.lower()

        # Verificar configuración de proxy
        args_proxy = ["-s", serial, "shell", "settings", "get", "global", "http_proxy"] if serial else ["shell", "settings", "get", "global", "http_proxy"]
        code_proxy, out_proxy, _ = self.run_adb(args_proxy)
        
        proxy_val = out_proxy.strip() if code_proxy == 0 else ""
        
        return {
            "usb_tethering": is_rndis,
            "reverse_tethering": proxy_val not in ["", ":0", "null"] if code_proxy == 0 else False,
            "proxy_value": proxy_val if proxy_val not in ["", "null"] else None
        }

    def get_running_processes(self, serial=None):
        """Obtiene la lista de procesos con una lógica de parseo ultra-robusta"""
        args = ["-s", serial, "shell", "top", "-b", "-n", "1"] if serial else ["shell", "top", "-b", "-n", "1"]
        code, out, _ = self.run_adb(args, timeout=10)
        
        if code != 0 or not out.strip():
            # Fallback a ps -A si top falla
            args = ["-s", serial, "shell", "ps", "-A"]
            code, out, _ = self.run_adb(args, timeout=5)
            if code != 0: return []

        processes = []
        lines = out.splitlines()
        header_idx = -1
        col_map = {}
        
        for i, line in enumerate(lines):
            line_upper = line.upper()
            if "PID" in line_upper and ("NAME" in line_upper or "CMD" in line_upper or "ARGS" in line_upper or "PACKAGE" in line_upper):
                header_idx = i
                
                # Pre-procesar cabecera para separar columnas pegadas como S[%CPU] o S%CPU
                processed_header = re.sub(r'([A-Z])(\[?%CPU\]?)', r'\1 \2', line)
                processed_header = re.sub(r'([A-Z])(\[?%MEM\]?)', r'\1 \2', processed_header)
                
                cols = processed_header.split()
                # Limpiar y mapear columnas
                for idx, col in enumerate(cols):
                    clean_col = re.sub(r'\W+', '', col).upper()
                    col_map[clean_col] = idx
                break
        
        if header_idx != -1:
            for line in lines[header_idx + 1:]:
                parts = line.split()
                if len(parts) < 3: continue
                try:
                    pid = parts[col_map.get("PID", 0)]
                    user = parts[col_map.get("USER", 1)] if "USER" in col_map else "root"
                    cpu_idx = col_map.get("CPU", -1)
                    if cpu_idx == -1:
                        for k, v in col_map.items():
                            if "CPU" in k: cpu_idx = v; break
                    mem_idx = col_map.get("MEM", -1)
                    if mem_idx == -1:
                        for k, v in col_map.items():
                            if "MEM" in k: mem_idx = v; break
                    cpu = parts[cpu_idx] if cpu_idx != -1 and len(parts) > cpu_idx else "0"
                    mem = parts[mem_idx] if mem_idx != -1 and len(parts) > mem_idx else "0"
                    name_keys = ["NAME", "CMD", "ARGS", "PACKAGE"]
                    name_idx = -1
                    for k in name_keys:
                        if k in col_map: name_idx = col_map[k]; break
                    if name_idx == -1: name_idx = len(parts) - 1
                    name = " ".join(parts[name_idx:])
                    name = re.sub(r'\x1B\[[0-9;]*[mK]', '', name).strip()
                    if not name or name.startswith("[") or name == "top" or name == "ps": continue
                    processes.append({"pid": pid, "user": user, "cpu": cpu.strip("%"), "mem": mem.strip("%"), "name": name})
                except: continue
        
        if not processes and len(lines) > 5:
            for line in lines[5:]: 
                parts = line.split()
                if len(parts) >= 8: 
                    try:
                        cpu_val = parts[8] if "%" in parts[8] or parts[8].replace(".","").isdigit() else "0"
                        mem_val = parts[9] if "%" in parts[9] or parts[9].replace(".","").isdigit() else "0"
                        processes.append({"pid": parts[0], "user": parts[1], "cpu": cpu_val, "mem": mem_val, "name": parts[-1]})
                    except: continue
        return processes
        
    def get_cpu_cores(self, serial=None):
        """Obtiene el número de núcleos de la CPU"""
        try:
            code, out, _ = self.run_adb(["-s", serial, "shell", "cat /proc/cpuinfo"] if serial else ["shell", "cat /proc/cpuinfo"])
            if code == 0:
                return len(re.findall(r"processor\s*:", out))
        except: pass
        return 1

    def get_cpu_usage(self, serial=None):
        """Obtiene el porcentaje total de uso de CPU del dispositivo (Normalizado 0-100%)"""
        if not serial: return 0
        
        args = ["-s", serial, "shell", "top", "-b", "-n", "1"]
        code, out, _ = self.run_adb(args, timeout=5)
        
        if code == 0:
            # Estrategia 1: Línea summary "800%cpu 12%user... 788%idle"
            idle_match = re.search(r"(\d+)%\s*idle", out.lower())
            cpu_match = re.search(r"(\d+)%\s*cpu", out.lower())
            
            if idle_match and cpu_match:
                try:
                    idle = int(idle_match.group(1))
                    total = int(cpu_match.group(1))
                    if total > 0:
                        usage = round(((total - idle) / total) * 100)
                        return max(0, min(100, usage))
                except: pass

            # Estrategia 2: Formato "User 2%, System 3%, Idle 95%"
            match_idle = re.search(r"[Ii]dle\s+(\d+)%", out)
            if match_idle:
                return 100 - int(match_idle.group(1))

            # Estrategia 3: Si todo falla, sumar columna %CPU pero detectando núcleos
            cores = self.get_cpu_cores(serial)
            lines = out.splitlines()
            cpu_idx = -1
            total_sum = 0
            for i, line in enumerate(lines):
                if "%CPU" in line.upper() or "CPU%" in line.upper():
                    cols = line.split()
                    for idx, col in enumerate(cols):
                        if "CPU" in col.upper():
                            cpu_idx = idx
                            break
                    break
            
            if cpu_idx != -1:
                for line in lines[i+1:]:
                    parts = line.split()
                    if len(parts) > cpu_idx:
                        try:
                            val = float(parts[cpu_idx].strip("%"))
                            total_sum += val
                        except: pass
                
                # Si la suma es muy alta (ej: 800), dividimos por núcleos
                if total_sum > 100:
                    return min(100, int(total_sum / cores))
                return int(total_sum)

        return 0

