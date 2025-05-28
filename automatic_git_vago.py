import subprocess
import sys
from importlib import import_module

# Lista de paquetes a verificar/instalar
paquetes = [
    {"nombre": "pyinstaller", "import_name": "PyInstaller"},  
    {"nombre": "tkinterdnd2", "import_name": "tkinterdnd2.TkinterDnD"}  
]

def verificar_instalar_paquetes():
    for paquete in paquetes:
        try:
            # Intenta importar el paquete
            import_module(paquete["import_name"].split('.')[0])  # Solo el módulo base
        except ImportError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", paquete["nombre"]])
            except subprocess.CalledProcessError:
                print(f"❌ Error al instalar {paquete['nombre']}. Verifica conexión o version...")

if __name__ == "__main__":
    verificar_instalar_paquetes()

import tkinter as tk
from tkinter import ttk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import sqlite3
import os
import shutil
import subprocess
from datetime import datetime
def conn():
    ruta_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "automatizacion.db")
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()
    return cursor
def crearInterfaz():
    crear_bd()
    global entrada_hora, tree
    # --- INTERFAZ GRÁFICA ---
    ventana = tk.Tk()
    ventana.title("Seleccionar carpeta con hora")
    ventana.geometry("600x400")

    # Frame para botón y entrada de hora
    frame_controles = tk.Frame(ventana)
    frame_controles.pack(pady=10)

    # Botón para seleccionar CARPETA (ahora dice "Seleccionar carpeta")
    boton_carpeta = tk.Button(
        frame_controles, 
        text="Seleccionar carpeta",  # Cambiado de "archivo" a "carpeta"
        command=seleccionar_carpeta  # Nueva función
    )
    boton_carpeta.pack(side=tk.LEFT, padx=5)

    # Etiqueta y entrada para la hora (igual que antes)
    tk.Label(frame_controles, text="Hora (HH:MM):").pack(side=tk.LEFT, padx=5)
    entrada_hora = tk.Entry(frame_controles, width=10)
    entrada_hora.pack(side=tk.LEFT, padx=5)

    # Treeview (igual que antes, pero muestra carpetas)
    tree = ttk.Treeview(ventana, columns=("id", "nombre", "ruta", "hora"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("nombre", text="Nombre de la carpeta")  # Cambiado para claridad
    tree.heading("ruta", text="Ruta completa")
    tree.heading("hora", text="Hora")
    tree.heading("borrar", text="Borrar")

    # Ajustar anchos de columnas
    tree.column("id", width=50, anchor="center")
    tree.column("nombre", width=150)
    tree.column("ruta", width=250)
    tree.column("hora", width=100, anchor="center")

    # Scrollbar vertical
    scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    tree.pack(expand=True, fill="both", padx=10, pady=5)

    ventana.mainloop()

def crear_bd():
    cursor = conn()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS carpetas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,         
        ruta TEXT NOT NULL,
        hora TIME NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

def seleccionar_carpeta():
    global entrada_hora, tree
    # 1. Verificar si se escribió una hora
    hora = entrada_hora.get().strip()  
    if not hora:
        messagebox.showerror("Error", "Debes escribir una hora (HH o HH:MM)")
        return

    try:
        partes = hora.split(":")
        if len(partes) == 1:
            horas = int(partes[0])
            minutos = 0
        elif len(partes) == 2:
            horas = int(partes[0])
            minutos = int(partes[1])
        else:
            raise ValueError("Demasiados ':'")

        if horas >= 24 or minutos >= 60:
            messagebox.showerror("Error", "Debes escribir una hora válida (HH:MM)")
            return

    except (ValueError, IndexError):
        messagebox.showerror("Error", "Formato incorrecto. Usa HH o HH:MM")
        return

    
    # 2. Abrir diálogo para seleccionar CARPETA (no archivo)
    ruta_carpeta = filedialog.askdirectory(title="Seleccionar carpeta")
    
    if ruta_carpeta:  # Si se seleccionó una carpeta
        nombre_carpeta = ruta_carpeta.split("/")[-1]  # Obtener el nombre de la carpeta
        # 3. Insertar en el Treeview
        hora = f"{horas:02d}:{minutos:02d}"  
        tree.insert("", "end", values=(len(tree.get_children()) + 1, nombre_carpeta, ruta_carpeta, hora))
        entrada_hora.delete(0, tk.END)  # Limpiar el campo de hora
        insertar_archivo(nombre_carpeta,ruta_carpeta,hora)

def insertar_archivo(nombre, ruta,hora):
    c = conn()
    c.execute("INSERT INTO carpetas (nombre, ruta, hora) VALUES (?, ?, ?)", (nombre, ruta, hora))

def mostrar_carpetas():
    c = conn()
    c.execute("SELECT * FROM carpetas")
    data = c.fetchall()
    
    tree.insert("", "first", values=(data.id, data.nombre, data.ruta, data.hora))

crearInterfaz()
