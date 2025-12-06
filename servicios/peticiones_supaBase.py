import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE")

# ==========================================
# 1. CONSULTAR CONDUCTOR POR PLACA
# ==========================================
def obtener_conductor_por_placa(placa: str):
    """
    Busca la placa en vehiculo_usuario, obtiene el vehiculo_propietario (user_id),
    y luego consulta los datos del usuario en perfil_usuario.
    Retorna dict con los datos del conductor o None si no existe.
    """
    
    # Normalizar la placa (remover espacios, convertir a mayúsculas)
    placa_normalizada = placa.strip().upper()
    print(f"🔎 Buscando placa normalizada: '{placa_normalizada}'")

    # PASO 1: Buscar la placa en vehiculo_usuario
    url_vehiculo = f"{SUPABASE_URL}/rest/v1/vehiculo_usuario"

    res_vehiculo = requests.get(url_vehiculo, params={
    "placa": f"ilike.%{placa_normalizada}%",
    "select": "*"
    }, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    })

    if not res_vehiculo.ok:
        print("❌ Error buscando placa en vehiculo_usuario:", res_vehiculo.text)
        return None

    datos_vehiculo = res_vehiculo.json()

    if len(datos_vehiculo) == 0:
        print(f"❌ La placa '{placa_normalizada}' no está registrada")
        print(f"   💡 Intentando búsqueda flexible...")
        
        # Intento 2: búsqueda LIKE (sin case-sensitive)
        res_vehiculo = requests.get(url_vehiculo, params={
            "placa": f"ilike.%{placa_normalizada}%",
            "select": "*"
        }, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        })
        
        if res_vehiculo.ok:
            datos_vehiculo = res_vehiculo.json()
            if len(datos_vehiculo) > 0:
                print(f"   ✅ Placa encontrada con búsqueda flexible")
            else:
                print(f"   ❌ Ninguna placa coincide con '{placa_normalizada}'")
                return None
        else:
            print(f"   ❌ Error en búsqueda flexible: {res_vehiculo.text}")
            return None

    # PASO 2: Obtener el vehiculo_propietario (user_id)
    propietario_id = datos_vehiculo[0].get("vehiculo_propietario")
    
    if not propietario_id:
        print("❌ La placa no tiene propietario asociado")
        return None

    print(f"   ✅ Placa encontrada - Propietario ID: {propietario_id}")

    # PASO 3: Buscar los datos del propietario en perfil_usuario
    url_perfil = f"{SUPABASE_URL}/rest/v1/perfil_usuario"

    res_perfil = requests.get(url_perfil, params={
        "id": f"eq.{propietario_id}",
        "select": "*"
    }, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    })

    if not res_perfil.ok:
        print("❌ Error buscando perfil del usuario:", res_perfil.text)
        return None

    datos_perfil = res_perfil.json()

    if len(datos_perfil) == 0:
        print(f"❌ No se encontró perfil para el propietario ID: {propietario_id}")
        return None

    # PASO 4: Combinar información del vehículo + perfil
    conductor = datos_perfil[0].copy()
    conductor["placa"] = datos_vehiculo[0].get("placa")
    conductor["foto_placa"] = datos_vehiculo[0].get("foto_placa")
    conductor["vehiculo_id"] = datos_vehiculo[0].get("id")  # 👈 AGREGAR ID DEL VEHÍCULO

    # 👇 AGREGAR FOTO BIOMÉTRICA
    conductor["foto_biometria"] = datos_perfil[0].get("foto_rostro")


    
    print(f"✅ Conductor encontrado: {conductor.get('nombre')} {conductor.get('apellido')}")
    return conductor


# ==========================================
# 2. DESCARGAR FOTO BIOMÉTRICA
# ==========================================
def descargar_foto_biometria(ruta_en_supabase: str):
    """
    Descarga una foto desde el bucket 'biometria'
    ruta_en_supabase llega como:
    95c2c4f1-85a5-4650-b9a7-c2cdd41f78e5/front_1764989392442.jpg
    """

    url = f"{SUPABASE_URL}/storage/v1/object/biometria/{ruta_en_supabase}"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print("❌ Error descargando biometría:", res.text)
        return None

    destino_dir = "face/imagenes_descargadas"
    os.makedirs(destino_dir, exist_ok=True)

    nombre_archivo = os.path.basename(ruta_en_supabase)
    ruta_local = f"{destino_dir}/{nombre_archivo}"

    with open(ruta_local, "wb") as f:
        f.write(res.content)

    return ruta_local


