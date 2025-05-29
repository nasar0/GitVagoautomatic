import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import os

def conn():
    ruta_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "automatizacion.db")
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()
    return cursor, conexion

def borrar_item_bd(id):
    c, con = conn()
    try:
        c.execute("DELETE FROM carpetas WHERE id = ?", (id,))
        con.commit()
        messagebox.showinfo("Info", "Se ha borrado correctamente")
        return True        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo borrar: {e}")
        return False
    finally:
        con.close()

def dropItem():
    seleccion = tree.selection()
    for item in seleccion:
        valores = tree.item(item, "values")
        id_bd = valores[0]
        if borrar_item_bd(id_bd):
            tree.delete(item)

def crear_bd():
    c, con = conn()
    c.execute("""
        CREATE TABLE IF NOT EXISTS carpetas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            ruta TEXT NOT NULL UNIQUE,
            hora TIME NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    con.commit()
    con.close()

def mostrar_carpetas():
    tree.delete(*tree.get_children())
    c, con = conn()
    c.execute("SELECT * FROM carpetas")
    data = c.fetchall()
    for fila in data:
        tree.insert("", "end", values=(fila[0], fila[1], fila[2], fila[3]))
    con.close()
    return data

def insertar_archivo(nombre, ruta, hora):
    c, con = conn()
    try:
        c.execute("INSERT INTO carpetas (nombre, ruta, hora) VALUES (?, ?, ?)", (nombre, ruta, hora))
        con.commit()
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "La ruta ya está registrada.")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo insertar: {e}")
        return False
    finally:
        con.close()

def seleccionar_carpeta():
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

    ruta_carpeta = filedialog.askdirectory(title="Seleccionar carpeta")
    if ruta_carpeta:
        if not os.path.isdir(os.path.join(ruta_carpeta, ".git")):
            messagebox.showwarning("Warning", "La carpeta seleccionada no es un repositorio Git (.git no encontrado)")
            return 
        nombre_carpeta = os.path.basename(ruta_carpeta)
        hora_fmt = f"{horas:02d}:{minutos:02d}"
        if insertar_archivo(nombre_carpeta, ruta_carpeta, hora_fmt):
            mostrar_carpetas()

def crearInterfaz():
    global entrada_hora, tree
    crear_bd()
    ventana = tk.Tk()
    ventana.title("Seleccionar carpeta con hora")
    ventana.geometry("600x400")

    frame_controles = tk.Frame(ventana)
    frame_controles.pack(pady=10)

    tk.Label(frame_controles, text="Hora (HH:MM):").pack(side=tk.LEFT, padx=5)
    entrada_hora = tk.Entry(frame_controles, width=10)
    entrada_hora.pack(side=tk.LEFT, padx=5)
    boton_carpeta = tk.Button(frame_controles, text="Seleccionar carpeta", command=seleccionar_carpeta)
    boton_carpeta.pack(side=tk.LEFT, padx=5)

    tree = ttk.Treeview(ventana, columns=("id", "nombre", "ruta", "hora"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("nombre", text="Nombre")
    tree.heading("ruta", text="Ruta completa")
    tree.heading("hora", text="Hora")

    tree.column("id", width=50, anchor="center")
    tree.column("nombre", width=100)
    tree.column("ruta", width=300)
    tree.column("hora", width=60, anchor="center")

    scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(expand=True, fill="both", padx=10, pady=5)

    boton_borrar = tk.Button(ventana, text="Borrar fila seleccionada", command=dropItem)
    boton_borrar.pack(pady=10)

    mostrar_carpetas()
    ventana.mainloop()

if __name__ == "__main__":
    crearInterfaz()
