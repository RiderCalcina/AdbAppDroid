import sys
import os
import logging
import traceback
from adbappkiller.ui.main_window import MainWindow

def setup_logging():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(base_dir, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    log_file = os.path.join(cache_dir, "app.log")
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.critical("Excepción no controlada", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

if __name__ == "__main__":
    setup_logging()
    logging.info("Iniciando AdbAppDroid (v4.5)")
    app = MainWindow()
    app.mainloop()
    logging.info("Aplicación cerrada de forma normal")
