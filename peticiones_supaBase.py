import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("SUPABASE_URL")
ANON = os.getenv("SUPABASE_KEY")

# ==========================================
# LOGIN: obtiene access_token + user_id
# ==========================================
def login(email, password):
    url = f"{BASE}/auth/v1/token?grant_type=password"

    res = requests.post(url, json={
        "email": email,
        "password": password
    }, headers={
        "apikey": ANON,
        "Content-Type": "application/json"
    })

    data = res.json()
    if not res.ok:
        raise Exception(data)

    return data["access_token"], data["user"]["id"]


email = "harrison12468@gmail.com"
password = "3147905916"

token, user_id = login(email, password)
print("\n🔑 TOKEN OBTENIDO PARA:", user_id)


# ==========================================
# LISTAR ARCHIVOS DEL BUCKET
# ==========================================
def listar_archivos(prefix=""):
    url = f"{BASE}/storage/v1/object/list/placas"

    res = requests.post(url, json={
        "prefix": prefix
    }, headers={
        "apikey": ANON,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })

    data = res.json()

    if not res.ok:
        raise Exception(data)

    return data


# ==========================================
# SUBIR ARCHIVO A /placas/{user_id}/archivo.png
# ==========================================
def subir(local_path):
    file_name = os.path.basename(local_path)
    path_remoto = f"{user_id}/{file_name}"   # 🔥 ruta correcta

    url = f"{BASE}/storage/v1/object/placas/{path_remoto}"

    with open(local_path, "rb") as f:
        contenido = f.read()

    res = requests.post(url, headers={
        "apikey": ANON,
        "Authorization": f"Bearer {token}",
        "Content-Type": "image/png",
        "x-upsert": "true"   # permite reemplazar si ya existe
    }, data=contenido)

    if not res.ok:
        raise Exception(res.text)

    print("📤 SUBIDO:", path_remoto)
    return path_remoto


# SUBIR TODOS LOS ARCHIVOS EN detecciones/
for archivo in os.listdir("detecciones"):
    ruta = f"detecciones/{archivo}"
    if os.path.isfile(ruta):
        subir(ruta)


# ==========================================
# CREAR URL FIRMADA
# ==========================================
def firmar(path_remoto):
    url = f"{BASE}/storage/v1/object/sign/placas/{path_remoto}"

    res = requests.post(url, json={
        "expiresIn": 3600
    }, headers={
        "apikey": ANON,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })

    data = res.json()

    if not res.ok:
        raise Exception(data)

    return BASE + "/storage/v1" + data["signedURL"]


# ==========================================
# DESCARGAR ARCHIVO
# ==========================================
def descargar(path_remoto):
    url = f"{BASE}/storage/v1/object/placas/{path_remoto}"

    res = requests.get(url, headers={
        "apikey": ANON,
        "Authorization": f"Bearer {token}"
    })

    if res.status_code != 200:
        print("❌ Error:", res.text)
        return

    os.makedirs("imagenes_descargadas", exist_ok=True)

    nombre = os.path.basename(path_remoto)
    destino = f"imagenes_descargadas/{nombre}"

    with open(destino, "wb") as f:
        f.write(res.content)

    print("📥 DESCARGADA:", destino)


# ==========================================
# LISTAR ARCHIVOS DEL USUARIO
# ==========================================
archivos = listar_archivos(prefix=f"{user_id}")

print("\n📦 ARCHIVOS EN SUPABASE DEL USUARIO:")
for f in archivos:
    print("-", f["name"])

# RECONSTRUIR PATH COMPLETO CORRECTO
rutas_completas = [f"{user_id}/{f['name']}" for f in archivos]

print(rutas_completas)
print("\n📄 Rutas completas reales en Storage:")
for r in rutas_completas:
    print("-", r)

# DESCARGAR EL PRIMER ARCHIVO CORRECTAMENTE
if rutas_completas:
    for ruta in rutas_completas:
        print("\nDescargando:", ruta)
        descargar(ruta)

