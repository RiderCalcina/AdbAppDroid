# Configuración y Constantes del Proyecto - Premium Palette 2026

THEME = {
    # 🌙 Gaze Dark Theme — macOS System Palette
    "BG": "#1e1e1e",            # Fondo principal (igual que Gaze dark bg)
    "CARD": "#2C2C2E",          # Superficies elevadas (Gaze sider/card bg)
    "CARD_HOVER": "#3A3A3C",    # Elevación visual al hacer hover
    
    # 📝 Tipografía
    "TEXT_MAIN": "#ffffff",     # Blanco puro (Gaze colorTextBase dark)
    "TEXT_SEC": "#A0A0A0",      # Gris neutro (Gaze header/secondary text)
    
    # 🎨 Acentos y Estados — System Colors (Gaze)
    "ACCENT": "#007AFF",        # System Blue (Gaze colorPrimary)
    "ACCENT_HOVER": "#0062CC",
    "ACCENT_SECONDARY": "#5856D6", # System Purple
    "ACCENT_SECONDARY_HOVER": "#4844C0",
    "SUCCESS": "#34C759",       # System Green (Gaze colorSuccess)
    "DANGER": "#FF3B30",        # System Red (Gaze colorError)
    "DANGER_HOVER": "#CC2F26",
    
    # 🔘 UI Elements
    "BORDER": "#3A3A3C",        # Borde sutil (Gaze colorBorder dark)
    "BUTTON_SECONDARY": "#3A3A3C",
    "BUTTON_SECONDARY_HOVER": "#4A4A4C",
    "WARNING": "#FF9500",       # System Orange (Gaze colorWarning)
    "DANGER_TEXT": "#FF8C8C",   # Rojo suave para texto de peligro
    
    # 📟 Legacy/Compatibilidad
    "FG": "#ffffff",
    "ENTRY_BG": "#2C2C2E",
    "ENTRY_FG": "#ffffff",
    "ACTIVE_APP": "#34C759",    # Mapeado a Success (System Green)
    "DANGER_PERM": "#FF4B2B",   # Rojo intenso para alerta (Gaze System Red)
    "LOG_BG": "#1e1e1e"
}

PELIGROSOS = {
    "ACCESS_COARSE_LOCATION", "ACCESS_FINE_LOCATION", "ACCESS_BACKGROUND_LOCATION",
    "READ_CALENDAR", "WRITE_CALENDAR", "READ_CALL_LOG", "WRITE_CALL_LOG",
    "CAMERA", "READ_CONTACTS", "WRITE_CONTACTS", "GET_ACCOUNTS", "RECORD_AUDIO",
    "READ_PHONE_STATE", "READ_PHONE_NUMBERS", "CALL_PHONE", "ANSWER_PHONE_CALLS",
    "ADD_VOICEMAIL", "USE_SIP", "PROCESS_OUTGOING_CALLS", "READ_SMS", "RECEIVE_SMS",
    "SEND_SMS", "RECEIVE_WAP_PUSH", "RECEIVE_MMS", "READ_EXTERNAL_STORAGE",
    "WRITE_EXTERNAL_STORAGE", "BODY_SENSORS", "ACTIVITY_RECOGNITION",
    "READ_MEDIA_AUDIO", "READ_MEDIA_VIDEO", "READ_MEDIA_IMAGES",
    "ACCESS_MEDIA_LOCATION", "POST_NOTIFICATIONS", "BLUETOOTH_SCAN",
    "BLUETOOTH_ADVERTISE", "BLUETOOTH_CONNECT"
}
