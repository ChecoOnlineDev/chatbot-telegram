import shutil
from pathlib import Path

def delete_subfolders_by_name(root_path: str, target_name: str, dry_run: bool = True):
    """
    Busca y elimina todas las subcarpetas con un nombre específico.
    """
    root = Path(root_path)
    
    if not root.exists():
        print(f"❌ La ruta {root_path} no existe.")
        return

    print(f"🔍 Buscando carpetas '{target_name}' en: {root.absolute()}")
    print("⚠️ MODO SIMULACIÓN ACTIVADO" if dry_run else "🚀 EJECUTANDO ELIMINACIÓN REAL")
    print("-" * 50)

    count = 0
    # rglob busca de forma recursiva en todas las subcarpetas
    for folder in root.rglob(target_name):
        if folder.is_dir():
            try:
                if dry_run:
                    print(f"[SIMULACIÓN] Se borraría: {folder}")
                else:
                    # shutil.rmtree borra la carpeta aunque tenga archivos dentro
                    shutil.rmtree(folder)
                    print(f"✅ Borrado: {folder}")
                count += 1
            except Exception as e:
                print(f"❌ Error al borrar {folder}: {e}")

    print("-" * 50)
    if dry_run:
        print(f"Terminado. Se encontraron {count} carpetas para borrar.")
        print("Para borrar realmente, cambia 'dry_run=False' en el script.")
    else:
        print(f"Terminado. Se borraron {count} carpetas con éxito.")

if __name__ == "__main__":
    # --- CONFIGURACIÓN ---
    RUTA_RAIZ = "."            # Carpeta actual o ruta absoluta
    NOMBRE_A_BORRAR = "__pycache__" # Cambia esto por 'node_modules', etc.
    MODO_SIMULACION = False     # Cambia a False para borrar de verdad
    # ---------------------

    delete_subfolders_by_name(RUTA_RAIZ, NOMBRE_A_BORRAR, dry_run=MODO_SIMULACION)