
import sys
import os
sys.path.insert(0, r"C:\Users\HARRISON\Documents\modelo_deteccion_letra_numero_placa\face")

try:
    from reconocimientoFacial import comparar_rostros
    resultado = comparar_rostros(r"C:\Users\HARRISON\Documents\modelo_deteccion_letra_numero_placa\temp\TRF088\rostro_captura.jpg", r"face/imagenes_descargadas/front_1764989392442.jpg")
    print("RESULTADO:" + str(resultado))
except Exception as e:
    print(f"ERROR_DEEPFACE:{str(e)}")
    print("RESULTADO:False")
