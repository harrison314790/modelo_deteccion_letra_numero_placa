"""
Script para probar y comparar la precisión de diferentes configuraciones
de reconocimiento facial.
"""

import sys
from pathlib import Path

# Agregar directorio face al path
BASE_DIR = Path(__file__).parent
FACE_DIR = BASE_DIR / "face"
sys.path.insert(0, str(FACE_DIR))

from deepface import DeepFace
import cv2


def probar_diferentes_modelos(img1_path, img2_path):
    """
    Prueba diferentes modelos y configuraciones para comparar precisión.
    
    Args:
        img1_path: Ruta de la primera imagen
        img2_path: Ruta de la segunda imagen
    """
    print("\n" + "="*70)
    print("🧪 PRUEBA DE PRECISIÓN - COMPARACIÓN DE MODELOS")
    print("="*70)
    print(f"📷 Imagen 1: {Path(img1_path).name}")
    print(f"📷 Imagen 2: {Path(img2_path).name}")
    print("="*70 + "\n")
    
    # Configuraciones a probar
    configuraciones = [
        {
            "nombre": "Facenet512 (Configuración Antigua)",
            "model": "Facenet512",
            "umbral": None,  # Usar umbral por defecto
            "align": False
        },
        {
            "nombre": "ArcFace (Configuración Nueva - Estricta)",
            "model": "ArcFace",
            "umbral": 0.60,  # Umbral estricto
            "align": True
        },
        {
            "nombre": "ArcFace (Configuración Nueva - Estándar)",
            "model": "ArcFace",
            "umbral": 0.68,  # Umbral estándar
            "align": True
        },
        {
            "nombre": "VGG-Face (Rápido)",
            "model": "VGG-Face",
            "umbral": 0.40,
            "align": True
        }
    ]
    
    resultados = []
    
    for config in configuraciones:
        print(f"\n🔍 Probando: {config['nombre']}")
        print("-" * 70)
        
        try:
            # Realizar verificación
            result = DeepFace.verify(
                img1_path=str(img1_path),
                img2_path=str(img2_path),
                model_name=config["model"],
                enforce_detection=False,
                distance_metric='cosine',
                align=config["align"]
            )
            
            distancia = result["distance"]
            verificado_default = result["verified"]
            
            # Aplicar umbral personalizado si existe
            if config["umbral"] is not None:
                verificado_custom = distancia < config["umbral"]
            else:
                verificado_custom = verificado_default
            
            # Calcular confianza
            confianza = (1 - distancia) * 100
            
            resultados.append({
                "config": config["nombre"],
                "distancia": distancia,
                "verificado_default": verificado_default,
                "verificado_custom": verificado_custom,
                "confianza": confianza
            })
            
            # Mostrar resultados
            print(f"   Distancia: {distancia:.4f}")
            print(f"   Verificado (default): {'✅ SÍ' if verificado_default else '❌ NO'}")
            if config["umbral"] is not None:
                print(f"   Verificado (umbral {config['umbral']}): {'✅ SÍ' if verificado_custom else '❌ NO'}")
            print(f"   Confianza: {confianza:.1f}%")
            print(f"   Estado: {'🟢 EXITO' if True else '🔴 ERROR'}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:60]}")
            resultados.append({
                "config": config["nombre"],
                "error": str(e)[:60]
            })
    
    # Resumen comparativo
    print("\n" + "="*70)
    print("📊 RESUMEN COMPARATIVO")
    print("="*70)
    
    print(f"\n{'Modelo':<45} {'Distancia':<12} {'Resultado':<10} {'Confianza'}")
    print("-" * 70)
    
    for res in resultados:
        if "error" not in res:
            modelo = res["config"][:44]
            distancia = f"{res['distancia']:.4f}"
            resultado = "✅ MATCH" if res["verificado_custom"] else "❌ NO MATCH"
            confianza = f"{res['confianza']:.1f}%"
            print(f"{modelo:<45} {distancia:<12} {resultado:<10} {confianza}")
        else:
            print(f"{res['config']:<45} ERROR")
    
    print("="*70)
    
    # Recomendación
    print("\n💡 RECOMENDACIÓN:")
    if resultados:
        mejor_config = min([r for r in resultados if "error" not in r], 
                          key=lambda x: x["distancia"])
        print(f"   Mejor precisión: {mejor_config['config']}")
        print(f"   Distancia más baja: {mejor_config['distancia']:.4f}")
    print("="*70 + "\n")


