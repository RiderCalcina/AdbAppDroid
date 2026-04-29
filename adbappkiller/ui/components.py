import customtkinter as ctk
from ..utils.config import THEME
from PIL import Image
import os
import threading

class AppInfoWidget(ctk.CTkTextbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            font=("Segoe UI", 12),
            fg_color=THEME["CARD"],
            text_color=THEME["TEXT_MAIN"],
            border_width=0
        )
        self.tag_config("danger", foreground=THEME["DANGER_PERM"])
        self.tag_config("bold", foreground=THEME["TEXT_MAIN"])
        self.tag_config("log", foreground=THEME["ACCENT"])
        self.tag_config("granted", foreground=THEME["SUCCESS"])
        self.tag_config("inactive", foreground=THEME["TEXT_SEC"])
        self.configure(state="disabled")

    def log(self, message, tag=None):
        self.configure(state="normal")
        self.insert("end", f"{message}\n", tag)
        self.see("end")
        self.configure(state="disabled")

    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")

    def scroll_to_top(self):
        self.see("1.0")

class CTKToolTip:
    """Implementación mejorada de ToolTip para CustomTkinter"""
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.id = None
        
        self.widget.bind("<Enter>", self.schedule_show)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.widget.bind("<ButtonPress>", self.hide_tooltip)

    def schedule_show(self, event=None):
        self.id = self.widget.after(self.delay, self.show_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        
        # Calcular posición debajo del widget
        x = self.widget.winfo_rootx() + (self.widget.winfo_width() // 2) - 50
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        import tkinter as tk
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        
        # Usar un Frame para el borde, ya que CTkLabel no soporta border_width en algunas versiones
        frame = ctk.CTkFrame(tw, fg_color=THEME["CARD"], border_width=1, border_color=THEME["BORDER"], corner_radius=8)
        frame.pack()

        label = ctk.CTkLabel(frame, text=self.text, padx=8, pady=4,
                             fg_color="transparent", text_color=THEME["TEXT_MAIN"],
                             font=("Segoe UI", 10))
        label.pack()

    def hide_tooltip(self, event=None):
        # Cancelar el timer si el ratón salió antes de que se mostrara
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
            
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class RSSFeedWidget(ctk.CTkFrame):
    def __init__(self, master, feed_url=None, **kwargs):
        super().__init__(master, **kwargs)
        self.feed_url = feed_url
        self.configure(fg_color=THEME["CARD"], border_width=1, border_color=THEME["BORDER"], corner_radius=12)
        
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.pack(pady=(5, 2))
        
        self.title_label = ctk.CTkLabel(self.title_frame, text="📰 FEED RSS  ", font=("Segoe UI", 10, "bold"), text_color=THEME["TEXT_SEC"])
        self.title_label.pack(side="left")
        
        self.title_link = ctk.CTkLabel(self.title_frame, text="QwertyAserty.com", font=("Segoe UI", 10, "bold"), text_color=THEME["TEXT_MAIN"], cursor="hand2")
        self.title_link.pack(side="left")
        self.title_link.bind("<Button-1>", lambda e: __import__('webbrowser').open("https://qwertyaserty.com/"))
        
        self.textbox = ctk.CTkTextbox(self, font=("Segoe UI", 11), fg_color=THEME["BG"], text_color=THEME["TEXT_MAIN"], border_width=0, corner_radius=8)
        self.textbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.textbox.configure(state="disabled")
        
        self.textbox.tag_config("title", foreground=THEME["TEXT_MAIN"])
        self.textbox.tag_config("link", foreground=THEME["TEXT_SEC"], underline=False)
        
        # Vincular clic en link
        self.textbox.tag_bind("link", "<Button-1>", self._on_link_click)
        self.textbox.tag_bind("link", "<Enter>", lambda e: self.textbox.configure(cursor="hand2"))
        self.textbox.tag_bind("link", "<Leave>", lambda e: self.textbox.configure(cursor=""))

        if self.feed_url:
            self.refresh_feed()

    def _on_link_click(self, event):
        import webbrowser
        # Obtener el texto bajo el clic
        index = self.textbox.index(f"@{event.x},{event.y}")
        line_start = self.textbox.index(f"{index} linestart")
        line_end = self.textbox.index(f"{index} lineend")
        raw_text = self.textbox.get(line_start, line_end).strip()
        
        if raw_text.startswith("http"):
            webbrowser.open(raw_text)

    def refresh_feed(self):
        import threading
        threading.Thread(target=self._fetch_feed, daemon=True).start()

    def _fetch_feed(self):
        import feedparser
        import requests
        
        try:
            response = requests.get(self.feed_url, timeout=10)
            feed = feedparser.parse(response.content)
            
            if feed.bozo: # Error de parseo (formato inválido)
                self.after(0, lambda: self._show_error("Formato de feed inválido."))
            else:
                self.after(0, lambda: self._update_ui(feed.entries))
        except requests.exceptions.ConnectionError:
            self.after(0, lambda: self._show_error("Parece que estás offline. Revisa tu conexión a internet para ver las noticias."))
        except requests.exceptions.Timeout:
            self.after(0, lambda: self._show_error("La conexión tardó demasiado. Reintentando..."))
        except Exception as e:
            self.after(0, lambda: self._show_error(f"Error inesperado: {str(e)}"))

    def _update_ui(self, entries):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        
        if not entries:
            self.textbox.insert("end", "No hay noticias nuevas en este momento.\n\nVuelve más tarde.")
        else:
            for entry in entries[:15]: # Limitar a 15 entradas
                title = entry.get("title", "Sin título").upper()
                link = entry.get("link", "")
                
                self.textbox.insert("end", f"• {title}\n", "title")
                if link:
                    self.textbox.insert("end", f"  {link}\n\n", "link")
                else:
                    self.textbox.insert("end", "\n")
        
        self.textbox.configure(state="disabled")

    def _show_error(self, error_msg):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("end", f"\n📡 ESTADO DEL FEED:\n\n", "title")
        self.textbox.insert("end", f"{error_msg}\n\n", "link")
        self.textbox.insert("end", "Haga clic aquí para reintentar", "retry")
        
        # Tag para reintentar
        self.textbox.tag_config("retry", foreground="#888", underline=True)
        self.textbox.tag_bind("retry", "<Button-1>", lambda e: self.refresh_feed())
        self.textbox.tag_bind("retry", "<Enter>", lambda e: self.textbox.configure(cursor="hand2"))
        self.textbox.tag_bind("retry", "<Leave>", lambda e: self.textbox.configure(cursor=""))
        
        self.textbox.configure(state="disabled")

class RSSMarqueeWidget(ctk.CTkFrame):
    def __init__(self, master, feed_url=None, **kwargs):
        super().__init__(master, **kwargs)
        self.feed_url = feed_url
        self.configure(fg_color=THEME["CARD"], height=35, corner_radius=8, border_width=1, border_color=THEME["BORDER"])
        
        self.marquee_text = "Cargando noticias destacadas..."
        self.label = ctk.CTkLabel(self, text=self.marquee_text, font=("Segoe UI", 11, "bold"), 
                                 text_color="#D1D5DB", cursor="hand2")
        self.label.place(x=300, y=5)
        
        # Vincular clic para abrir web
        self.label.bind("<Button-1>", lambda e: __import__('webbrowser').open("https://qwertyaserty.com/"))
        self.bind("<Button-1>", lambda e: __import__('webbrowser').open("https://qwertyaserty.com/"))
        
        self.pos_x = 0
        self.running = True
        
        if self.feed_url:
            self.refresh_queue()
        
        self._scroll()

    def refresh_queue(self):
        def task():
            import feedparser
            import requests
            import urllib.request
            import io
            
            content = None
            # Intento 1: Requests (silenciando warnings de versiones)
            try:
                import warnings
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=UserWarning)
                    response = requests.get(self.feed_url, timeout=8, verify=False)
                    if response.status_code == 200:
                        content = response.content
            except: pass
            
            # Intento 2: Urllib (Fallback robusto si requests falla por SSL/Certificados)
            if not content:
                try:
                    import ssl
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    with urllib.request.urlopen(self.feed_url, timeout=8, context=ctx) as r:
                         content = r.read()
                except: pass
            
            if content:
                try:
                    feed = feedparser.parse(content)
                    all_entries = feed.entries
                    
                    if not all_entries:
                        self.marquee_text = "No hay noticias nuevas disponibles.      "
                    else:
                        items = []
                        # 1. El último post absoluto (siempre primero como novedad)
                        first_title = all_entries[0].title
                        clean_first = first_title.replace("[DESTACADO]", "").replace("[destacado]", "").replace("⭐", "").strip()
                        items.append(f"ÚLTIMO POST: {clean_first}")
                        
                        # 2. Todos los destacados (sin excepciones, para garantizar persistencia)
                        # Buscamos en los primeros 20 para asegurar que si hay destacados "viejos" sigan saliendo
                        destacados = [e.title for e in all_entries[:20] if "[DESTACADO]" in e.title.upper()]
                        for d in destacados:
                            if d not in items: # Evitar duplicar exactamente el mismo string
                                items.append(d)
                        
                        # 3. Rellenar con los más recientes para variedad
                        for e in all_entries[1:10]: 
                            if len(items) >= 6: break
                            if e.title not in items and e.title != first_title:
                                items.append(e.title)
                        
                        # Unir con separadores y repetir para asegurar un bucle fluido
                        base_text = " ★ " + "  |  ★ ".join(items) + "      "
                        self.marquee_text = base_text * 3
                    
                    self.after(0, lambda: self.label.configure(text=self.marquee_text))
                except Exception as e:
                    self.after(0, lambda: self.label.configure(text=f"Error al procesar noticias.      "))
            else:
                self.after(0, lambda: self.label.configure(text="Error de conexión al feed RSS.      "))
        
        threading.Thread(target=task, daemon=True).start()

    def _scroll(self):
        if not self.running: return
        w = self.winfo_width()
        if w < 10: w = 350 # Fallback inicial
        
        self.pos_x -= 1 # Velocidad más lenta y elegante
        
        # Obtener el ancho real del texto del label
        try:
            text_width = self.label.winfo_reqwidth()
        except:
            # Fallback aproximado si no se puede medir
            text_width = len(self.marquee_text) * 8
            
        # Lógica de bucle continuo (seamless)
        # Si el texto es largo (gracias a las repeticiones), reseteamos a 0 permitiendo fluidez
        if text_width > w:
            # Si hemos desplazado un tercio del texto total (una iteración completa)
            if self.pos_x < -(text_width / 3):
                self.pos_x = 0
        else:
            # Fallback estándar si por alguna razón el texto es muy corto
            if self.pos_x < -text_width:
                self.pos_x = w
        
        self.label.place(x=self.pos_x, y=5)
        self.after(30, self._scroll)

class CPUGraphWidget(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=THEME["CARD"], border_width=1, border_color=THEME["BORDER"], corner_radius=12)
        
        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent", height=30)
        self.header.pack(fill="x", padx=10, pady=(5, 0))
        
        ctk.CTkLabel(self.header, text="📊 RENDIMIENTO CPU", font=("Segoe UI", 10, "bold"), text_color=THEME["TEXT_SEC"]).pack(side="left")
        self.val_label = ctk.CTkLabel(self.header, text="0%", font=("Segoe UI", 12, "bold"), text_color=THEME["ACCENT"])
        self.val_label.pack(side="right")
        
        # Canvas para el gráfico
        self.canvas = ctk.CTkCanvas(self, bg=THEME["BG"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=8)
        
        self.history = [0] * 50 # 50 puntos
        self.max_history = 50
        self.update_id = None
        
        self.bind("<Configure>", lambda e: self.draw())

    def update_value(self, value):
        self.history.pop(0)
        self.history.append(value)
        self.val_label.configure(text=f"{value}%")
        self.draw()

    def draw(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10: return
        
        self.canvas.delete("all")
        
        # Dibujar Cuadrícula
        grid_color = "#1F1F1F"
        # Líneas horizontales (cada 25%)
        for i in range(1, 4):
            y = h - (h * i / 4)
            self.canvas.create_line(0, y, w, y, fill=grid_color, dash=(2, 4))
            
        # Líneas verticales
        for i in range(1, 6):
            x = w * i / 6
            self.canvas.create_line(x, 0, x, h, fill=grid_color, dash=(2, 4))

        # Dibujar Gráfico (Línea)
        points = []
        step = w / (self.max_history - 1)
        
        for i, val in enumerate(self.history):
            x = i * step
            # Normalizar val (0-100) al alto del canvas (invertido)
            y = h - (val / 100 * (h - 10)) - 5
            points.append(x)
            points.append(y)
            
        if len(points) >= 4:
            # Línea de degradado (Área sombreada)
            poly_points = [0, h] + points + [w, h]
            self.canvas.create_polygon(poly_points, fill="#E50914", stipple="gray25", outline="")
            
            # Línea principal
            self.canvas.create_line(points, fill=THEME["ACCENT"], width=2, smooth=True)
            
            # Punto actual
            self.canvas.create_oval(w-5, points[-1]-3, w+1, points[-1]+3, fill=THEME["ACCENT"], outline="white")

class CTkWarningDialog(ctk.CTkToplevel):
    def __init__(self, master, title, message, yes_text="Sí", no_text="No", **kwargs):
        super().__init__(master, **kwargs)
        self.title(title)
        
        self.transient(master) # Make it a transient window of master
        
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            icon_path = os.path.join(base_dir, "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.after(200, lambda: self.iconbitmap(icon_path))
        except Exception:
            pass

        self.geometry("450x250")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.grab_set()
        
        self.result = False
        
        self.update_idletasks()
        if master.winfo_viewable():
            x = master.winfo_x() + (master.winfo_width() // 2) - 225
            y = master.winfo_y() + (master.winfo_height() // 2) - 125
            self.geometry(f"+{x}+{y}")
            
        self.configure(fg_color=THEME["BG"])
        
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        self.icon_label = ctk.CTkLabel(self.main_frame, text="⚠️", font=("Segoe UI", 48), text_color=THEME["WARNING"])
        self.icon_label.grid(row=0, column=0, padx=(0, 15), sticky="nw")
        
        self.msg_label = ctk.CTkLabel(
            self.main_frame, text=message, font=("Segoe UI", 12), text_color=THEME["TEXT_MAIN"], 
            justify="left", wraplength=320
        )
        self.msg_label.grid(row=0, column=1, sticky="nw", pady=(10, 0))
        
        self.btn_frame = ctk.CTkFrame(self, fg_color=THEME["CARD"], height=60, corner_radius=0)
        self.btn_frame.pack(fill="x", side="bottom")
        self.btn_frame.pack_propagate(False)
        
        self.btn_no = ctk.CTkButton(self.btn_frame, text=no_text, fg_color=THEME["BUTTON_SECONDARY"], hover_color=THEME["BUTTON_SECONDARY_HOVER"], text_color=THEME["TEXT_MAIN"], command=self.on_no, width=100, font=("Segoe UI", 12, "bold"), corner_radius=8)
        self.btn_no.pack(side="right", padx=15, pady=15)
        
        self.btn_yes = ctk.CTkButton(self.btn_frame, text=yes_text, fg_color=THEME["DANGER"], hover_color=THEME["DANGER_HOVER"], text_color="#FFFFFF", command=self.on_yes, width=100, font=("Segoe UI", 12, "bold"), corner_radius=8, border_width=1, border_color="#DC2626")
        self.btn_yes.pack(side="right", padx=10, pady=15)
        
        self.protocol("WM_DELETE_WINDOW", self.on_no)

    def on_yes(self):
        self.result = True
        self.grab_release()
        self.destroy()
        
    def on_no(self):
        self.result = False
        self.grab_release()
        self.destroy()

    def get_result(self):
        self.wait_window(self)
        return self.result

