import customtkinter as ctk
import os
import threading
import time
import requests
import py7zr
import subprocess
import shutil
from PIL import Image
import zipfile
import sys
import ctypes

# En lugar de ctk.set_default_color_theme("orange")
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") # El tema base

# --- Constantes de Colores ---
COLOR_NARANJA = "#ED8936" # Un naranja vibrante
COLOR_NARANJA_HOVER = "#DD6B20" # Un poco más oscuro para cuando pasas el ratón
COLOR_VERDE_ACCION = "#2FA572"
COLOR_NARANJA_ACCION = "#D48806"

def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para dev y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Clases de la UI ---

class EmulatorCard(ctk.CTkFrame):
    def __init__(self, master, console_name, emu_name, exe_path, download_url=None, extract_path=None, image_path=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.exe_path = exe_path
        self.download_url = download_url
        self.extract_path = extract_path if extract_path else os.path.dirname(exe_path)

        self.console_name = console_name

        # 0. Imagen de la Consola
        if image_path:
            final_image_path = resource_path(image_path)
            if os.path.exists(final_image_path):
                try:
                    # Cargar imagen. Ajusta size=(ancho, alto) según tus preferencias.
                    pil_image = Image.open(final_image_path)
                    self.console_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(120, 80))
                    
                    self.label_image = ctk.CTkLabel(self, text="", image=self.console_image)
                    self.label_image.pack(pady=(10, 0))
                except Exception as e:
                    print(f"Error cargando imagen para {console_name}: {e}")

        # 1. Nombre de la Consola
        self.label_console = ctk.CTkLabel(self, text=console_name, font=("Arial", 20, "bold"))
        self.label_console.pack(pady=(10, 0))

        # 2. Nombre del Emulador (Paréntesis)
        self.label_emu = ctk.CTkLabel(self, text=f"({emu_name})", font=("Arial", 12, "italic"))
        self.label_emu.pack(pady=(0, 10))

        # 3. Botón Dinámico
        self.btn_action = ctk.CTkButton(
            self, 
            text="Descargar", 
            fg_color=COLOR_NARANJA, 
            hover_color=COLOR_NARANJA_HOVER,
            command=self.handle_click  # <-- ¡ACCIÓN AÑADIDA!
        )
        self.btn_action.pack(pady=10, padx=20)
        
        # Botón Desinstalar (oculto por defecto)
        self.btn_uninstall = ctk.CTkButton(
            self,
            text="DESINSTALAR",
            fg_color="#C53030", # Rojo
            hover_color="#9B2C2C",
            command=self.uninstall_emulator
        )

        # Barra de progreso (oculta por defecto)
        self.progress_bar = ctk.CTkProgressBar(self, width=120, height=10)
        self.progress_bar.set(0)
        
        self.check_status()

    def check_status(self):
        """Revisa si el ejecutable del emulador existe y actualiza el botón."""
        if os.path.exists(self.exe_path):
            self.btn_action.configure(text="EJECUTAR", fg_color=COLOR_NARANJA_ACCION)
            self.btn_uninstall.pack(pady=(0, 10), padx=20)
        else:
            self.btn_action.configure(text="Descargar e Instalar", fg_color=COLOR_VERDE_ACCION)
            self.btn_uninstall.pack_forget()

    def handle_click(self):
        if self.btn_action.cget("text") == "EJECUTAR":
            print(f"Lanzando {self.console_name}...")
            try:
                subprocess.Popen(self.exe_path, cwd=os.path.dirname(self.exe_path))
            except Exception as e:
                print(f"Error al ejecutar {self.console_name}: {e}")
        else:
            self.start_download_thread()

    def uninstall_emulator(self):
        """Elimina la carpeta del emulador."""
        try:
            if os.path.exists(self.extract_path):
                shutil.rmtree(self.extract_path)
                print(f"{self.console_name} desinstalado correctamente.")
                self.check_status()
        except Exception as e:
            print(f"Error al desinstalar {self.console_name}: {e}")

    def start_download_thread(self):
        if not self.download_url:
            print(f"No hay URL configurada para {self.console_name}")
            return

        self.btn_action.configure(state="disabled", text="Descargando...")
        self.progress_bar.pack(pady=(0, 10)) # Mostrar barra
        # Usamos hilos para que la ventana no se congele
        thread = threading.Thread(target=self.download_and_install)
        thread.start()

    def download_and_install(self):
        """Descarga y extrae el emulador usando requests y py7zr."""
        try:
            # 1. Preparar directorio
            if not os.path.exists(self.extract_path):
                os.makedirs(self.extract_path)
            
            # Detectar extensión (exe, zip o 7z)
            url_lower = self.download_url.lower()
            is_exe = ".exe" in url_lower
            is_zip = ".zip" in url_lower



            if is_exe:
                filename = "installer.exe"
            elif is_zip:
                filename = "temp_emu.zip"
            else:
                filename = "temp_emu.7z"
            
            file_path = os.path.join(self.extract_path, filename)

            # 2. Descargar
            response = requests.get(self.download_url, stream=True)
            response.raise_for_status()
            total_length = int(response.headers.get('content-length', 0))
            dl = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    dl += len(chunk)
                    f.write(chunk)
                    if total_length > 0:
                        self.progress_bar.set(dl / total_length)
            
            # 3. Extraer o Instalar
            if is_exe:
                self.btn_action.configure(text="Instalando...")
                # Ejecutar instalador y esperar a que el usuario termine
                subprocess.run([file_path], check=True)
            else:
                self.btn_action.configure(text="Extrayendo...")
                if is_zip:
                    with zipfile.ZipFile(file_path, 'r') as z:
                        z.extractall(self.extract_path)
                else:
                    with py7zr.SevenZipFile(file_path, mode='r') as z:
                        z.extractall(path=self.extract_path)
            
            # 4. Limpiar
            os.remove(file_path)
            self.progress_bar.pack_forget() # Ocultar barra al terminar

            print(f"Instalación de {self.console_name} completada.")
            self.btn_action.configure(state="normal")
            self.check_status()
        
        except Exception as e:
            print(f"Error instalando {self.console_name}: {e}")
            self.btn_action.configure(state="normal", text="Error", fg_color="red")

class MistikLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ID único para que Windows mantenga el icono en la barra de tareas al mover el exe
        try:
            myappid = 'mistik.launcher.portable.v1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        self.title("Mistik Launcher - Portable Edition")
        self.geometry("800x500")

        # Configurar icono de la ventana (asegúrate de tener 'icon.ico' en la carpeta assets)
        try:
            self.iconbitmap(resource_path("assets/icon.ico"))
        except Exception:
            pass # Si no encuentra el icono, usa el predeterminado

        # Título principal
        self.label_title = ctk.CTkLabel(self, text="Bienvenidos al Mistik Launcher ;)", font=("Comic Sans MS", 30, "bold"))
        self.label_title.pack(pady=25)

        # Contenedor de tarjetas (Grid)
        self.cards_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.cards_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Configurar columnas para que se expandan y centren el contenido
        self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # --- Configuración de Emuladores ---
        # Centralizamos los datos para que sea más fácil añadir/quitar emuladores
        emulators_data = [
            {"console": "Wii", "emu": "Dolphin", "path": "emulators/Dolphin/Dolphin-x64/Dolphin.exe", "url": "https://dl.dolphin-emu.org/releases/2509/dolphin-2509-x64.7z", "extract_path": "emulators/Dolphin", "image": "assets/wii.png"},
            {"console": "Wii U", "emu": "Cemu", "path": "emulators/Cemu/Cemu_2.6/Cemu.exe", "extract_path": "emulators/Cemu", "image": "assets/wiiu.png","url": "https://github.com/cemu-project/Cemu/releases/download/v2.6/cemu-2.6-windows-x64.zip"},
            {"console": "3DS", "emu": "Azahar", "path": "emulators/Azahar/azahar-2123.3-windows-msvc/azahar.exe", "extract_path": "emulators/Azahar", "url":"https://github.com/azahar-emu/azahar/releases/download/2123.3/azahar-2123.3-windows-msvc.zip", "image": "assets/3ds.png"},
            {"console": "PS1", "emu": "DuckStation", "path": "emulators/DuckStation/DuckStation.exe","image": "assets/ps1.png"},
            {"console": "PS2", "emu": "PCSX2", "path": "emulators/PCSX2/PCSX2.exe", "image": "assets/ps2.png"},
            {"console": "PSP", "emu": "PPSSPP", "path": "emulators/PPSSPP/PPSSPP.exe", "image": "assets/psp.png"},
        ]

        # --- Creación dinámica de tarjetas ---
        self.cards = []
        cols = 3 # Número de columnas deseadas
        for i, data in enumerate(emulators_data):
            row = i // cols
            col = i % cols
            
            card = EmulatorCard(self.cards_frame, data["console"], data["emu"], data["path"], data.get("url"), extract_path=data.get("extract_path"), image_path=data.get("image"))
            card.grid(row=row, column=col, padx=20, pady=20)
            self.cards.append(card)


if __name__ == "__main__":
    app = MistikLauncher()
    app.mainloop()

#Pasar a .exe con:
# python -m pip install pyinstaller
# python -m PyInstaller --noconfirm --onefile --windowed --name "MistikLauncher" --icon "assets/icon.ico" --add-data "assets;assets" --collect-all customtkinter mistik-launcher-code.py
