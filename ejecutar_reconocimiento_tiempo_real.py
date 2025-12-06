"""
Ejecutor del reconocimiento facial en tiempo real.
Este script ejecuta el reconocimiento usando el entorno virtual de DeepFace.
"""

import subprocess
from pathlib import Path

# Rutas
BASE_DIR = Path(__file__).parent
FACE_DIR = BASE_DIR / "face"
PYTHON_DEEPFACE = FACE_DIR / "deepface_env" / "Scripts" / "python.exe"
SCRIPT_RECONOCIMIENTO = FACE_DIR / "reconocimiento_tiempo_real.py"

def main():
    print("="*60)
    print("🚀 INICIANDO RECONOCIMIENTO FACIAL EN TIEMPO REAL")
    print("="*60)
    
    # Verificar que existe el Python del venv
    if not PYTHON_DEEPFACE.exists():
        print(f"❌ Error: No se encuentra el Python de DeepFace")
        print(f"   Ruta esperada: {PYTHON_DEEPFACE}")
        print(f"\n💡 Ejecuta primero: python instalar.py")
        return
    
    # Verificar script
    if not SCRIPT_RECONOCIMIENTO.exists():
        print(f"❌ Error: No se encuentra el script de reconocimiento")
        print(f"   Ruta esperada: {SCRIPT_RECONOCIMIENTO}")
        return
    
    print(f"✅ Python DeepFace: {PYTHON_DEEPFACE}")
    print(f"✅ Script: {SCRIPT_RECONOCIMIENTO}")
    print("\n🎬 Ejecutando...\n")
    
    # Ejecutar el script con el Python correcto
    try:
        resultado = subprocess.run(
            [str(PYTHON_DEEPFACE), str(SCRIPT_RECONOCIMIENTO)],
            cwd=str(FACE_DIR)
        )
        
        if resultado.returncode == 0:
            print("\n✅ Reconocimiento finalizado correctamente")
        else:
            print(f"\n⚠️  El script finalizó con código: {resultado.returncode}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por el usuario (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Error ejecutando el reconocimiento: {e}")


if __name__ == "__main__":
    main()
