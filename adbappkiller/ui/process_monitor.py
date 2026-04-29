import customtkinter as ctk
import threading
import time
import os
import re
from ..utils.config import THEME

class ProcessMonitorWindow(ctk.CTkToplevel):
    def __init__(self, master, adb_controller, serial):
        super().__init__(master)
        
        self.adb = adb_controller
        self.serial = serial
        self.running = True
        
        self.title("Monitor de Procesos - ADBAppDroid")
        
        # Icono de la ventana
        self.after(200, self._set_icon)

        self.geometry("850x500")
        self.resizable(True, True)
        
        # Forzar que aparezca al frente
        self.attributes("-topmost", True)
        self.after(500, lambda: self.attributes("-topmost", False))
        self.lift()
        self.focus_force()
        
        self.configure(fg_color=THEME["BG"])
        
        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Iniciar hilo de actualización
        self.update_thread = threading.Thread(target=self.refresh_loop, daemon=True)
        self.update_thread.start()

    def _set_icon(self):
        try:
            # Ruta absoluta robusta
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(os.path.dirname(os.path.dirname(curr_dir)), "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

    def setup_ui(self):
        # Contenedor principal de texto
        self.proc_container = ctk.CTkTextbox(self, font=("Courier New", 11), fg_color=THEME["BG"], text_color=THEME["TEXT_MAIN"], border_width=0, corner_radius=8)
        self.proc_container.pack(fill="both", expand=True, padx=15, pady=(15, 5))
        
        # Botón de copiar
        self.btn_copy = ctk.CTkButton(self, text="📋 Copiar al Portapapeles", width=200, height=32, corner_radius=6, fg_color=THEME["BUTTON_SECONDARY"], hover_color=THEME["BUTTON_SECONDARY_HOVER"], text_color=THEME["TEXT_MAIN"], font=("Segoe UI", 11, "bold"), command=self.copy_to_clipboard)
        self.btn_copy.pack(pady=(0, 15))
        
        # Estilos y Tags
        self.proc_container.tag_config("header", foreground=THEME["TEXT_SEC"])
        self.proc_container.tag_config("high_cpu", foreground=THEME["DANGER"])
        self.proc_container.tag_config("system_user", foreground=THEME["TEXT_SEC"])

    def refresh_loop(self):
        while self.running:
            processes = self.adb.get_running_processes(self.serial)
            # Siempre llamar a update_table para mostrar el header aunque no haya procesos
            self.after(0, lambda p=processes: self.update_table(p))
            time.sleep(2)

    def update_table(self, processes):
        if not self.running: return
        
        if not isinstance(processes, list):
            processes = []
            
        # ORDENAMIENTO: Por CPU de mayor a menor
        def get_cpu(p):
            try:
                # Limpiar CPU string (ej: "21.4")
                val = re.sub(r'[^0-9.]', '', str(p.get('cpu', '0')))
                return float(val) if val else 0.0
            except: return 0.0
            
        try:
            processes.sort(key=get_cpu, reverse=True)
        except Exception as e:
            print(f"Error sorting processes: {e}")
            
        try:
            self.proc_container.configure(state="normal")
            self.proc_container.delete("1.0", "end")
            
            # Columnas: PID(8), USER(14), CPU%(8), MEM%(8), NOMBRE
            COL = (8, 14, 8, 8)
            header = ("PID".ljust(COL[0]) + "USUARIO".ljust(COL[1])
                      + "CPU%".ljust(COL[2]) + "MEM%".ljust(COL[3])
                      + "NOMBRE DEL PROCESO\n")
            header += "─" * 90 + "\n"
            self.proc_container.insert("end", header, "header")
            
            if not processes:
                self.proc_container.insert("end", "\n[ No se detectaron procesos activos ]\n", "header")
            else:
                for p in processes:
                    try:
                        pid  = str(p.get('pid', '?')).ljust(COL[0])
                        user = str(p.get('user', '?')).ljust(COL[1])
                        cpu  = str(p.get('cpu', '0')).ljust(COL[2])
                        mem  = str(p.get('mem', '0')).ljust(COL[3])
                        name = str(p.get('name', '???'))
                        
                        line = f"{pid}{user}{cpu}{mem}{name}\n"
                        
                        tag = None
                        try:
                            cpu_clean = re.sub(r'[^0-9.]', '', cpu)
                            if cpu_clean:
                                cpu_val = float(cpu_clean)
                                if cpu_val > 50.0:
                                    tag = "high_cpu"
                        except: pass
                        
                        if not tag and (p.get('user') == "root" or p.get('user') == "system"):
                            tag = "system_user"
                            
                        self.proc_container.insert("end", line, tag)
                    except Exception as e:
                        print(f"Error rendering process line: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error updating process table: {e}")
        finally:
            # Dejar en modo 'disabled' para evitar edición accidental pero permitir selección
            try:
                self.proc_container.configure(state="disabled")
            except: pass

    def copy_to_clipboard(self):
        """Copia todo el contenido del monitor al portapapeles"""
        try:
            content = self.proc_container.get("1.0", "end-1c")
            self.clipboard_clear()
            self.clipboard_append(content)
            self.update() # Requerido por algunos entornos para persistir
            
            # Feedback visual temporal
            old_text = self.btn_copy.cget("text")
            self.btn_copy.configure(text="✅ Copiado", fg_color=THEME["SUCCESS"])
            self.after(2000, lambda: self.btn_copy.configure(text=old_text, fg_color=THEME["BUTTON_SECONDARY"]))
        except Exception:
            pass

    def on_closing(self):
        self.running = False
        self.destroy()
