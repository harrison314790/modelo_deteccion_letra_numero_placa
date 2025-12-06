#!/usr/bin/env python3
"""
Script de diagnóstico para verificar ambos venv están correctamente configurados.
Ejecutar desde el venv 3.11.8 principal.
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
VENV_3_11 = BASE_DIR / ".venv"
VENV_DEEPFACE = BASE_DIR / "face" / "deepface_env"

PYTHON_3_11 = VENV_3_11 / "Scripts" / "python.exe"
PYTHON_DEEPFACE = VENV_DEEPFACE / "Scripts" / "python.exe"

print("="*70)
print("🔍 DIAGNÓSTICO DE ENTORNOS PYTHON")
print("="*70)

# ========== VERIFICAR VENV 3.11.8 ==========
print("\n📦 VENV Principal (3.11.8)")
print("-" * 70)

if not VENV_3_11.exists():
    print(f"❌ No existe: {VENV_3_11}")
    print("   Debes crear el venv: py -3.11 -m venv .venv")
else:
    print(f"✔ Encontrado: {VENV_3_11}")
    
    if PYTHON_3_11.exists():
        print(f"✔ Python ejecutable: {PYTHON_3_11}")
        
        # Verificar versión
        try:
            result = subprocess.run(
                [str(PYTHON_3_11), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            print(f"✔ Versión: {result.stdout.strip()}")
        except Exception as e:
            print(f"❌ Error al verificar versión: {e}")
        
        # Verificar librerías críticas
        libros_requeridas = [
            "ultralytics",
            "torch",
            "cv2",
            "easyocr",
            "supabase",
            "dotenv"
        ]
        
        print("\n  Librerías instaladas:")
        for lib in libros_requeridas:
            try:
                result = subprocess.run(
                    [str(PYTHON_3_11), "-c", f"import {lib}; print({lib}.__version__ if hasattr({lib}, '__version__') else 'installed')"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                version = result.stdout.strip() if result.stdout else "installed"
                print(f"    ✔ {lib}: {version}")
            except:
                print(f"    ❌ {lib}: NO INSTALADO")
    else:
        print(f"❌ Python ejecutable no encontrado: {PYTHON_3_11}")

# ========== VERIFICAR VENV DEEPFACE ==========
print("\n" + "="*70)
print("🧠 VENV DeepFace (3.10.11)")
print("-" * 70)

if not VENV_DEEPFACE.exists():
    print(f"❌ No existe: {VENV_DEEPFACE}")
    print("   Debes crear el venv: py -3.10 -m venv face/deepface_env")
else:
    print(f"✔ Encontrado: {VENV_DEEPFACE}")
    
    if PYTHON_DEEPFACE.exists():
        print(f"✔ Python ejecutable: {PYTHON_DEEPFACE}")
        
        # Verificar versión
        try:
            result = subprocess.run(
                [str(PYTHON_DEEPFACE), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            print(f"✔ Versión: {result.stdout.strip()}")
        except Exception as e:
            print(f"❌ Error al verificar versión: {e}")
        
        # Verificar librerías críticas
        libros_requeridas = ["deepface", "tensorflow", "cv2", "dotenv"]
        
        print("\n  Librerías instaladas:")
        for lib in libros_requeridas:
            try:
                result = subprocess.run(
                    [str(PYTHON_DEEPFACE), "-c", f"import {lib}; print({lib}.__version__ if hasattr({lib}, '__version__') else 'installed')"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                version = result.stdout.strip() if result.stdout else "installed"
                print(f"    ✔ {lib}: {version}")
            except:
                print(f"    ❌ {lib}: NO INSTALADO")
    else:
        print(f"❌ Python ejecutable no encontrado: {PYTHON_DEEPFACE}")

# ========== VERIFICAR ARCHIVOS CLAVE ==========
print("\n" + "="*70)
print("📁 ARCHIVOS CLAVE")
print("-" * 70)

archivos_verificar = [
    BASE_DIR / "main_integrated.py",
    BASE_DIR / "placas" / "prueba_yolo.py",
    BASE_DIR / "placas" / "prueba_numero_letra.py",
    BASE_DIR / "face" / "reconocimientoFacial.py",
    BASE_DIR / "servicios" / "peticiones_supaBase.py",
    BASE_DIR / ".env",
]

for archivo in archivos_verificar:
    if archivo.exists():
        print(f"✔ {archivo.relative_to(BASE_DIR)}")
    else:
        print(f"❌ FALTA: {archivo.relative_to(BASE_DIR)}")

# ========== RESUMEN ==========
print("\n" + "="*70)
print("📊 RESUMEN")
print("-" * 70)

venv_3_11_ok = PYTHON_3_11.exists()
venv_deepface_ok = PYTHON_DEEPFACE.exists()

if venv_3_11_ok and venv_deepface_ok:
    print("✅ AMBOS ENTORNOS DETECTADOS CORRECTAMENTE")
    print("\nPuedes ejecutar:")
    print("  .\.venv\Scripts\Activate.ps1")
    print("  python main_integrated.py")
elif venv_3_11_ok:
    print("⚠️  FALTA: venv DeepFace (3.10.11)")
    print("   Crea con: py -3.10 -m venv face/deepface_env")
elif venv_deepface_ok:
    print("⚠️  FALTA: venv Principal (3.11.8)")
    print("   Crea con: py -3.11 -m venv .venv")
else:
    print("❌ FALTAN AMBOS ENTORNOS")
    print("   Debes crear ambos venv")

print("\n" + "="*70)
