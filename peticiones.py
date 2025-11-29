import os
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client, Client
import mimetypes

# Credenciales del .env
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Crear cliente
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Login usuario
email = "harrison12468@gmail.com"
password = "3147905916"

session = supabase.auth.sign_in_with_password({
    "email": email,
    "password": password
})

# Activar RLS con token del usuario
supabase.postgrest.auth(session.session.access_token)

# Seleccionar bucket
bucket = supabase.storage.from_("placas")

# =======================================================
# 1. LISTAR ARCHIVOS DEL BUCKET
# =======================================================
files = bucket.list()

print("ARCHIVOS EN EL BUCKET:")
for f in files:
    print("-", f["name"])

# =======================================================
# 2. GENERAR URL FIRMADA PARA DESCARGAR / VER IMAGEN
# =======================================================

if len(files) > 0:
    file_name = files[0]["name"]  # el primer archivo

    signed_url = bucket.create_signed_url(file_name, expires_in=3600)

    print("\nURL FIRMADA (1 hora):")
    print(signed_url)

# =======================================================
# 3. (OPCIONAL) DESCARGAR LA IMAGEN A LOCAL
# =======================================================

    data = bucket.download(file_name)
    with open("descargada_" + file_name, "wb") as out:
        out.write(data)

    print("\nImagen descargada como:", "descargada_" + file_name)

# Cerrar sesión
supabase.auth.sign_out()