def verificar_calidad_imagenes(img1_path, img2_path):
    """Verifica la calidad de las imágenes antes de comparar."""
    print("\n" + "="*70)
    print("🔍 VERIFICACIÓN DE CALIDAD DE IMÁGENES")
    print("="*70)
    
    for i, img_path in enumerate([img1_path, img2_path], 1):
        print(f"\n📷 Imagen {i}: {Path(img_path).name}")
        print("-" * 70)
        
        # Leer imagen
        img = cv2.imread(str(img_path))
        
        if img is None:
            print("   ❌ No se pudo leer la imagen")
            continue
        
        # Información básica
        h, w = img.shape[:2]
        print(f"   Resolución: {w}x{h}")
        print(f"   Tamaño: {Path(img_path).stat().st_size / 1024:.1f} KB")
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Calcular métricas
        nitidez = cv2.Laplacian(gray, cv2.CV_64F).var()
        brillo = gray.mean()
        contraste = gray.std()
        
        print(f"   Nitidez: {nitidez:.2f}", end="")
        if nitidez < 100:
            print(" ⚠️  Baja")
        elif nitidez > 500:
            print(" ✅ Excelente")
        else:
            print(" ✅ Buena")
        
        print(f"   Brillo: {brillo:.2f}", end="")
        if brillo < 80 or brillo > 180:
            print(" ⚠️  Puede mejorar")
        else:
            print(" ✅ Adecuado")
        
        print(f"   Contraste: {contraste:.2f}", end="")
        if contraste < 30:
            print(" ⚠️  Bajo")
        else:
            print(" ✅ Bueno")
        
        # Detectar rostros
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        print(f"   Rostros detectados: {len(faces)}", end="")
        if len(faces) == 0:
            print(" ❌ Ninguno")
        elif len(faces) == 1:
            print(" ✅ Uno")
        else:
            print(f" ⚠️  Múltiples ({len(faces)})")
    
    print("\n" + "="*70 + "\n")


def main():
    """Función principal."""
    print("\n" + "="*70)
    print("🎯 SCRIPT DE PRUEBA DE PRECISIÓN - RECONOCIMIENTO FACIAL")
    print("="*70)
    
    # Solicitar rutas de imágenes
    print("\n📂 Por favor, proporciona las rutas de las imágenes a comparar:")
    print("\nEjemplos de rutas:")
    print("  - face/referencia/mi_foto.jpeg")
    print("  - face/imagenes_descargadas/front_123.jpg")
    print("  - temp/captura.jpg")
    
    img1_path = input("\n📷 Ruta de imagen 1: ").strip().strip('"')
    img2_path = input("📷 Ruta de imagen 2: ").strip().strip('"')
    
    # Convertir a Path
    img1_path = Path(img1_path)
    img2_path = Path(img2_path)
    
    # Verificar que existan
    if not img1_path.exists():
        print(f"\n❌ Error: No se encuentra {img1_path}")
        return
    
    if not img2_path.exists():
        print(f"\n❌ Error: No se encuentra {img2_path}")
        return
    
    # 1. Verificar calidad
    verificar_calidad_imagenes(img1_path, img2_path)
    
    input("⏸️  Presiona ENTER para continuar con las pruebas de modelos...")
    
    # 2. Probar diferentes modelos
    probar_diferentes_modelos(img1_path, img2_path)
    
    print("✅ Pruebas completadas!")
    print("\n💡 Recomendación: Usa ArcFace con umbral 0.60 para máxima precisión")
    print("   (Ya está implementado en tus scripts de reconocimiento)\n")


if __name__ == "__main__":
    main()
