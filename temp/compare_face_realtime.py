
import sys
sys.path.insert(0, r"C:\Users\HARRISON\Documents\modelo_deteccion_letra_numero_placa\face")

try:
    from deepface import DeepFace
    result = DeepFace.verify(
        img1_path=r"face/imagenes_descargadas/front_1764989392442.jpg",
        img2_path=r"C:\Users\HARRISON\Documents\modelo_deteccion_letra_numero_placa\temp\temp_frame_compare.jpg",
        model_name='ArcFace',  # Modelo más preciso
        enforce_detection=False,
        distance_metric='cosine',
        align=True  # Alinear rostros para mejor precisión
    )
    
    # Aplicar umbral más estricto para mayor precisión
    distancia = result['distance']
    es_coincidencia = distancia < 0.60  # Umbral estricto para ArcFace
    
    print(f"RESULTADO:{es_coincidencia}")
    print(f"DISTANCIA:{distancia:.4f}")
except Exception as e:
    print(f"RESULTADO:False")
    print(f"DISTANCIA:0.9999")
    print(f"ERROR:{str(e)[:50]}")
