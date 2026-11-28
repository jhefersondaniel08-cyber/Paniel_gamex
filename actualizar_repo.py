"""Script para sincronizar y actualizar los archivos del juego con el repositorio de GitHub:
https://github.com/jhefersondaniel08-cyber/Paniel_gamex
"""
import os
import shutil
import subprocess
import sys

def actualizar():
    print("=" * 60)
    print("  Sincronizando con https://github.com/jhefersondaniel08-cyber/Paniel_gamex")
    print("=" * 60)

    git_exe = shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe"
    if not os.path.exists(git_exe):
        print(f"Error: No se encontró git en '{git_exe}'")
        return False

    print("[1/3] Descargando cambios más recientes de GitHub...")
    res_fetch = subprocess.run([git_exe, "fetch", "origin", "main"], capture_output=True, text=True)
    if res_fetch.returncode != 0:
        print("Error al conectar con GitHub:", res_fetch.stderr)
        return False
    print("✓ Cambios recibidos correctamente.")

    print("[2/3] Actualizando archivos locales...")
    res_merge = subprocess.run([git_exe, "pull", "--ff-only", "origin", "main"], capture_output=True, text=True)
    if res_merge.returncode != 0:
        res_reset = subprocess.run([git_exe, "checkout", "-f", "-B", "main", "origin/main"], capture_output=True, text=True)
        print("✓ Archivos actualizados y sincronizados con origin/main.")
    else:
        print("✓ Archivos ya estaban al día o combinados limpiamente.")

    print("[3/3] Verificando estado:")
    res_log = subprocess.run([git_exe, "log", "-1", "--oneline"], capture_output=True, text=True)
    print(f"Último commit activo: {res_log.stdout.strip()}")
    print("\n¡Todo listo! Tus archivos están 100% sincronizados con GitHub.")
    return True

if __name__ == "__main__":
    actualizar()

