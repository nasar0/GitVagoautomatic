import subprocess
import sys
from importlib import import_module

paquetes = [
    {"nombre": "pyinstaller", "import_name": "PyInstaller"},
    {"nombre": "python-crontab", "import_name": "crontab"},
    {"nombre": "ttkbootstrap", "import_name": "ttkbootstrap"}
]

def verificar_instalar_paquetes():
    for paquete in paquetes:
        try:
            import_module(paquete["import_name"].split('.')[0])
        except ImportError:
            try:
                print(f"Instalando paquete: {paquete['nombre']}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", paquete["nombre"]])
            except subprocess.CalledProcessError as e:
                print(f"❌ Error al instalar {paquete['nombre']}: {e}. Sigue adelante si no es crítico.")

if __name__ == "__main__":
    verificar_instalar_paquetes()

    
from automatic_git_vago import crearInterfaz,crearCrontab
crearCrontab()
crearInterfaz()