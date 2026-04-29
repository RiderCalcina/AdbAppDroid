import json
import os

class HistoryManager:
    def __init__(self, filename="history.json"):
        # Guardar el archivo en la carpeta del aplicativo
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.filepath = os.path.join(self.base_path, filename)
        self.history = self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    data = json.load(f)
                    # Migración: Asegurar campos nuevos
                    if "output_dir" not in data: data["output_dir"] = None
                    return data
            except Exception:
                return {"last": None, "devices": [], "output_dir": None}
        return {"last": None, "devices": [], "output_dir": None}

    def save(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.history, f, indent=4)
        except Exception as e:
            print(f"Error saving history: {e}")

    def add_device(self, ip, port):
        device = f"{ip}:{port}"
        if device not in self.history["devices"]:
            # Insertar al inicio para que el más reciente salga primero
            self.history["devices"].insert(0, device)
            # Limitar a los últimos 10 dispositivos
            self.history["devices"] = self.history["devices"][:10]
        
        self.history["last"] = device
        self.save()

    def clear_history(self):
        self.history = {"last": None, "devices": []}
        self.save()

    def get_devices(self):
        return self.history["devices"]

    def get_last(self):
        return self.history["last"]

    def get_output_dir(self):
        return self.history.get("output_dir")

    def set_output_dir(self, path):
        self.history["output_dir"] = path
        self.save()
