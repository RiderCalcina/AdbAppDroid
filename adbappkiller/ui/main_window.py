import customtkinter as ctk
import threading
import time
import os
import subprocess
from tkinter import messagebox, filedialog
from .components import AppInfoWidget, CTKToolTip, RSSFeedWidget, CTkWarningDialog, RSSMarqueeWidget, CPUGraphWidget
from .process_monitor import ProcessMonitorWindow
from ..core.adb_controller import ADBController
from ..core.downloader import Downloader
from ..utils.config import THEME, PELIGROSOS
from ..utils.helpers import safe_str
from ..utils.config_manager import ConfigManager
from PIL import Image

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AdbAppDroid")
        
        # Icono de la ventana
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        
        # Geometría horizontal
        window_width = 864
        window_height = 600
        
        # Posicionamiento a la izquierda con margen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        margin = 50
        x = margin
        y = (screen_height // 2) - (window_height // 2)
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        
        self.adb = ADBController()
        self.downloader = Downloader(log_callback=self.add_log)
        self.history = ConfigManager()
        
        self.running = True
        self.current_app = None
        self.active_serial = None
        self.scrcpy_processes = {}
        self.recording_processes = {}
        
        # Animación
        self.pulse_val = 0
        self.pulse_dir = 1
        
        # Botones de instalación dinámicos
        self._btn_inst_adb = None
        self._btn_inst_scrcpy = None
        self.process_monitor = None
        
        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.after(100, self.initialize)
        self.pulse_animation()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        # self.grid_rowconfigure(2, weight=0) # ELIMINAR (ya no habrá fila global abajo)

        # 0. Connection Status Indicator (Global)
        self.status_header = ctk.CTkFrame(self, fg_color=THEME["CARD"], height=45, corner_radius=0)
        self.status_header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.status_header.grid_propagate(False)
        
        # --- LADO DERECHO: Botones y especificaciones ---
        self.btn_help = ctk.CTkButton(self.status_header, text="?", width=35, height=35, font=("Segoe UI", 18), fg_color="transparent", hover_color=THEME["BUTTON_SECONDARY"], text_color="#FFFF00", command=self.open_help)
        self.btn_help.pack(side="right", padx=(2, 10))
        CTKToolTip(self.btn_help, "Información y ayuda del aplicativo")



        self.specs_label = ctk.CTkLabel(self.status_header, text="", font=("Segoe UI", 12), text_color=THEME["TEXT_MAIN"])
        self.specs_label.pack(side="right", padx=(10, 5), pady=(2, 0))

        # --- LADO IZQUIERDO: Estado de conexión ---
        self.indicator_dot = ctk.CTkLabel(self.status_header, text="●", font=("Segoe UI", 22), text_color=THEME["TEXT_SEC"])
        self.indicator_dot.pack(side="left", padx=(15, 5))

        self.device_combo = ctk.CTkOptionMenu(self.status_header, values=["SIN CONEXIÓN"], command=self.on_device_selected, width=160, fg_color=THEME["BUTTON_SECONDARY"], button_color=THEME["BUTTON_SECONDARY"], button_hover_color=THEME["BUTTON_SECONDARY_HOVER"], font=("Segoe UI", 12, "bold"))
        self.device_combo.pack(side="left", padx=5, pady=(2, 0))

        self.conn_type_label = ctk.CTkLabel(self.status_header, text="", font=("Segoe UI", 12), text_color=THEME["TEXT_MAIN"])
        self.conn_type_label.pack(side="left", padx=10, pady=(2, 0))

        # Main horizontal container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.main_container.grid_columnconfigure(0, weight=6) # Log panel
        self.main_container.grid_columnconfigure(1, weight=4) # Control panel
        self.main_container.grid_rowconfigure(0, weight=1)

        # --- LEFT PANEL (LOGS & INFO) ---
        self.left_panel = ctk.CTkFrame(self.main_container, fg_color="transparent", width=510, height=520)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(2, weight=1) # The info widget row should expand
        self.left_panel.grid_propagate(False)

        # 1. Header: App Activa (Moved to Left)
        self.header_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent", height=60, width=510)
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.header_frame.grid_propagate(False)
        
        self.app_icon_label = ctk.CTkLabel(self.header_frame, text="", width=48, height=48)
        self.app_icon_label.pack(side="left", padx=(0, 10))

        self.app_label = ctk.CTkLabel(
            self.header_frame, text="Esperando detección...", 
            font=("Segoe UI", 18, "bold"), text_color=THEME["SUCCESS"],
            anchor="w", justify="left")
        self.app_label.pack(side="left", fill="x", expand=True)

        # 2. Progress Bar
        self.progress = ctk.CTkProgressBar(self.left_panel, height=2)
        self.progress.grid(row=1, column=0, sticky="ew", pady=2)
        self.progress.set(0)

        # 3. Info Area
        self.info_widget = AppInfoWidget(self.left_panel, height=450)
        self.info_widget.grid(row=2, column=0, sticky="nsew", pady=5)

        # --- RIGHT PANEL (CONTROLS) ---
        self.right_panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.right_panel.grid_columnconfigure(0, weight=1)

        # WiFi Frame
        self.wifi_frame = ctk.CTkFrame(self.right_panel, border_width=1, border_color=THEME["BORDER"], fg_color=THEME["CARD"], corner_radius=8)
        self.wifi_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.wifi_frame.grid_columnconfigure(1, weight=2)
        self.wifi_frame.grid_columnconfigure(3, weight=1)
        self.wifi_frame.grid_columnconfigure(4, weight=1)
        
        # WiFi - Título integrado en la primera fila para ahorrar espacio
        ctk.CTkLabel(self.wifi_frame, text="📡 CONEXIÓN POR DEPURACIÓN INALÁMBRICA", font=("Segoe UI", 10, "bold"), text_color=THEME["TEXT_SEC"]).grid(row=0, column=0, columnspan=2, padx=10, sticky="w", pady=(5,0))
        
        ctk.CTkLabel(self.wifi_frame, text="IP:", font=("Segoe UI", 11), text_color=THEME["TEXT_MAIN"]).grid(row=1, column=0, padx=(10, 2), pady=(5, 10))
        self.wifi_ip_entry = ctk.CTkEntry(self.wifi_frame, placeholder_text="192.168.1.5", placeholder_text_color=THEME["TEXT_SEC"], width=120, height=28, fg_color=THEME["BG"], border_color=THEME["BORDER"], text_color=THEME["TEXT_MAIN"], corner_radius=6, font=("Segoe UI", 11))
        self.wifi_ip_entry.grid(row=1, column=1, padx=2, pady=(5, 10), sticky="ew")
        self.wifi_ip_entry.bind("<Enter>", lambda e: self.wifi_ip_entry.configure(placeholder_text=""))
        self.wifi_ip_entry.bind("<Leave>", lambda e: self.wifi_ip_entry.configure(placeholder_text="192.168.1.5"))
        
        ctk.CTkLabel(self.wifi_frame, text="Puerto:", font=("Segoe UI", 11), text_color=THEME["TEXT_MAIN"]).grid(row=1, column=2, padx=(5, 2), pady=(5, 10))
        self.wifi_port_entry = ctk.CTkEntry(self.wifi_frame, placeholder_text="5555", placeholder_text_color=THEME["TEXT_SEC"], width=60, height=28, fg_color=THEME["BG"], border_color=THEME["BORDER"], text_color=THEME["TEXT_MAIN"], corner_radius=6, font=("Segoe UI", 11))
        self.wifi_port_entry.grid(row=1, column=3, padx=2, pady=(5, 10), sticky="ew")
        self.wifi_port_entry.bind("<Enter>", lambda e: self.wifi_port_entry.configure(placeholder_text=""))
        self.wifi_port_entry.bind("<Leave>", lambda e: self.wifi_port_entry.configure(placeholder_text="5555"))
        
        self.btn_wifi_toggle = ctk.CTkButton(self.wifi_frame, text="Conectar", width=110, height=28, fg_color=THEME["BUTTON_SECONDARY"], hover_color=THEME["BUTTON_SECONDARY_HOVER"], text_color="#FFFFFF", corner_radius=6, command=self.toggle_wifi, font=("Segoe UI", 11, "bold"))
        self.btn_wifi_toggle.grid(row=1, column=4, columnspan=3, padx=(2, 10), pady=(5, 10), sticky="ew")

        # 2. Actions Area
        self.actions_container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.actions_container.grid(row=1, column=0, sticky="nsew")
        self.actions_container.grid_columnconfigure(0, weight=1)

        btn_style = {"height": 32, "font": ("Segoe UI", 11), "corner_radius": 6}
        btn_action_style = btn_style.copy()
        btn_action_style["fg_color"] = THEME["BUTTON_SECONDARY"]
        btn_action_style["hover_color"] = THEME["BUTTON_SECONDARY_HOVER"]

        # --- SECCIÓN: GESTIÓN DE APLICACIONES ---
        self.app_mng_frame = ctk.CTkFrame(self.actions_container, fg_color=THEME["CARD"], border_width=1, border_color=THEME["BORDER"], corner_radius=8)
        self.app_mng_frame.pack(fill="x", pady=(0, 10), padx=2)
        
        # Título más sutil y pegado para ahorrar espacio
        ctk.CTkLabel(self.app_mng_frame, text="📦 GESTIÓN DE APLICACIONES", font=("Segoe UI", 10, "bold"), text_color=THEME["TEXT_SEC"]).pack(anchor="w", padx=10, pady=(5, 0))
        
        self.app_btns_grid = ctk.CTkFrame(self.app_mng_frame, fg_color="transparent")
        self.app_btns_grid.pack(fill="x", padx=5, pady=5)
        self.app_btns_grid.grid_columnconfigure((0, 1), weight=1)

        self.btn_uninst = ctk.CTkButton(self.app_btns_grid, text="🗑 Desinstalar", command=self.uninstall, **btn_action_style)
        self.btn_uninst.grid(row=0, column=0, padx=5, pady=4, sticky="ew")
        CTKToolTip(self.btn_uninst, "Elimina la aplicación seleccionada del dispositivo")

        self.btn_disable = ctk.CTkButton(self.app_btns_grid, text="🚫 Desactivar", command=self.disable_app, **btn_action_style)
        self.btn_disable.grid(row=0, column=1, padx=5, pady=4, sticky="ew")
        CTKToolTip(self.btn_disable, "Desactiva la app (congelar) sin desinstalarla")

        self.btn_clear = ctk.CTkButton(self.app_btns_grid, text="🧹 Limpiar Datos", command=self.clear_data, **btn_action_style)
        self.btn_clear.grid(row=1, column=0, padx=5, pady=4, sticky="ew")
        CTKToolTip(self.btn_clear, "Borra todos los datos y caché de la aplicación")

        self.btn_ext = ctk.CTkButton(self.app_btns_grid, text="💾 Extraer APK", command=self.extract, **btn_action_style)
        self.btn_ext.grid(row=1, column=1, padx=5, pady=4, sticky="ew")
        CTKToolTip(self.btn_ext, "Copia el archivo instalador (.apk) al ordenador")

        self.btn_install = ctk.CTkButton(self.app_btns_grid, text="📥 Instalar APK", command=self.install_apk, **btn_action_style)
        self.btn_install.grid(row=2, column=0, padx=5, pady=4, sticky="ew")
        CTKToolTip(self.btn_install, "Instala un archivo .apk desde tu ordenador al dispositivo")

        self.btn_report = ctk.CTkButton(self.app_btns_grid, text="📄 Guardar Informe", command=self.save_session_report, **btn_action_style)
        self.btn_report.grid(row=2, column=1, padx=5, pady=4, sticky="ew")
        CTKToolTip(self.btn_report, "Descarga un informe detallado de la sesión en formato .txt")

        # Monitor processes uses primary accent
        self.btn_monitor = ctk.CTkButton(self.app_btns_grid, text="📊 Monitor de procesos", fg_color=THEME["BUTTON_SECONDARY"], hover_color=THEME["BUTTON_SECONDARY_HOVER"], command=self.open_process_monitor, **btn_style)
        self.btn_monitor.grid(row=3, column=0, columnspan=2, padx=5, pady=4, sticky="ew")
        CTKToolTip(self.btn_monitor, "Ver procesos y consumo de recursos en tiempo real")

        # --- SECCIÓN: CONTROL DE PANTALLA ---
        self.scr_mng_frame = ctk.CTkFrame(self.actions_container, fg_color=THEME["CARD"], border_width=1, border_color=THEME["BORDER"], corner_radius=8)
        self.scr_mng_frame.pack(fill="x", pady=2, padx=2)

        ctk.CTkLabel(self.scr_mng_frame, text="📱 CONTROL DE PANTALLA", font=("Segoe UI", 10, "bold"), text_color=THEME["TEXT_SEC"]).pack(anchor="w", padx=10, pady=(5, 0))

        self.scr_btns_grid = ctk.CTkFrame(self.scr_mng_frame, fg_color="transparent")
        self.scr_btns_grid.pack(fill="x", padx=5, pady=5)
        self.scr_btns_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Screen buttons use primary accent
        self.btn_folder = ctk.CTkButton(self.scr_btns_grid, text="📁 Carpeta", fg_color=THEME["BUTTON_SECONDARY"], hover_color=THEME["BUTTON_SECONDARY_HOVER"], command=self.change_output_dir, **btn_style)
        self.btn_folder.grid(row=0, column=0, padx=5, pady=4, sticky="ew")
        CTKToolTip(self.btn_folder, "Seleccionar carpeta de salida para capturas y videos")

        self.btn_scrcpy = ctk.CTkButton(self.scr_btns_grid, text="▶ Espejo", fg_color=THEME["BUTTON_SECONDARY"], hover_color=THEME["BUTTON_SECONDARY_HOVER"], command=self.launch_scrcpy, **btn_style)
        self.btn_scrcpy.grid(row=0, column=1, padx=5, pady=4, sticky="ew")
        CTKToolTip(self.btn_scrcpy, "Abre una ventana para ver y controlar el dispositivo")

        self.btn_screenshot = ctk.CTkButton(self.scr_btns_grid, text="📸 Capturar", fg_color=THEME["BUTTON_SECONDARY"], hover_color=THEME["BUTTON_SECONDARY_HOVER"], command=self.capture_screen, **btn_style)
        self.btn_screenshot.grid(row=0, column=2, padx=5, pady=4, sticky="ew")
        CTKToolTip(self.btn_screenshot, "Toma una foto de la pantalla actual")

        self.btn_record = ctk.CTkButton(self.scr_btns_grid, text="🎥 Grabar", fg_color=THEME["BUTTON_SECONDARY"], hover_color=THEME["BUTTON_SECONDARY_HOVER"], command=self.toggle_recording, **btn_style)
        self.btn_record.grid(row=0, column=3, padx=5, pady=4, sticky="ew")
        CTKToolTip(self.btn_record, "Graba un video de lo que sucede en el dispositivo")

        # 3. CPU Graph instead of full RSS
        self.cpu_graph = CPUGraphWidget(self.right_panel)
        self.cpu_graph.grid(row=2, column=0, sticky="nsew", pady=(10, 5), padx=2)
        
        # 4. RSS MARQUEE (AQUÍ DENTRO)
        self.rss_marquee = RSSMarqueeWidget(self.right_panel, feed_url="https://qwertyaserty.com/rblog/rss")
        self.rss_marquee.grid(row=3, column=0, sticky="ew", pady=(0, 5), padx=2)
        
        self.right_panel.grid_rowconfigure(2, weight=1)
        self.right_panel.grid_rowconfigure(3, weight=0)





    def open_link(self, url):
        import webbrowser
        webbrowser.open(url)

    def on_device_selected(self, choice):
        if choice == "SIN CONEXIÓN" or not choice:
            self.active_serial = None
            return
            
        serial = choice.split(" (")[0]
        if self.active_serial != serial:
            self.active_serial = serial
            self.current_app = None # Forzar actualización
            if hasattr(self, 'log_activity'): self.log_activity(f"Cambiado a dispositivo: {serial}")
            self.update_device_header_info_from_choice(choice)

    def pulse_animation(self):
        if not self.running: return
        # Oscila entre 0 y 255
        self.pulse_val += 15 * self.pulse_dir
        if self.pulse_val >= 255:
            self.pulse_val = 255
            self.pulse_dir = -1
        elif self.pulse_val <= 100:
            self.pulse_val = 100
            self.pulse_dir = 1
        
        # Color verde brillante pulsante si hay conexión
        color = f"#{0:02x}{self.pulse_val:02x}{int(self.pulse_val*0.6):02x}"
        if self.active_serial:
            self.indicator_dot.configure(text_color=color)
        else:
            self.indicator_dot.configure(text_color="#555")
            
        self.after(50, self.pulse_animation)

    def initialize(self):
        threading.Thread(target=self.monitor_loop, daemon=True).start()
        threading.Thread(target=self.device_monitor, daemon=True).start()
        self.check_tools()

    def check_tools(self):
        if not self.adb.get_adb_executable():
            self.show_install_adb()
        # Verificar scrcpy en la raíz relativa al script
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if not os.path.exists(os.path.join(base_dir, "scrcpy", "scrcpy.exe")):
            self.show_install_scrcpy()

    def show_install_adb(self):
        if not self._btn_inst_adb:
            self._btn_inst_adb = ctk.CTkButton(self.right_panel, text="📥 Instalar ADB (Local)", fg_color=THEME["BUTTON_SECONDARY"], height=28, command=self.install_adb)
            self._btn_inst_adb.grid(row=2, column=0, pady=5, sticky="ew")

    def show_install_scrcpy(self):
        if not self._btn_inst_scrcpy:
            self._btn_inst_scrcpy = ctk.CTkButton(self.right_panel, text="📥 Instalar scrcpy (Local)", fg_color=THEME["BUTTON_SECONDARY"], height=28, command=self.install_scrcpy)
            self._btn_inst_scrcpy.grid(row=3, column=0, pady=5, sticky="ew")

    def install_adb(self):
        self._btn_inst_adb.configure(state="disabled", text="Instalando...")
        def task():
            if self.downloader.install_adb_locally():
                self.after(0, self._btn_inst_adb.destroy)
                self.add_log("✅ ADB instalado. Reiniciando conexión...")
            else:
                self.after(0, lambda: self._btn_inst_adb.configure(state="normal", text="📥 Reintentar ADB"))
        threading.Thread(target=task, daemon=True).start()

    def install_scrcpy(self):
        self._btn_inst_scrcpy.configure(state="disabled", text="Instalando...")
        def task():
            if self.downloader.install_scrcpy_locally():
                self.after(0, self._btn_inst_scrcpy.destroy)
                self.add_log("✅ scrcpy instalado.")
            else:
                self.after(0, lambda: self._btn_inst_scrcpy.configure(state="normal", text="📥 Reintentar scrcpy"))
        threading.Thread(target=task, daemon=True).start()

    def add_log(self, msg):
        self.info_widget.log(msg)

    def set_status(self, msg):
        # Forward status messages to the log area since the bottom status bar is removed
        if "Conectando" in msg or "Tomando captura" in msg or "Grabando" in msg:
            self.add_log(f"ℹ️ {msg}")

    def toggle_wifi(self):
        text = self.btn_wifi_toggle.cget("text")
        if "Conectar" in text:
            self.connect_wifi()
        else:
            self.disconnect_wifi()

    def connect_wifi(self):
        ip = self.wifi_ip_entry.get()
        port = self.wifi_port_entry.get() or "5555"
        if not ip: return
        full_endpoint = f"{ip}:{port}"
        self.set_status(f"Conectando a {full_endpoint}...")
        self.btn_wifi_toggle.configure(state="disabled")
        
        def task():
            code, out, err = self.adb.connect_wireless(full_endpoint)
            if "connected" in out.lower():
                self.add_log(f"✅ Conectado a {full_endpoint}")
            else:
                self.add_log(f"❌ Error WiFi: {out or err}")
            self.after(0, lambda: self.btn_wifi_toggle.configure(state="normal"))
            
        threading.Thread(target=task, daemon=True).start()

    def disconnect_wifi(self):
        # Tomar valores antes de que se desconecte para el log
        ip = self.wifi_ip_entry.get()
        port = self.wifi_port_entry.get()
        full_endpoint = f"{ip}:{port}" if ip and port else ip
        
        self.set_status(f"Desconectando {full_endpoint or 'todo'}...")
        self.btn_wifi_toggle.configure(state="disabled", text="Desconectando...")
        
        def task():
            # Forzar desconexión
            code, out, err = self.adb.disconnect_wireless(full_endpoint)
            # Doble check: si no se especificó IP, desconectar todo puede requerir un segundo intento o kill-server (evitado por ahora)
            if "error" in out.lower() or "error" in err.lower():
                time.sleep(1)
                code, out, err = self.adb.disconnect_wireless(full_endpoint)
            
            # Resultado
            res_msg = out.strip() or err.strip() or "Desconectado"
            self.add_log(f"🔌 {res_msg}")
            
            # Limpiar estado interno
            if not full_endpoint or not ip: # Si fue desconexión general
                self.active_serial = None
            
            # Actualizar botón en el hilo principal
            self.after(0, lambda: self._post_disconnect_ui())
            
        threading.Thread(target=task, daemon=True).start()

    def _post_disconnect_ui(self):
        self.btn_wifi_toggle.configure(state="normal", text="Conectar", fg_color=THEME["BUTTON_SECONDARY"], hover_color=THEME["BUTTON_SECONDARY_HOVER"])
        self.device_combo.set("SIN CONEXIÓN")
        self.device_combo.configure(values=["SIN CONEXIÓN"])
        self.conn_type_label.configure(text="")


    def device_monitor(self):
        last_state = None
        while self.running:
            devs = self.adb.get_connected_devices()
            state_key = str(devs)
            if state_key != last_state:
                last_state = state_key
                self.current_app = None # Forzar refresco de monitor de app
                
                valid_devs = [d for d in devs if d['status'] == 'device']
                
                if not valid_devs:
                    self.after(0, lambda: self.device_combo.configure(values=["SIN CONEXIÓN"]))
                    self.after(0, lambda: self.device_combo.set("SIN CONEXIÓN"))
                    self.after(0, lambda: self.conn_type_label.configure(text="", text_color=THEME["TEXT_SEC"]))
                    self.after(0, lambda: self.specs_label.configure(text=""))
                    self.after(0, lambda: self.app_label.configure(text="Esperando detección..."))
                    self.after(0, lambda: self.app_icon_label.configure(image=None))
                    self.after(0, lambda: self.info_widget.clear())
                    if self.active_serial:
                        if hasattr(self, 'log_activity'): self.log_activity(f"Dispositivo desconectado: {self.active_serial}")
                    self.active_serial = None
                else:
                    # Preparar lista para el combobox
                    combo_values = [f"{d['serial']} ({d['type']})" for d in valid_devs]
                    self.after(0, lambda vals=combo_values: self.device_combo.configure(values=vals))
                    
                    # Si el dispositivo activo ya no está, o no hay ninguno activo, seleccionar el primero
                    current_active_valid = any(d['serial'] == self.active_serial for d in valid_devs)
                    if not current_active_valid:
                        new_active = valid_devs[0]
                        self.active_serial = new_active['serial']
                        new_choice = combo_values[0]
                        self.after(0, lambda c=new_choice: self.device_combo.set(c))
                        if hasattr(self, 'log_activity'): self.log_activity(f"Dispositivo detectado/activo: {new_active['serial']} ({new_active['type']})")
                    else:
                        # Mantener selección visual actual
                        active_type = next((d['type'] for d in valid_devs if d['serial'] == self.active_serial), "USB")
                        current_choice = f"{self.active_serial} ({active_type})"
                        self.after(0, lambda c=current_choice: self.device_combo.set(c))
                        
                    # Determinar tipo de conexión para el botón WiFi y etiqueta (usando el serial activo)
                    types = [d['type'] for d in valid_devs]
                    active_type = next((d['type'] for d in valid_devs if d['serial'] == self.active_serial), "USB")
                    
                    msg = f"VÍA {active_type}"
                    if "WiFi" in types and "USB" in types:
                        msg = f"{msg} (MÚLTIPLES DISP.)"
                        
                    self.after(0, lambda m=msg: self.conn_type_label.configure(text=m, text_color=THEME["TEXT_MAIN"]))
                    
                    if "WiFi" in types:
                        self.after(0, lambda: self.btn_wifi_toggle.configure(text="Desconectar", fg_color=THEME["BUTTON_SECONDARY"], hover_color=THEME["BUTTON_SECONDARY_HOVER"]))
                    else:
                        self.after(0, lambda: self.btn_wifi_toggle.configure(text="Conectar", fg_color=THEME["BUTTON_SECONDARY"], hover_color=THEME["BUTTON_SECONDARY_HOVER"]))
                        
                    self.update_device_header_info(self.active_serial, THEME["TEXT_MAIN"], msg)
                    
            time.sleep(3)

    def update_device_header_info_from_choice(self, choice):
        serial = choice.split(" (")[0]
        active_type = choice.split(" (")[1].replace(")", "")
        msg = f"VÍA {active_type}"
        self.after(0, lambda m=msg: self.conn_type_label.configure(text=m, text_color=THEME["TEXT_MAIN"]))
        self.update_device_header_info(serial, THEME["TEXT_MAIN"], msg)

    def update_device_header_info(self, serial, color, conn_msg):
        def task():
            info = self.adb.get_device_info(serial)
            brand_model = f"{info['brand']} {info['model']}".upper()
            specs_text = f"{brand_model} | RAM: {info['ram']} | CPU: {info['cpu']} | {info['screen']} | 🔋 {info['battery']} | 💾 {info['storage']}"
            
            # Verificar si el dispositivo sigue siendo el activo antes de actualizar UI
            if self.active_serial == serial:
                self.after(0, lambda: self.specs_label.configure(text=specs_text, text_color=THEME["TEXT_MAIN"]))

        threading.Thread(target=task, daemon=True).start()

    def monitor_loop(self):
        while self.running:
            app = self.adb.get_foreground_app(self.active_serial)
            if app != self.current_app:
                if app:
                    self.log_activity(f"App en primer plano: {app}")
                self.current_app = app
                self.root_update_app_info(app)
            # Update CPU Graph if device is connected
            if self.active_serial:
                cpu_usage = self.adb.get_cpu_usage(self.active_serial)
                self.after(0, lambda v=cpu_usage: self.cpu_graph.update_value(v))
            
            time.sleep(1.0)

    def root_update_app_info(self, pkg):
        self.after(0, lambda: self.update_app_info(pkg))

    def update_app_info(self, pkg):
        self.info_widget.clear()
        if not pkg:
            self.app_label.configure(text="Esperando detección...")
            self.app_icon_label.configure(image=None)
            return
        
        # UI Feedback inmediato
        self.app_label.configure(text=f"App: {pkg}")
        self.app_icon_label.configure(image=None)
        self.info_widget.log("Cargando detalles...")

        # Lanzar obtención de datos en hilo separado
        def fetch_details():
            # 1. Cargar Icono
            self.load_app_icon(self.active_serial, pkg)
            
            # 2. Cargar Detalles
            details = self.adb.get_app_details(self.active_serial, pkg)
            
            # 3. Actualizar UI en el hilo principal
            self.after(0, lambda: self._apply_app_details(details))

        threading.Thread(target=fetch_details, daemon=True).start()

    def _apply_app_details(self, details):
        if not details:
            self.info_widget.clear()
            self.info_widget.log("No se pudieron obtener detalles de la app.")
            return

        self.info_widget.clear()
        self.info_widget.log(f"📦 {details['name']}", "bold")
        self.info_widget.log(f"Paquete: {details['package']}\n")
        
        self.info_widget.log(f"Tipo: {'Sistema' if details['is_system'] else 'Usuario'}")
        self.info_widget.log(f"Versión: {details['version']}")
        self.info_widget.log(f"Instalada: {details['install_time']}")
        self.info_widget.log(f"UID: {details['uid']}")

        requested = details.get('requested_permissions', [])
        granted = details.get('granted_permissions', [])

        if requested:
            # Dividir en peligrosos y normales
            dangerous = [p for p in requested if p in PELIGROSOS]
            others = [p for p in requested if p not in PELIGROSOS]

            if dangerous:
                self.info_widget.log("\n⚠️ Permisos Peligrosos:", "danger")
                for p in dangerous:
                    if p in granted:
                        self.info_widget.log(f" - ✅ {p}", "danger")
                    else:
                        self.info_widget.log(f" - ❌ {p} (Inactivo)", "inactive")
            
            if others:
                self.info_widget.log("\n🔹 Otros Permisos:")
                for p in others:
                    if p in granted:
                        self.info_widget.log(f" - ✅ {p}", "granted")
                    else:
                        self.info_widget.log(f" - ❌ {p} (Inactivo)", "inactive")

        # Rutas al final
        paths = details.get("apk_paths", [])
        if paths:
            self.info_widget.log("\n📁 Rutas APK:")
            for p in paths: self.info_widget.log(f" - {p}")
        
        self.info_widget.scroll_to_top()

    def load_app_icon(self, serial, pkg):
        # Usar la cola del controlador para cargar el icono
        self.adb.get_app_icon(serial, pkg, callback=self.on_monitor_icon_loaded)

    def on_monitor_icon_loaded(self, icon_path):
        if icon_path and os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(48, 48))
                self.after(0, lambda: self.app_icon_label.configure(image=ctk_img))
            except Exception:
                self.after(0, lambda: self.app_icon_label.configure(image=None))
        else:
            self.after(0, lambda: self.app_icon_label.configure(image=None))


    def uninstall(self):
        if not self.current_app: return
        
        details = self.adb.get_app_details(self.current_app)
        is_system = details.get("is_system", False)
        
        if is_system:
            msg = f"⚠ AVISO CRÍTICO: {self.current_app}\n\nEsta es una APLICACIÓN DEL SISTEMA.\n\nDesinstalar aplicaciones clave del sistema puede causar fallas irrecuperables, bucles de reinicio (bootloops) o la pérdida total de funcionalidad de tu teléfono.\n\n¿Estás absolutamente seguro de que deseas correr el riesgo y continuar con la DESINSTALACIÓN?"
            dialog = CTkWarningDialog(self, title="⚠ ADVERTENCIA DE SISTEMA", message=msg)
            if not dialog.get_result():
                return
        else:
            if not messagebox.askyesno("Confirmar", f"¿Desinstalar {self.current_app}?"): return
            
        self.progress.set(0.5)
        def task():
            target = self.current_app
            code, out, _ = self.adb.uninstall_app(self.active_serial, target)
            self.progress.set(1)
            self.add_log(f"🗑 Desinstalación: {out.strip()}")
            self.log_activity(f"Desinstaló aplicación: {target} -> {out.strip()}")
            time.sleep(1)
            self.progress.set(0)
        threading.Thread(target=task, daemon=True).start()

    def disable_app(self):
        if not self.current_app: return
        
        details = self.adb.get_app_details(self.current_app)
        is_system = details.get("is_system", False)
        
        if is_system:
            msg = f"⚠ AVISO: {self.current_app}\n\nEstás a punto de desactivar (congelar) una aplicación del sistema.\n\nSi bien esto no borra la app, desactivar servicios importantes puede causar inestabilidad del sistema o fallas en otras aplicaciones.\n\n¿Deseas continuar y DESACTIVARLA?"
            dialog = CTkWarningDialog(self, title="⚠ ADVERTENCIA DE SISTEMA", message=msg)
            if not dialog.get_result():
                return
        else:
            if not messagebox.askyesno("Desactivar", f"¿Deseas DESACTIVAR la app {self.current_app}?"): return
            
        self.progress.set(0.5)
        def task():
            target = self.current_app
            code, out, _ = self.adb.disable_app(self.active_serial, target)
            self.progress.set(1)
            self.add_log(f"🚫 Desactivación: {out.strip()}")
            self.log_activity(f"Desactivó aplicación (congeló): {target}")
            time.sleep(1)
            self.progress.set(0)
        threading.Thread(target=task, daemon=True).start()

    def extract(self):
        if not self.current_app: return
        
        # Sincronización de ruta con ajustes
        initial_dir = self.history.get_output_dir()
        
        path = filedialog.asksaveasfilename(
            defaultextension=".apk", 
            initialdir=initial_dir,
            initialfile=f"{self.current_app}.apk",
            title="Extraer APK"
        )
        if not path: return
        
        details = self.adb.get_app_details(self.current_app)
        apks = details.get("apk_paths", [])
        if not apks: return

        self.progress.set(0.1)
        def task():
            # Simplificado: solo el primero por ahora o aviso si son varios
            if len(apks) > 1: self.add_log("⚠️ App múltiple, extrayendo base...")
            code, out, err = self.adb.pull_file(self.active_serial, apks[0], path)
            self.progress.set(1)
            self.add_log(f"💾 Extraído: {os.path.basename(path)}")
            self.log_activity(f"Extrajo APK: {self.current_app} -> {os.path.basename(path)}")
            time.sleep(1)
            self.progress.set(0)
        threading.Thread(target=task, daemon=True).start()

    def clear_data(self):
        if not self.current_app: return
        if not messagebox.askyesno("Limpiar", "¿Borrar datos de la app?"): return
        threading.Thread(target=lambda: self.adb.clear_app_data(self.active_serial, self.current_app), daemon=True).start()

    def change_output_dir(self):
        path = filedialog.askdirectory(title="Seleccionar carpeta para capturas y videos")
        if path:
            self.history.set_output_dir(path)
            self.add_log(f"📁 Carpeta de salida: {path}")

    def get_valid_output_dir(self):
        out_dir = self.history.get_output_dir()
        if not out_dir or not os.path.exists(out_dir):
            if messagebox.askyesno("Configuración", "Debes seleccionar una carpeta para guardar las capturas. ¿Seleccionar ahora?"):
                self.change_output_dir()
                return self.history.get_output_dir()
            return None
        return out_dir

    def capture_screen(self):
        if not self.active_serial: 
            messagebox.showwarning("Aviso", "Conecta un dispositivo primero.")
            return
        
        out_dir = self.get_valid_output_dir()
        if not out_dir: return

        import datetime
        filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        local_path = os.path.join(out_dir, filename)

        self.set_status("Tomando captura...")
        def task():
            code, out, err = self.adb.take_screenshot(self.active_serial, local_path)
            if code == 0:
                self.add_log(f"📸 Captura guardada: {filename}")
                self.log_activity(f"Tomó captura de pantalla: {filename}")
            else:
                self.add_log(f"❌ Error captura: {err or out}")
            self.set_status("Listo")

        threading.Thread(target=task, daemon=True).start()

    def toggle_recording(self):
        if not self.active_serial:
            messagebox.showwarning("Aviso", "Conecta un dispositivo primero.")
            return

        active = self.active_serial

        if active not in self.recording_processes or self.recording_processes[active] is None:
            # Iniciar grabación
            out_dir = self.get_valid_output_dir()
            if not out_dir: return

            # Verificar si scrcpy existe
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if not os.path.exists(os.path.join(base_dir, "scrcpy", "scrcpy.exe")):
                self.add_log("❌ Error: scrcpy no instalado. Instálalo primero.")
                return

            import datetime
            filename = f"record_{active.replace(':', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mkv"
            recording_local_path = os.path.join(out_dir, filename)

            # Obtener info para decidir sobre el audio
            info = self.adb.get_device_info(active)
            # Android 11 es SDK 30. Scrcpy requiere SDK >= 30 para audio interno.
            sdk_ver = info.get("android_sdk", 0)
            record_audio = sdk_ver >= 30

            self.btn_record.configure(text="⏹ Detener", fg_color=THEME["DANGER"], hover_color=THEME["DANGER_HOVER"])
            msg = f"🎥 Grabando {active} con audio (SDK {sdk_ver})..." if record_audio else f"🎥 Grabando {active} solo video (SDK {sdk_ver} < 30)..."
            self.add_log(msg)
            
            proc = self.adb.start_recording(
                active, 
                recording_local_path, 
                record_audio=record_audio
            )
            
            if not proc:
                self._finalize_recording(active, False, recording_local_path)
                self.add_log(f"❌ Error fatal al lanzar scrcpy en {active}.")
                return
                
            self.recording_processes[active] = (proc, recording_local_path)

            def check_startup():
                time.sleep(2.0)
                if active in self.recording_processes:
                    p, rp = self.recording_processes[active]
                    if p and p.poll() is not None:
                        self.after(0, lambda: self._finalize_recording(active, False, rp))
                        self.after(0, lambda: self.add_log(f"❌ Error: La grabación en {active} se detuvo."))
            
            threading.Thread(target=check_startup, daemon=True).start()
        else:
            # Detener grabación
            self.btn_record.configure(state="disabled", text="Finalizando...")
            def task():
                proc, rp = self.recording_processes[active]
                self.adb.stop_recording(proc)
                time.sleep(1.0) # Esperar a que el archivo se libere
                if hasattr(self, 'log_activity'): self.log_activity(f"Finalizó grabación de video en {active}: {os.path.basename(rp)}")
                self.after(0, lambda: self._finalize_recording(active, True, rp))
            
            threading.Thread(target=task, daemon=True).start()

    def _finalize_recording(self, serial, success, recording_local_path):
        if serial in self.recording_processes:
            del self.recording_processes[serial]
            
        if self.active_serial == serial:
            self.btn_record.configure(
                state="normal",
                text="🎥 Grabar",
                fg_color=THEME["BUTTON_SECONDARY"],
                hover_color=THEME["BUTTON_SECONDARY_HOVER"]
            )
            
        if success and os.path.exists(recording_local_path):
            self.add_log(f"✅ Video guardado [{serial}]: {os.path.basename(recording_local_path)}")
        elif success:
            self.add_log(f"❌ Error en {serial}: No se generó el archivo de video.")

    def launch_scrcpy(self):
        if not self.active_serial:
            messagebox.showwarning("Aviso", "Conecta un dispositivo primero.")
            return

        def task():
            # Obtener info del dispositivo para calcular dimensiones
            info = self.adb.get_device_info(self.active_serial)
            model = info.get("model", "Desconocido")
            
            # Título solicitado: (SCRCPY - AdbAppDroid)
            window_title = "SCRCPY - AdbAppDroid"
            
            # Coordenadas y dimensiones de la ventana principal
            main_x = self.winfo_rootx()
            main_w = self.winfo_width()
            
            # Dimensiones de la pantalla
            screen_h = self.winfo_screenheight()
            
            # Dinámico: El tamaño máximo será el 85% del alto de la pantalla (máx 1024)
            # Esto asegura que la ventana quepa y deje margen arriba/abajo
            max_size = min(1024, int(screen_h * 0.85))
            
            scrcpy_h = max_size 
            
            try:
                screen = info.get("screen", "1080x1920")
                if "x" in screen:
                    w_orig, h_orig = map(int, screen.split("x"))
                    if h_orig < w_orig: # Horizontal
                        scrcpy_h = int(max_size * (h_orig / w_orig))
            except: pass

            # Compensar la barra de título de Windows (aprox 40px) en el centrado vertical
            estimated_total_h = scrcpy_h + 40
            
            # Cálculo de posición: al lado derecho de la interfaz y centrado verticalmente respecto a la PANTALLA
            x = main_x + main_w + 10
            y = (screen_h // 2) - (estimated_total_h // 2)
            
            # Asegurar que el título siempre sea visible (margen de seguridad de 30px)
            y = max(30, y)
            
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            exec_p = os.path.join(base_dir, "scrcpy", "scrcpy.exe")
            
            if os.path.exists(exec_p):
                active = self.active_serial
                proc = self.adb.start_mirroring(
                    active,
                    window_title=f"{window_title} [{active}]",
                    x=x, y=y, max_size=max_size
                )
                if proc:
                    self.scrcpy_processes[active] = proc
                    self.add_log(f"▶ Espejo iniciado para {active}")
                
                # Intentar aplicar el icono de AdbAppDroid a la ventana de scrcpy
                icon_path = os.path.join(base_dir, "assets", "icon.ico")
                self.log_activity(f"Lanzó espejo (Scrcpy) para {model}")
                if os.path.exists(icon_path):
                    self._apply_scrcpy_icon(window_title, icon_path)
            else:
                self.add_log("❌ scrcpy no encontrado. Instálalo primero.")
        
        threading.Thread(target=task, daemon=True).start()

    def _apply_scrcpy_icon(self, title, icon_path):
        """Intenta aplicar el icono del programa a la ventana de scrcpy (Solo Windows)"""
        import ctypes
        import time
        
        def run():
            # Esperar a que la ventana se cree (máximo 5 segundos)
            for _ in range(25):
                hwnd = ctypes.windll.user32.FindWindowW(None, title)
                if hwnd:
                    # Cargar icono (O_ICON=1, LR_LOADFROMFILE=0x10)
                    hicon = ctypes.windll.user32.LoadImageW(0, icon_path, 1, 0, 0, 0x10)
                    if hicon:
                        # WM_SETICON = 0x80
                        ctypes.windll.user32.SendMessageW(hwnd, 0x80, 0, hicon) # Pequeño
                        ctypes.windll.user32.SendMessageW(hwnd, 0x80, 1, hicon) # Grande
                    return
                time.sleep(0.2)
        
        threading.Thread(target=run, daemon=True).start()

    def install_apk(self):
        if not self.active_serial:
            messagebox.showwarning("Aviso", "Conecta un dispositivo primero.")
            return
        
        initial_dir = self.history.get_output_dir()
        path = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("Archivos APK", "*.apk")],
            title="Seleccionar APK para instalar"
        )
        if not path: return

        self.add_log(f"📥 Instalando {os.path.basename(path)}...")
        self.progress.set(0.1)
        
        def task():
            code, out, err = self.adb.install_apk(self.active_serial, path)
            self.progress.set(1)
            if code == 0:
                self.add_log(f"✅ Instalación exitosa: {os.path.basename(path)}")
                self.log_activity(f"Instaló APK: {os.path.basename(path)}")
            else:
                self.add_log(f"❌ Error al instalar: {err or out}")
            time.sleep(1)
            self.progress.set(0)
            
        threading.Thread(target=task, daemon=True).start()

    def save_session_report(self):
        content = self.info_widget.get("1.0", "end-1c")
        if not content.strip():
            messagebox.showinfo("Informe", "No hay información en la sesión actual para guardar.")
            return

        import datetime
        now_dt = datetime.datetime.now()
        timestamp = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        device_info = self.conn_type_label.cget("text")
        
        report = f"========================================\n"
        report += f"   INFORME DE SESIÓN - ADBAppDroid\n"
        report += f"========================================\n"
        report += f"Fecha: {timestamp}\n"
        report += f"Dispositivo: {device_info}\n"
        report += f"----------------------------------------\n\n"
        report += content
        report += f"\n\n----------------------------------------\n"
        report += f"Fin del informe. Generado por QWERTY-ASERTY\n"

        # Sincronización de ruta con ajustes
        initial_dir = self.history.get_output_dir()

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialdir=initial_dir,
            initialfile=f"session_report_{now_dt.strftime('%Y%m%d_%H%M%S')}.txt",
            filetypes=[("Archivos de texto", "*.txt")],
            title="Guardar Informe de Sesión"
        )
        
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(report)
                self.add_log(f"✅ Informe guardado: {os.path.basename(path)}")
                self.log_activity(f"Guardó informe de sesión: {os.path.basename(path)}")
            except Exception as e:
                self.add_log(f"❌ Error al guardar informe: {e}")

    def open_process_monitor(self):
        if not self.active_serial:
            messagebox.showwarning("Aviso", "Conecta un dispositivo primero.")
            return
        
        # Verificar si ya existe y es válido
        if self.process_monitor and self.process_monitor.winfo_exists():
            self.process_monitor.lift()
            self.process_monitor.focus_force()
            return

        # Abrir ventana de monitor
        self.log_activity("Abrió el monitor de procesos")
        self.process_monitor = ProcessMonitorWindow(self, self.adb, self.active_serial)

    def on_closing(self):
        self.running = False
        self.destroy()
    def log_activity(self, message):
        """Registra una acción en el archivo log general en la raíz."""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_line = f"[{timestamp}] {message}\n"
            
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            log_file = os.path.join(base_dir, "activity_log.txt")
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_line)
        except Exception as e:
            print(f"Error logging activity: {e}")

    def open_help(self):
        """Abre el archivo help.html en el navegador predeterminado."""
        import webbrowser
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        help_file = os.path.join(base_dir, "help.html")
        if os.path.exists(help_file):
            webbrowser.open(f"file:///{help_file}")
            self.log_activity("Abrió el sistema de ayuda HTML")
        else:
            messagebox.showerror("Error", "Archivo de ayuda no encontrado.")
