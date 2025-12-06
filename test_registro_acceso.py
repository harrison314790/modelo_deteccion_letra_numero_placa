"""
Script de prueba para verificar el registro de accesos en la base de datos.
Útil para probar la funcionalidad sin tener que hacer todo el flujo completo.
"""

import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from servicios.peticiones_supaBase import (
    registrar_acceso,
    crear_notificacion,
    obtener_conductor_por_placa
)


def probar_registro_acceso():
    """Prueba el registro de un acceso exitoso."""
    
    print("\n" + "="*70)
    print("🧪 PRUEBA DE REGISTRO DE ACCESO")
    print("="*70)
    
    # Solicitar placa
    placa = input("\n📋 Ingresa una placa registrada en Supabase: ").strip().upper()
    
    if not placa:
        print("❌ Placa no puede estar vacía")
        return
    
    # Buscar conductor
    print(f"\n🔍 Buscando información de la placa: {placa}")
    conductor = obtener_conductor_por_placa(placa)
    
    if not conductor:
        print("❌ No se encontró información para esa placa")
        return
    
    # Mostrar información
    nombre_completo = f"{conductor.get('nombre', '')} {conductor.get('apellido', '')}".strip()
    print(f"\n✅ Conductor encontrado:")
    print(f"   Nombre: {nombre_completo}")
    print(f"   Email: {conductor.get('email', 'N/A')}")
    print(f"   Usuario ID: {conductor.get('id')}")
    print(f"   Vehículo ID: {conductor.get('vehiculo_id')}")
    
    # Confirmar registro
    print("\n" + "-"*70)
    confirmar = input("¿Deseas registrar un acceso de PRUEBA para este usuario? (s/n): ").strip().lower()
    
    if confirmar != 's':
        print("❌ Operación cancelada")
        return
    
    # Registrar acceso de prueba
    print("\n📝 Registrando acceso de prueba...")
    print("-" * 70)
    
    registro = registrar_acceso(
        usuario_id=conductor.get('id'),
        vehiculo_id=conductor.get('vehiculo_id'),
        placa=placa,
        tipo_evento="entrada",
        metodo_acceso="facial",
        ubicacion="Parqueadero Principal - PRUEBA",
        foto_captura=None,
        confianza=0.95,
        estado="exitoso"
    )
    
    if registro:
        print("\n✅ ACCESO REGISTRADO EXITOSAMENTE")
        print(f"   ID: {registro.get('id')}")
        print(f"   Usuario ID: {registro.get('usuario_id')}")
        print(f"   Vehículo ID: {registro.get('vehiculo_id')}")
        print(f"   Placa: {registro.get('placa')}")
        print(f"   Tipo: {registro.get('tipo_evento')}")
        print(f"   Método: {registro.get('metodo_acceso')}")
        print(f"   Estado: {registro.get('estado')}")
        print(f"   Confianza: {registro.get('confianza')}")
        print(f"   Fecha: {registro.get('created_at')}")
    else:
        print("\n❌ Error al registrar el acceso")
        return
    
    # Crear notificación
    print("\n🔔 Creando notificación de prueba...")
    print("-" * 70)
    
    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    notificacion = crear_notificacion(
        usuario_id=conductor.get('id'),
        titulo="✅ Acceso de Prueba Registrado",
        mensaje=f"Se registró un acceso de prueba. Placa: {placa}. Fecha: {fecha_hora}. Esta es una notificación de prueba del sistema.",
        tipo="info",
        icono="🧪"
    )
    
    if notificacion:
        print("\n✅ NOTIFICACIÓN CREADA EXITOSAMENTE")
        print(f"   ID: {notificacion.get('id')}")
        print(f"   Usuario ID: {notificacion.get('usuario_id')}")
        print(f"   Título: {notificacion.get('titulo')}")
        print(f"   Mensaje: {notificacion.get('mensaje')}")
        print(f"   Tipo: {notificacion.get('tipo')}")
        print(f"   Leída: {notificacion.get('leida')}")
        print(f"   Fecha: {notificacion.get('created_at')}")
    else:
        print("\n⚠️  No se pudo crear la notificación")
    
    print("\n" + "="*70)
    print("✅ PRUEBA COMPLETADA")
    print("="*70)
    print("\n💡 Verifica en tu aplicación frontend:")
    print("   1. La tabla 'registro_acceso' debe tener un nuevo registro")
    print("   2. La tabla 'notificaciones' debe tener una nueva notificación")
    print("   3. El usuario debe poder ver la notificación en su interfaz\n")


def probar_acceso_denegado():
    """Prueba el registro de un acceso denegado."""
    
    print("\n" + "="*70)
    print("🧪 PRUEBA DE REGISTRO DE ACCESO DENEGADO")
    print("="*70)
    
    # Solicitar placa
    placa = input("\n📋 Ingresa una placa registrada: ").strip().upper()
    
    if not placa:
        print("❌ Placa no puede estar vacía")
        return
    
    # Buscar conductor
    print(f"\n🔍 Buscando información de la placa: {placa}")
    conductor = obtener_conductor_por_placa(placa)
    
    if not conductor:
        print("❌ No se encontró información para esa placa")
        return
    
    nombre_completo = f"{conductor.get('nombre', '')} {conductor.get('apellido', '')}".strip()
    print(f"\n✅ Conductor: {nombre_completo}")
    
    # Registrar acceso denegado
    print("\n📝 Registrando intento de acceso DENEGADO...")
    
    registro = registrar_acceso(
        usuario_id=conductor.get('id'),
        vehiculo_id=conductor.get('vehiculo_id'),
        placa=placa,
        tipo_evento="entrada",
        metodo_acceso="facial",
        ubicacion="Parqueadero Principal - PRUEBA",
        foto_captura=None,
        confianza=0.0,
        estado="denegado"
    )
    
    if registro:
        print(f"✅ Intento denegado registrado (ID: {registro.get('id')})")
    
    # Crear notificación de advertencia
    print("\n🔔 Creando notificación de advertencia...")
    
    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    notificacion = crear_notificacion(
        usuario_id=conductor.get('id'),
        titulo="⚠️ Intento de Acceso Denegado - PRUEBA",
        mensaje=f"Intento de ingreso con placa {placa} fue rechazado en prueba del sistema. Fecha: {fecha_hora}",
        tipo="advertencia",
        icono="🚨"
    )
    
    if notificacion:
        print(f"✅ Notificación de advertencia creada")
    
    print("\n✅ Prueba completada\n")


def menu():
    """Menú principal."""
    
    while True:
        print("\n" + "="*70)
        print("🧪 MENÚ DE PRUEBAS - REGISTRO DE ACCESOS")
        print("="*70)
        print("\n1. Probar registro de acceso EXITOSO")
        print("2. Probar registro de acceso DENEGADO")
        print("3. Salir")
        
        opcion = input("\nSelecciona una opción (1-3): ").strip()
        
        if opcion == "1":
            probar_registro_acceso()
        elif opcion == "2":
            probar_acceso_denegado()
        elif opcion == "3":
            print("\n👋 Saliendo...\n")
            break
        else:
            print("\n❌ Opción inválida. Intenta de nuevo.")


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrumpido por el usuario\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