# ==========================================
# 3. REGISTRAR ACCESO EN BASE DE DATOS
# ==========================================
def registrar_acceso(
    usuario_id: str,
    vehiculo_id: str,
    placa: str,
    tipo_evento: str = "entrada",
    metodo_acceso: str = "facial",
    ubicacion: str = "Parqueadero Principal",
    foto_captura: str = None,
    confianza: float = None,
    estado: str = "exitoso"
):
    """
    Registra un acceso en la tabla registro_acceso.
    
    Args:
        usuario_id: UUID del usuario (auth.users)
        vehiculo_id: UUID del vehículo
        placa: Placa del vehículo
        tipo_evento: 'entrada' o 'salida'
        metodo_acceso: 'facial', 'placa' o 'manual'
        ubicacion: Ubicación del acceso
        foto_captura: URL de la foto capturada (opcional)
        confianza: Nivel de confianza del reconocimiento (0-1)
        estado: 'exitoso', 'denegado' o 'pendiente'
    
    Returns:
        dict con los datos del registro creado o None si hay error
    """
    
    url = f"{SUPABASE_URL}/rest/v1/registro_acceso"
    
    # Preparar datos
    datos = {
        "usuario_id": usuario_id,
        "vehiculo_id": vehiculo_id,
        "placa": placa.upper(),
        "tipo_evento": tipo_evento,
        "metodo_acceso": metodo_acceso,
        "ubicacion": ubicacion,
        "estado": estado
    }
    
    # Agregar campos opcionales
    if foto_captura:
        datos["foto_captura"] = foto_captura
    
    if confianza is not None:
        # Asegurar que esté entre 0 y 1
        datos["confianza"] = max(0.0, min(1.0, float(confianza)))
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    try:
        res = requests.post(url, json=datos, headers=headers)
        
        if res.status_code in [200, 201]:
            resultado = res.json()
            print(f"✅ Acceso registrado en base de datos (ID: {resultado[0].get('id', 'N/A')})")
            return resultado[0] if resultado else None
        else:
            print(f"❌ Error registrando acceso: {res.status_code}")
            print(f"   Respuesta: {res.text}")
            return None
    
    except Exception as e:
        print(f"❌ Excepción registrando acceso: {str(e)}")
        return None


# ==========================================
# 4. CREAR NOTIFICACIÓN
# ==========================================
def crear_notificacion(
    usuario_id: str,
    titulo: str,
    mensaje: str,
    tipo: str = "info",
    icono: str = None,
    url: str = None
):
    """
    Crea una notificación para el usuario.
    
    Args:
        usuario_id: UUID del usuario (auth.users)
        titulo: Título de la notificación
        mensaje: Mensaje de la notificación
        tipo: 'info', 'exito', 'advertencia' o 'error'
        icono: Icono opcional (nombre o emoji)
        url: URL opcional para acción
    
    Returns:
        dict con los datos de la notificación creada o None si hay error
    """
    
    url_endpoint = f"{SUPABASE_URL}/rest/v1/notificaciones"
    
    datos = {
        "usuario_id": usuario_id,
        "titulo": titulo,
        "mensaje": mensaje,
        "tipo": tipo,
        "leida": False
    }
    
    if icono:
        datos["icono"] = icono
    
    if url:
        datos["url"] = url
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    try:
        res = requests.post(url_endpoint, json=datos, headers=headers)
        
        if res.status_code in [200, 201]:
            resultado = res.json()
            print(f"✅ Notificación creada (ID: {resultado[0].get('id', 'N/A')})")
            return resultado[0] if resultado else None
        else:
            print(f"⚠️  Error creando notificación: {res.status_code}")
            print(f"   Respuesta: {res.text}")
            return None
    
    except Exception as e:
        print(f"⚠️  Excepción creando notificación: {str(e)}")
        return None



