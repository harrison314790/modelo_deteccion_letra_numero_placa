import cv2
from deepface import DeepFace

def comparar_rostros(ruta_rostro_capturado, ruta_rostro_referencia):
    """
    Compara dos rostros usando DeepFace con modelo de alta precisión.
    
    ruta_rostro_capturado → imagen tomada en el parqueadero (ESP32 CAM / cámara)
    ruta_rostro_referencia → imagen guardada en Supabase (descargada previamente)

    Retorna:
        True si es la misma persona
        False si no coincide
    """

    try:
        # Usar ArcFace para mayor precisión
        result = DeepFace.verify(
            img1_path=ruta_rostro_capturado,
            img2_path=ruta_rostro_referencia,
            model_name="ArcFace",  # Modelo más preciso que Facenet512
            enforce_detection=False,
            distance_metric='cosine',
            align=True  # Alinear rostros para mejor comparación
        )
        
        # Aplicar umbral más estricto para mayor precisión
        distancia = result["distance"]
        es_coincidencia = distancia < 0.60  # Umbral estricto para ArcFace
        
        print(f"📊 Distancia: {distancia:.4f} | Coincidencia: {es_coincidencia}")
        
        return es_coincidencia

    except Exception as e:
        print("❌ Error en comparación facial:", e)
        return False
