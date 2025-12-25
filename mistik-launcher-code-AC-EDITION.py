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
from tkinter import messagebox

# En lugar de ctk.set_default_color_theme("orange")
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- Constantes de Colores ---
COLOR_NARANJA = "#ED8936"
COLOR_NARANJA_HOVER = "#DD6B20"
COLOR_VERDE_ACCION = "#2FA572"
COLOR_NARANJA_ACCION = "#D48806"
COLOR_AZUL_SYNC = "#3182CE" # Nuevo color para estado de Sync

def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Clases de la UI ---

class EmulatorCard(ctk.CTkFrame):
    def __init__(self, master, console_name, emu_name, exe_path, download_url=None, extract_path=None, image_path=None, sync_config=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.exe_path = exe_path
        self.download_url = download_url
        self.extract_path = extract_path if extract_path else os.path.dirname(exe_path)
        self.sync_config = sync_config # Configuración de Git (Diccionario)
        self.console_name = console_name

        # 0. Imagen
        if image_path:
            final_image_path = resource_path(image_path)
            if os.path.exists(final_image_path):
                try:
                    pil_image = Image.open(final_image_path)
                    self.console_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(120, 80))
                    self.label_image = ctk.CTkLabel(self, text="", image=self.console_image)
                    self.label_image.pack(pady=(10, 0))
                except Exception as e:
                    print(f"Error cargando imagen para {console_name}: {e}")

        # 1. Etiquetas
        self.label_console = ctk.CTkLabel(self, text=console_name, font=("Arial", 20, "bold"))
        self.label_console.pack(pady=(10, 0))

        self.label_emu = ctk.CTkLabel(self, text=f"({emu_name})", font=("Arial", 12, "italic"))
        self.label_emu.pack(pady=(0, 10))

        # 2. Botón Principal
        self.btn_action = ctk.CTkButton(
            self, 
            text="Descargar", 
            fg_color=COLOR_NARANJA, 
            hover_color=COLOR_NARANJA_HOVER,
            command=self.handle_click
        )
        self.btn_action.pack(pady=10, padx=20)
        
        # 3. Botón Desinstalar
        self.btn_uninstall = ctk.CTkButton(
            self, text="DESINSTALAR", fg_color="#C53030", hover_color="#9B2C2C", command=self.uninstall_emulator
        )

        # 4. Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(self, width=120, height=10)
        self.progress_bar.set(0)
        
        self.check_status()

    def check_status(self):
        """Revisa si el ejecutable existe."""
        if os.path.exists(self.exe_path):
            # Si tiene Sync activado, lo indicamos en el botón
            if self.sync_config:
                self.btn_action.configure(text="☁️ JUGAR (SYNC)", fg_color=COLOR_AZUL_SYNC)
            else:
                self.btn_action.configure(text="EJECUTAR", fg_color=COLOR_NARANJA_ACCION)
            
            self.btn_uninstall.pack(pady=(0, 10), padx=20)
        else:
            self.btn_action.configure(text="Descargar e Instalar", fg_color=COLOR_VERDE_ACCION)
            self.btn_uninstall.pack_forget()

    def handle_click(self):
        text = self.btn_action.cget("text")
        
        if "EJECUTAR" in text or "JUGAR" in text:
            if self.sync_config:
                # Lanzar ciclo de sincronización en un hilo aparte
                threading.Thread(target=self.run_sync_cycle).start()
            else:
                # Ejecución normal
                print(f"Lanzando {self.console_name}...")
                subprocess.Popen(self.exe_path, cwd=os.path.dirname(self.exe_path))
        else:
            self.start_download_thread()

    def run_sync_cycle(self):
        """ Ciclo completo: Pull -> Jugar -> Push """
        save_path = self.sync_config.get("save_path")
        
        # Expandir %AppData% si es necesario
        save_path = os.path.expandvars(save_path)

        if not os.path.exists(save_path):
            print(f"Error: No encuentro la ruta de guardado: {save_path}")
            messagebox.showerror("Error de Sync", f"No se encuentra la carpeta de guardado:\n{save_path}\n\nAsegúrate de haber iniciado el juego al menos una vez.")
            return

        # 1. PULL (Descargar)
        self.btn_action.configure(state="disabled", text="Bajando Nube...", fg_color="#4A5568")
        try:
            subprocess.run(["git", "pull", "origin", "main"], cwd=save_path, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            print("Git Pull exitoso.")
        except Exception as e:
            print(f"Error en Git Pull (puede que sea la primera vez o no haya internet): {e}")
            messagebox.showwarning("Advertencia de Sync", f"No se pudo descargar la última partida de la nube.\n\nEstás jugando con tu partida LOCAL.\nError: {e}")

        # 2. JUGAR (Launch & Wait)
        self.btn_action.configure(text="Jugando...", fg_color=COLOR_NARANJA_ACCION)
        try:
            # Usamos subprocess.run o Popen.wait() para bloquear este hilo hasta que cierres el emulador
            process = subprocess.Popen(self.exe_path, cwd=os.path.dirname(self.exe_path))
            process.wait() # <--- Aquí el programa espera a que cierres Azahar
        except Exception as e:
            print(f"Error ejecutando emulador: {e}")
            messagebox.showerror("Error", f"No se pudo iniciar el emulador:\n{e}")
            self.check_status() # Restaurar botón
            self.btn_action.configure(state="normal")
            return

        # 3. PUSH (Subir)
        self.btn_action.configure(text="Subiendo Nube...", fg_color="#2B6CB0")
        try:
            # Comandos git encadenados
            subprocess.run(["git", "add", "."], cwd=save_path, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(["git", "commit", "-m", f"MistikAutoSave {time.strftime('%Y-%m-%d %H:%M')}"], cwd=save_path, check=False, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(["git", "push", "origin", "main"], cwd=save_path, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            print("Git Push exitoso.")
        except Exception as e:
            print(f"Error subiendo partida: {e}")
            messagebox.showwarning("Error de Nube", f"No se pudo subir la partida a la nube:\n{e}\n\nTu partida local está a salvo, pero no está sincronizada.")

        # Restaurar estado original
        self.check_status()
        self.btn_action.configure(state="normal")

    def uninstall_emulator(self):
        try:
            if os.path.exists(self.extract_path):
                shutil.rmtree(self.extract_path)
                self.check_status()
        except Exception as e:
            print(f"Error al desinstalar: {e}")

    def start_download_thread(self):
        if not self.download_url: return
        self.btn_action.configure(state="disabled", text="Descargando...")
        self.progress_bar.pack(pady=(0, 10))
        threading.Thread(target=self.download_and_install).start()

    def download_and_install(self):
        try:
            if not os.path.exists(self.extract_path):
                os.makedirs(self.extract_path)
            
            url_lower = self.download_url.lower()
            filename = "installer.exe" if ".exe" in url_lower else ("temp.zip" if ".zip" in url_lower else "temp.7z")
            file_path = os.path.join(self.extract_path, filename)

            # Descarga
            response = requests.get(self.download_url, stream=True)
            total_length = int(response.headers.get('content-length', 0))
            dl = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    dl += len(chunk)
                    f.write(chunk)
                    if total_length > 0: self.progress_bar.set(dl / total_length)
            
            # Extracción
            self.btn_action.configure(text="Instalando...")
            if ".exe" in url_lower:
                subprocess.run([file_path], check=True)
            elif ".zip" in url_lower:
                with zipfile.ZipFile(file_path, 'r') as z: z.extractall(self.extract_path)
            else:
                with py7zr.SevenZipFile(file_path, mode='r') as z: z.extractall(path=self.extract_path)
            
            if os.path.exists(file_path): os.remove(file_path)
            
            self.progress_bar.pack_forget()
            self.btn_action.configure(state="normal")
            self.check_status()
        
        except Exception as e:
            print(f"Error: {e}")
            self.btn_action.configure(state="normal", text="Error", fg_color="red")

class MistikLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('mistik.launcher.v2')
        except: pass

        self.title("Mistik Launcher - Cloud Edition")
        self.geometry("900x600")
        try: self.iconbitmap(resource_path("assets/icon.ico"))
        except: pass

        self.label_title = ctk.CTkLabel(self, text="Mistik Launcher", font=("Comic Sans MS", 30, "bold"))
        self.label_title.pack(pady=20)

        self.cards_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.cards_frame.pack(expand=True, fill="both", padx=20, pady=20)
        self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # --- IMPORTANTE: CONFIGURACIÓN DE TUS RUTAS ---
        # Usa %AppData% para que sirva en cualquier PC.
        # Copia aquí la ruta exacta que tenías en la imagen image_4c476d.png
        # pero cambia "C:\Users\Yesu\AppData\Roaming" por "%AppData%"
        
        ruta_guardado_acnl = r"%AppData%\Azahar\sdmc\Nintendo 3DS\00000000000000000000000000000000\00000000000000000000000000000000\title\00040000\00198f00\data\00000001"

        emulators_data = [
            {
                "console": "3DS (Animal Crossing)", 
                "emu": "Azahar", 
                "path": "emulators/Azahar/azahar-2123.3-windows-msvc/azahar.exe", 
                "url": "https://github.com/azahar-emu/azahar/releases/download/2123.3/azahar-2123.3-windows-msvc.zip", 
                "extract_path": "emulators/Azahar", 
                "image": "assets/3ds.png",
                # AQUÍ ESTÁ LA MAGIA DEL SYNC:
                "sync_config": {
                    "save_path": ruta_guardado_acnl
                }
            },
            {"console": "Wii", "emu": "Dolphin", "path": "emulators/Dolphin/Dolphin-x64/Dolphin.exe", "url": "https://dl.dolphin-emu.org/releases/2509/dolphin-2509-x64.7z", "extract_path": "emulators/Dolphin", "image": "assets/wii.png"},
            {"console": "Wii U", "emu": "Cemu", "path": "emulators/Cemu/Cemu_2.6/Cemu.exe", "extract_path": "emulators/Cemu", "image": "assets/wiiu.png","url": "https://github.com/cemu-project/Cemu/releases/download/v2.6/cemu-2.6-windows-x64.zip"},
            {"console": "PS2", "emu": "PCSX2", "path": "emulators/PCSX2/PCSX2.exe", "image": "assets/ps2.png"},
        ]

        self.cards = []
        cols = 3
        for i, data in enumerate(emulators_data):
            row = i // cols
            col = i % cols
            card = EmulatorCard(
                self.cards_frame, 
                data["console"], 
                data["emu"], 
                data["path"], 
                data.get("url"), 
                extract_path=data.get("extract_path"), 
                image_path=data.get("image"),
                sync_config=data.get("sync_config") # Pasamos la config de sync
            )
            card.grid(row=row, column=col, padx=20, pady=20)
            self.cards.append(card)

if __name__ == "__main__":
    app = MistikLauncher()
    app.mainloop()