# Guía de Migración a otra PC

ADBAppKiller es una herramienta diseñada para ser altamente portable. Sigue estos pasos para mover el proyecto completo de una computadora a otra sin perder configuraciones ni herramientas.

## 📦 Método 1: Copia Completa (Recomendado)

Debido a que ADBAppKiller descarga sus dependencias binarias (`adb` y `scrcpy`) en su propio directorio, la forma más sencilla de migrar es:

1. **Comprimir la carpeta**: Comprime toda la carpeta `adbappkiller3.1` en un archivo `.zip` o `.rar`.
2. **Transferir**: Mueve el archivo comprimido a la nueva PC mediante una memoria USB, red local o nube.
3. **Descomprimir**: Extrae el contenido en la nueva PC.
4. **Instalar Python**: Asegúrate de que la nueva PC tenga Python instalado y configurado en el PATH.
5. **Ejecutar**: Ejecuta `main.py`. Todo debería funcionar inmediatamente ya que los binarios ya están incluidos.

## 🛠 Método 2: Instalación Limpia

Si prefieres no copiar los binarios pesados (`adb` y `scrcpy` ocupan ~100MB+):

1. Copia únicamente los archivos de código fuente:
   - Directorio `adbappkiller/`
   - `main.py`
   - `aak.ico`
2. En la nueva PC, ejecuta `main.py`.
3. Utiliza los botones de **Instalación Automática** que aparecerán en la interfaz para descargar `adb` y `scrcpy` específicamente para esa máquina.

## ⚠️ Consideraciones de Seguridad y Drivers

Al cambiar de PC, ten en cuenta lo siguiente:
- **Drivers OEM**: Es posible que la nueva PC necesite los drivers específicos del fabricante del teléfono (Samsung, Xiaomi, Huawei, etc.) para que ADB reconozca el dispositivo.
- **Autorización RSA**: El teléfono detectará una nueva PC y pedirá nuevamente confirmación para permitir la depuración USB. Deberás aceptar la huella digital de la nueva computadora en la pantalla del dispositivo.

## 🗃 Estructura Mínima para Migrar
Para que el proyecto funcione, debes asegurar la presencia de:
```text
adbappkiller3.1/
├── adbappkiller/       <-- Lógica interna
├── main.py         <-- Punto de entrada
└── aak.ico             <-- Icono de la app
```

---

> [!IMPORTANT]
> No es necesario copiar las carpetas `__pycache__`, ya que Python las regenerará automáticamente.
