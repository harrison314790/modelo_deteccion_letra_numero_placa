#!/usr/bin/env python3
"""
📋 CHECKLIST - Verifica que todo está listo
Ejecuta este script antes de iniciar el sistema
"""

import os
import sys
from pathlib import Path
from colorama import init, Fore, Style

# Para colores en Windows
try:
    init(autoreset=True)
    HAS_COLOR = True
except:
    HAS_COLOR = False

BASE_DIR = Path(__file__).parent

def check(condicion, mensaje_ok, mensaje_fallo):
    """Mostrar estado de verificación."""
    if HAS_COLOR:
        if condicion:
            print(f"{Fore.GREEN}✅ {mensaje_ok}")
        else:
            print(f"{Fore.RED}❌ {mensaje_fallo}")
    else:
        print(f"{'✓' if condicion else '✗'} {mensaje_ok if condicion else mensaje_fallo}")
    
    return condicion

def main():
    print("\n" + "="*70)
    print("📋 CHECKLIST - VERIFICACIÓN DE CONFIGURACIÓN")
    print("="*70 + "\n")
    
    puntuacion = 0
    total = 0
    
    # ==================== PYTHON VERSIONS ====================
    print("🐍 PYTHON VERSIONS")
    print("-" * 70)
    
    # Python 3.11
    total += 1
    try:
        import subprocess
        resultado = subprocess.run(
            ["py", "-3.11", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "3.11" in resultado.stdout or "3.11" in resultado.stderr:
            if check(True, "Python 3.11.x detectado", ""):
                puntuacion += 1
        else:
            check(False, "", "Python 3.11.x no detectado")
    except:
        check(False, "", "Python 3.11.x no detectado")
    
    # Python 3.10
    total += 1
    try:
        resultado = subprocess.run(
            ["py", "-3.10", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "3.10" in resultado.stdout or "3.10" in resultado.stderr:
            if check(True, "Python 3.10.x detectado", ""):
                puntuacion += 1
        else:
            check(False, "", "Python 3.10.x no detectado")
    except:
        check(False, "", "Python 3.10.x no detectado")
    
    # ==================== VIRTUAL ENVIRONMENTS ====================
    print("\n📦 ENTORNOS VIRTUALES")
    print("-" * 70)
    
    # venv 3.11.8
    total += 1
    venv_3_11 = BASE_DIR / ".venv"
    python_3_11 = venv_3_11 / "Scripts" / "python.exe"
    
    if check(venv_3_11.exists(), 
             "Venv 3.11.8 existe (.venv)", 
             "Venv 3.11.8 NO existe"):
        puntuacion += 1
    
    # deepface_env
    total += 1
    venv_deepface = BASE_DIR / "face" / "deepface_env"
    python_deepface = venv_deepface / "Scripts" / "python.exe"
    
    if check(venv_deepface.exists(), 
             "Venv DeepFace existe (face/deepface_env)", 
             "Venv DeepFace NO existe"):
        puntuacion += 1
    
    # ==================== ARCHIVOS CLAVE ====================
    print("\n📁 ARCHIVOS CLAVE")
    print("-" * 70)
    
    archivos_requeridos = {
        "main_integrated.py": "Flujo integrado",
        ".env": "Credenciales Supabase",
        "requirements.txt": "Dependencias (raíz)",
        "face/requirements.txt": "Dependencias DeepFace",
        "placas/prueba_yolo.py": "Detección YOLO",
        "placas/prueba_numero_letra.py": "OCR",
        "face/reconocimientoFacial.py": "Reconocimiento facial",
        "servicios/peticiones_supaBase.py": "API Supabase",
        "modelos/detectar-Placa/best.pt": "Modelo YOLO",
        "modelos/leer_numero_placas/best.pt": "Modelo OCR",
    }
    
    for archivo, descripcion in archivos_requeridos.items():
        total += 1
        ruta = BASE_DIR / archivo
        if check(ruta.exists(), 
                 f"{descripcion} ✓", 
                 f"{descripcion} ✗"):
            puntuacion += 1
        else:
            print(f"  └─ Ruta esperada: {ruta}")
    
    # ==================== CONFIGURACIÓN ====================
    print("\n⚙️  CONFIGURACIÓN")
    print("-" * 70)
    
    # Verificar .env
    total += 1
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            contenido = f.read()
        
        tiene_url = 'SUPABASE_URL' in contenido
        tiene_key = 'SUPABASE_KEY' in contenido
        
        if tiene_url and tiene_key:
            if check(True, ".env tiene SUPABASE_URL y SUPABASE_KEY", ""):
                puntuacion += 1
        else:
            check(False, "", ".env incompleto (falta URL o KEY)")
    else:
        check(False, "", ".env no existe")
    
    # ==================== LIBRERÍAS (opcional) ====================
    print("\n📦 LIBRERÍAS (Verificación opcional)")
    print("-" * 70)
    
    librerias_verificar = [
        ("ultralytics", "YOLO"),
        ("torch", "PyTorch"),
        ("cv2", "OpenCV"),
        ("easyocr", "EasyOCR"),
        ("supabase", "Supabase SDK"),
    ]
    
    for lib, nombre in librerias_verificar:
        try:
            __import__(lib)
            print(f"  ✓ {nombre} está instalado")
        except ImportError:
            print(f"  ⚠️  {nombre} no detectado (en venv actual)")
    
    # ==================== RESUMEN ====================
    print("\n" + "="*70)
    print(f"📊 RESULTADO: {puntuacion}/{total} verificaciones pasadas")
    print("="*70)
    
    porcentaje = (puntuacion / total) * 100
    
    if porcentaje == 100:
        print(f"\n{Fore.GREEN if HAS_COLOR else ''}✅ SISTEMA COMPLETAMENTE CONFIGURADO")
        print("Puedes ejecutar: python main_integrated.py")
    elif porcentaje >= 80:
        print(f"\n{Fore.YELLOW if HAS_COLOR else ''}⚠️  SISTEMA PARCIALMENTE CONFIGURADO ({porcentaje:.0f}%)")
        print("Sigue los pasos en GUIA_EJECUCION_RAPIDA.md")
    else:
        print(f"\n{Fore.RED if HAS_COLOR else ''}❌ SISTEMA NO ESTÁ LISTO ({porcentaje:.0f}%)")
        print("Ejecuta: python instalar.py")
    
    print("\n📚 DOCUMENTACIÓN ÚTIL:")
    print("  • RESUMEN_SOLUCION.md → Qué se implementó")
    print("  • GUIA_EJECUCION_RAPIDA.md → Cómo empezar")
    print("  • SOLUCIONES_VENV.md → Alternativas técnicas")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
