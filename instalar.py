#!/usr/bin/env python3
"""
Script de instalación automática de ambos venv.
Ejecutar una sola vez para preparar el proyecto completo.
"""

import subprocess
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

print("="*70)
print("🔧 INSTALACIÓN AUTOMÁTICA DE ENTORNOS")
print("="*70)

# ==================== VENV 3.11.8 ====================
print("\n📦 Instalando venv Principal (Python 3.11.8)...")
print("-" * 70)

venv_3_11 = BASE_DIR / ".venv"

if venv_3_11.exists():
    print("✔ venv 3.11.8 ya existe")
else:
    print("Creando venv 3.11.8...")
    try:
        subprocess.run(
            ["py", "-3.11", "-m", "venv", str(venv_3_11)],
            check=True,
            timeout=60
        )
        print("✔ venv 3.11.8 creado")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

# Instalar dependencias 3.11.8
python_3_11 = venv_3_11 / "Scripts" / "python.exe"
pip_3_11 = venv_3_11 / "Scripts" / "pip.exe"

if python_3_11.exists():
    print("\nInstalando dependencias para venv 3.11.8...")
    try:
        # Actualizar pip
        subprocess.run(
            [str(pip_3_11), "install", "--upgrade", "pip"],
            check=True,
            timeout=120
        )
        
        # Instalar requirements
        reqs_main = BASE_DIR / "requirements.txt"
        if reqs_main.exists():
            subprocess.run(
                [str(pip_3_11), "install", "-r", str(reqs_main)],
                check=True,
                timeout=600
            )
            print("✔ Dependencias instaladas en venv 3.11.8")
        else:
            print(f"⚠️  No encontrado: {reqs_main}")
    except Exception as e:
        print(f"❌ Error instalando dependencias: {e}")
        # No es fatal, continuar

# ==================== VENV DEEPFACE ====================
print("\n🧠 Instalando venv DeepFace (Python 3.10.11)...")
print("-" * 70)

venv_deepface = BASE_DIR / "face" / "deepface_env"

if venv_deepface.exists():
    print("✔ venv DeepFace ya existe")
else:
    print("Creando venv DeepFace (Python 3.10.11)...")
    try:
        subprocess.run(
            ["py", "-3.10", "-m", "venv", str(venv_deepface)],
            check=True,
            timeout=60
        )
        print("✔ venv DeepFace creado")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("⚠️  Verifica que Python 3.10 está instalado")
        sys.exit(1)

# Instalar dependencias DeepFace
python_deepface = venv_deepface / "Scripts" / "python.exe"
pip_deepface = venv_deepface / "Scripts" / "pip.exe"

if python_deepface.exists():
    print("\nInstalando dependencias para venv DeepFace...")
    try:
        # Actualizar pip
        subprocess.run(
            [str(pip_deepface), "install", "--upgrade", "pip"],
            check=True,
            timeout=120
        )
        
        # Instalar requirements deepface
        reqs_deepface = BASE_DIR / "face" / "requirements.txt"
        if reqs_deepface.exists():
            subprocess.run(
                [str(pip_deepface), "install", "-r", str(reqs_deepface)],
                check=True,
                timeout=600
            )
            print("✔ Dependencias instaladas en venv DeepFace")
        
        # Instalar DeepFace si no está
        print("\nInstalando DeepFace...")
        subprocess.run(
            [str(pip_deepface), "install", "deepface"],
            check=True,
            timeout=300
        )
        print("✔ DeepFace instalado")
    
    except Exception as e:
        print(f"❌ Error instalando dependencias: {e}")

# ==================== RESUMEN ====================
print("\n" + "="*70)
print("✅ INSTALACIÓN COMPLETADA")
print("="*70)

print("\n📝 Próximos pasos:")
print("\n1. Verifica que .env tiene credenciales de Supabase:")
print("   SUPABASE_URL=...")
print("   SUPABASE_KEY=...")

print("\n2. Ejecuta el flujo integrado:")
print("   .\\venv\\Scripts\\Activate.ps1")
print("   python main_integrated.py")

print("\n3. Si hay problemas, ejecuta el diagnóstico:")
print("   python diagnostico_venv.py")

print("\n" + "="*70)
print("💡 Documentación:")
print("   - GUIA_EJECUCION_RAPIDA.md → Instrucciones paso a paso")
print("   - INTEGRACION_MULTIPLES_VENV.md → Detalles técnicos")
print("="*70 + "\n")
