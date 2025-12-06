from servicios.peticiones_supaBase import obtener_conductor_por_placa, descargar_foto_biometria
from placas.prueba_numero_letra import leer_placa
from face.reconocimientoFacial import comparar_rostros
import os

def procesar_evento_parqueadero(ruta_imagen_placa, ruta_captura_rostro):
    print("\n===============================")
    print("🚗 EVENTO PARQUEADERO INICIADO")
    print("===============================\n")

    # ---------------------------
    # 1. Validación de archivos
    # ---------------------------
    if not os.path.exists(ruta_imagen_placa):
        print(f"❌ ERROR: No existe la imagen de placa: {ruta_imagen_placa}")
        return

    if not os.path.exists(ruta_captura_rostro):
        print(f"❌ ERROR: No existe la captura del rostro: {ruta_captura_rostro}")
        return

    # ---------------------------
    # 2. Extraer texto de la placa
    # ---------------------------
    print("➡ Procesando imagen de placa...\n")

    placa = leer_placa(ruta_imagen_placa)

    if not placa:
        print("❌ No se pudo leer ninguna placa.")
        return

    print(f"✔ Placa detectada: {placa}\n")

    # ---------------------------
    # 3. Consultar en Supabase
    # ---------------------------
    print("➡ Consultando conductor en Supabase...")

    conductor = obtener_conductor_por_placa(placa)

    if not conductor:
        print("❌ La placa no está registrada en Supabase")
        return

    print(f"✔ Conductor encontrado: {conductor['nombre']}")
    print(f"✔ Foto biométrica registrada: {conductor['foto']}\n")

    # ---------------------------
    # 4. Descargar foto biométrica
    # ---------------------------
    print("➡ Descargando foto biométrica...")

    ruta_foto_biometria = descargar_foto_biometria(conductor["foto"])

    if not ruta_foto_biometria or not os.path.exists(ruta_foto_biometria):
        print("❌ No se pudo descargar la foto biométrica.")
        return

    print(f"✔ Foto descargada correctamente: {ruta_foto_biometria}\n")

    # ---------------------------
    # 5. Comparación facial
    # ---------------------------
    print("➡ Verificando identidad del conductor...\n")

    es_mismo = comparar_rostros(ruta_captura_rostro, ruta_foto_biometria)

    if es_mismo:
        print("🔓 ACCESO PERMITIDO: Coincidencia facial confirmada.\n")
    else:
        print("⛔ ACCESO DENEGADO: La cara NO coincide con la biometría.\n")



if __name__ == "__main__":
    procesar_evento_parqueadero(
        ruta_imagen_placa="placas/imagenes_descargadas/placa1.png",
        ruta_captura_rostro="face/referencia/mi_foto.jpeg"
    )
