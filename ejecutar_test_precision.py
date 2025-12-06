"""
Ejecutor del script de prueba de precisión facial.
Usa el entorno virtual de DeepFace.
"""

import subprocess
from pathlib import Path

# Rutas
BASE_DIR = Path(__file__).parent
FACE_DIR = BASE_DIR / "face"
PYTHON_DEEPFACE = FACE_DIR / "deepface_env" / "Scripts" / "python.exe"
SCRIPT_TEST = BASE_DIR / "test_precision_facial.py"

def main():
    print("="*70)
    print("🚀 EJECUTANDO PRUEBAS DE PRECISIÓN FACIAL")
    print("="*70)
    
    # Verificar que existe el Python del venv
    if not PYTHON_DEEPFACE.exists():
        print(f"❌ Error: No se encuentra el Python de DeepFace")
        print(f"   Ruta esperada: {PYTHON_DEEPFACE}")
        print(f"\n💡 Ejecuta primero: python instalar.py")
        return
    
    # Verificar script
    if not SCRIPT_TEST.exists():
        print(f"❌ Error: No se encuentra el script de prueba")
        print(f"   Ruta esperada: {SCRIPT_TEST}")
        return
    
    print(f"✅ Python DeepFace: {PYTHON_DEEPFACE}")
    print(f"✅ Script: {SCRIPT_TEST}")
    print("\n🎬 Ejecutando...\n")
    
    # Ejecutar el script con el Python correcto
    try:
        resultado = subprocess.run(
            [str(PYTHON_DEEPFACE), str(SCRIPT_TEST)],
            cwd=str(BASE_DIR)
        )
        
        if resultado.returncode == 0:
            print("\n✅ Pruebas finalizadas correctamente")
        else:
            print(f"\n⚠️  El script finalizó con código: {resultado.returncode}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por el usuario (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Error ejecutando las pruebas: {e}")


if __name__ == "__main__":
    main()
