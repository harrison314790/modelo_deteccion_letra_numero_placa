"""
Utilidades para mejorar la calidad de imágenes faciales antes de la comparación.
Estas funciones preprocesadas ayudan a aumentar la precisión del reconocimiento.
"""

import cv2
import numpy as np
from pathlib import Path


def mejorar_imagen_facial(ruta_imagen, guardar_mejorada=False):
    """
    Mejora la calidad de una imagen facial para mejor reconocimiento.
    
    Args:
        ruta_imagen: Ruta de la imagen a mejorar
        guardar_mejorada: Si True, guarda la versión mejorada
    
    Returns:
        numpy.ndarray: Imagen mejorada
    """
    # Leer imagen
    img = cv2.imread(str(ruta_imagen))
    
    if img is None:
        raise ValueError(f"No se pudo leer la imagen: {ruta_imagen}")
    
    # 1. Normalizar iluminación (CLAHE)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    lab = cv2.merge([l, a, b])
    img_mejorada = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    # 2. Reducir ruido
    img_mejorada = cv2.fastNlMeansDenoisingColored(img_mejorada, None, 10, 10, 7, 21)
    
    # 3. Aumentar nitidez ligeramente
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    img_nitida = cv2.filter2D(img_mejorada, -1, kernel)
    img_mejorada = cv2.addWeighted(img_mejorada, 0.7, img_nitida, 0.3, 0)
    
    # Guardar si se solicita
    if guardar_mejorada:
        ruta_original = Path(ruta_imagen)
        ruta_mejorada = ruta_original.parent / f"{ruta_original.stem}_mejorada{ruta_original.suffix}"
        cv2.imwrite(str(ruta_mejorada), img_mejorada)
        print(f"✅ Imagen mejorada guardada: {ruta_mejorada}")
    
    return img_mejorada


def detectar_y_alinear_rostro(imagen):
    """
    Detecta y alinea el rostro en la imagen para mejor comparación.
    
    Args:
        imagen: numpy.ndarray o ruta de imagen
    
    Returns:
        numpy.ndarray: Rostro alineado o imagen original si no se detecta rostro
    """
    # Cargar imagen si es ruta
    if isinstance(imagen, (str, Path)):
        img = cv2.imread(str(imagen))
    else:
        img = imagen.copy()
    
    # Detectar rostros
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) == 0:
        return img  # No se detectó rostro, devolver original
    
    # Tomar el rostro más grande
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    
    # Recortar rostro con margen
    margen = int(w * 0.2)
    y1 = max(0, y - margen)
    y2 = min(img.shape[0], y + h + margen)
    x1 = max(0, x - margen)
    x2 = min(img.shape[1], x + w + margen)
    
    rostro = img[y1:y2, x1:x2]
    
    return rostro


def preparar_imagen_para_comparacion(ruta_imagen, guardar_preparada=False):
    """
    Pipeline completo de preparación de imagen para reconocimiento facial.
    
    Args:
        ruta_imagen: Ruta de la imagen a preparar
        guardar_preparada: Si True, guarda la versión preparada
    
    Returns:
        numpy.ndarray: Imagen lista para comparación
    """
    print(f"🔧 Preparando imagen: {Path(ruta_imagen).name}")
    
    # 1. Mejorar calidad
    img_mejorada = mejorar_imagen_facial(ruta_imagen)
    print("   ✓ Calidad mejorada")
    
    # 2. Detectar y alinear rostro
    img_alineada = detectar_y_alinear_rostro(img_mejorada)
    print("   ✓ Rostro alineado")
    
    # 3. Redimensionar a tamaño óptimo (224x224 es común para modelos de face recognition)
    img_final = cv2.resize(img_alineada, (224, 224), interpolation=cv2.INTER_LANCZOS4)
    print("   ✓ Redimensionada a 224x224")
    
    # Guardar si se solicita
    if guardar_preparada:
        ruta_original = Path(ruta_imagen)
        ruta_preparada = ruta_original.parent / f"{ruta_original.stem}_preparada{ruta_original.suffix}"
        cv2.imwrite(str(ruta_preparada), img_final)
        print(f"   ✅ Guardada: {ruta_preparada}")
    
    return img_final


def comparar_calidad_imagenes(ruta1, ruta2):
    """
    Compara la calidad de dos imágenes y da recomendaciones.
    
    Args:
        ruta1: Ruta de primera imagen
        ruta2: Ruta de segunda imagen
    
    Returns:
        dict: Información de calidad de ambas imágenes
    """
    def calcular_calidad(ruta):
        img = cv2.imread(str(ruta))
        if img is None:
            return {"error": "No se pudo leer imagen"}
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Calcular nitidez (Laplacian)
        nitidez = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calcular brillo promedio
        brillo = np.mean(gray)
        
        # Calcular contraste
        contraste = gray.std()
        
        # Detectar rostros
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        return {
            "resolucion": f"{img.shape[1]}x{img.shape[0]}",
            "nitidez": nitidez,
            "brillo": brillo,
            "contraste": contraste,
            "rostros_detectados": len(faces),
            "tamaño_kb": Path(ruta).stat().st_size / 1024
        }
    
    info1 = calcular_calidad(ruta1)
    info2 = calcular_calidad(ruta2)
    
    print("\n" + "="*60)
    print("📊 COMPARACIÓN DE CALIDAD DE IMÁGENES")
    print("="*60)
    
    print(f"\n📷 Imagen 1: {Path(ruta1).name}")
    for key, value in info1.items():
        print(f"   {key}: {value:.2f}" if isinstance(value, float) else f"   {key}: {value}")
    
    print(f"\n📷 Imagen 2: {Path(ruta2).name}")
    for key, value in info2.items():
        print(f"   {key}: {value:.2f}" if isinstance(value, float) else f"   {key}: {value}")
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    
    if info1.get("nitidez", 0) < 100 or info2.get("nitidez", 0) < 100:
        print("   ⚠️  Nitidez baja detectada - considere usar imágenes más nítidas")
    
    if info1.get("rostros_detectados", 0) == 0 or info2.get("rostros_detectados", 0) == 0:
        print("   ⚠️  No se detectó rostro en alguna imagen")
    
    if abs(info1.get("brillo", 128) - info2.get("brillo", 128)) > 50:
        print("   ⚠️  Gran diferencia de brillo - puede afectar precisión")
    
    print("="*60 + "\n")
    
    return {"imagen1": info1, "imagen2": info2}


if __name__ == "__main__":
    """Ejemplo de uso"""
    print("🧪 Utilidades de Mejora de Imágenes Faciales")
    print("="*60)
    print("\nEjemplos de uso:")
    print("\n1. Mejorar calidad de imagen:")
    print("   img = mejorar_imagen_facial('foto.jpg', guardar_mejorada=True)")
    print("\n2. Preparar imagen para comparación:")
    print("   img = preparar_imagen_para_comparacion('foto.jpg', guardar_preparada=True)")
    print("\n3. Comparar calidad de dos imágenes:")
    print("   info = comparar_calidad_imagenes('foto1.jpg', 'foto2.jpg')")
    print("\n" + "="*60)
