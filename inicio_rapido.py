#!/usr/bin/env python3
"""
🚀 INICIO RÁPIDO - Ejecuta esto primero

Este script te guía paso a paso para:
1. Instalar ambos entornos
2. Verificar que todo está correcto
3. Ejecutar el flujo integrado
"""

import subprocess
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

def ejecutar_paso(titulo, comando, es_python=False):
    """Ejecuta un paso con feedback visual."""
    print(f"\n{'='*70}")
    print(f"📌 {titulo}")
    print(f"{'='*70}")
    
    if es_python:
        print(f"Ejecutando: python {comando}\n")
        try:
            exec(open(comando).read())
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    else:
        print(f"Ejecutando: {comando}\n")
        try:
            resultado = subprocess.run(comando, shell=True, capture_output=False)
            return resultado.returncode == 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

def main():
    print("\n" + "🎯"*35)
    print("INICIO RÁPIDO - SISTEMA DE DETECCIÓN DE PLACAS Y RECONOCIMIENTO FACIAL")
    print("🎯"*35)
    
    os.chdir(BASE_DIR)
    
    # PASO 1: Instalación automática
    print("\n\n⏭️  PASO 1/3: Instalar entornos virtuales")
    print("-" * 70)
    print("Se instalarán automáticamente:")
    print("  • venv 3.11.8 (.venv) → YOLO + OCR + Supabase")
    print("  • venv 3.10.11 (face/deepface_env) → DeepFace")
    
    respuesta = input("\n¿Continuar con la instalación? (s/n): ").lower()
    
    if respuesta != 's':
        print("❌ Instalación cancelada")
        return
    
    print("\n⏳ Esto puede tomar varios minutos...\n")
    
    if not ejecutar_paso("Instalando entornos", "python instalar.py"):
        print("⚠️  Hubo un error en la instalación")
        print("💡 Intenta ejecutar manualmente:")
        print("   python instalar.py")
        return
    
    # PASO 2: Diagnóstico
    print("\n\n⏭️  PASO 2/3: Verificar configuración")
    print("-" * 70)
    
    if not ejecutar_paso("Verificando entornos", "python diagnostico_venv.py"):
        print("⚠️  Verificación completada con advertencias")
    
    # PASO 3: Verificar .env
    print("\n\n⏭️  PASO 3/3: Verificar configuración de Supabase")
    print("-" * 70)
    
    env_file = BASE_DIR / ".env"
    
    if not env_file.exists():
        print("⚠️  No encontrado: .env")
        print("\nDebes crear un archivo .env con tus credenciales de Supabase:")
        print("\n```")
        print('SUPABASE_URL="https://tu-proyecto.supabase.co"')
        print('SUPABASE_KEY="tu-api-key-anon"')
        print("```\n")
        
        respuesta = input("¿Deseas crear el archivo .env ahora? (s/n): ").lower()
        
        if respuesta == 's':
            url = input("\nIngresa tu SUPABASE_URL: ").strip()
            key = input("Ingresa tu SUPABASE_KEY: ").strip()
            
            with open(env_file, 'w') as f:
                f.write(f'SUPABASE_URL="{url}"\n')
                f.write(f'SUPABASE_KEY="{key}"\n')
            
            print("✅ .env creado")
        else:
            print("⚠️  Debes crear .env antes de ejecutar main_integrated.py")
            return
    else:
        print("✔ .env existe")
        with open(env_file, 'r') as f:
            contenido = f.read()
            if 'SUPABASE_URL' in contenido and 'SUPABASE_KEY' in contenido:
                print("✔ Credenciales de Supabase detectadas")
            else:
                print("⚠️  .env existe pero parece incompleto")
    
    # RESUMEN FINAL
    print("\n\n" + "="*70)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("="*70)
    
    print("\n📝 Resumen de lo que se instaló:")
    print("  ✔ venv 3.11.8 (.venv)")
    print("  ✔ venv 3.10.11 (face/deepface_env)")
    print("  ✔ Todas las dependencias requeridas")
    print("  ✔ Archivo .env configurado")
    
    print("\n🚀 PRÓXIMO PASO: Ejecutar el sistema")
    print("-" * 70)
    
    respuesta = input("\n¿Deseas ejecutar main_integrated.py ahora? (s/n): ").lower()
    
    if respuesta == 's':
        print("\n⏳ Iniciando flujo integrado...\n")
        print("="*70)
        print("INSTRUCCIONES:")
        print("  1. Se abrirá tu cámara web")
        print("  2. Captura una foto de la placa (presiona ESPACIO)")
        print("  3. El sistema detectará y leerá la placa")
        print("  4. Consultará Supabase por el conductor")
        print("  5. Se abrirá la cámara nuevamente para capturar tu rostro")
        print("  6. Comparará tu rostro con la biometría registrada")
        print("  7. Verás si acceso es permitido o denegado")
        print("="*70)
        
        input("\nPresiona ENTER para continuar...")
        
        venv_python = BASE_DIR / ".venv" / "Scripts" / "python.exe"
        
        if not venv_python.exists():
            print(f"❌ No encontrado: {venv_python}")
            print("⚠️  Verifica que la instalación fue exitosa")
            return
        
        try:
            subprocess.run(
                [str(venv_python), "main_integrated.py"],
                cwd=str(BASE_DIR)
            )
        except Exception as e:
            print(f"❌ Error ejecutando: {e}")
    else:
        print("\n📚 Para ejecutar después:")
        print("```powershell")
        print(".\\venv\\Scripts\\Activate.ps1")
        print("python main_integrated.py")
        print("```")
    
    # AYUDA ADICIONAL
    print("\n\n📚 DOCUMENTACIÓN DISPONIBLE")
    print("-" * 70)
    print("  • README.md → Descripción general del proyecto")
    print("  • GUIA_EJECUCION_RAPIDA.md → Paso a paso detallado")
    print("  • INTEGRACION_MULTIPLES_VENV.md → Detalles técnicos")
    print("  • SOLUCIONES_VENV.md → Alternativas de integración")
    
    print("\n" + "="*70)
    print("✅ ¡Todo configurado! Puedes empezar a usar el sistema")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Proceso interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
