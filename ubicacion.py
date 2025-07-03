import requests
import urllib.parse

# Clave API de Graphhopper
API_KEY = "9db0905d-f6d0-4a77-b9e3-9b90d159e108"

def geocode(location):
    """
    Convierte una ubicación en coordenadas geográficas (latitud, longitud).
    """
    url = "https://graphhopper.com/api/1/geocode?"
    params = {
        "q": location,
        "limit": 1,
        "key": API_KEY
    }
    full_url = url + urllib.parse.urlencode(params)
    try:
        response = requests.get(full_url)
        response.raise_for_status() # Lanza una excepción para errores HTTP
        data = response.json()
        
        if data["hits"]:
            point = data["hits"][0]["point"]
            name = data["hits"][0]["name"]
            country = data["hits"][0].get("country", "")
            full_name = f"{name}, {country}" if country else name
            return point["lat"], point["lng"], full_name
        else:
            print(f"  Ubicación no encontrada: {location}")
            return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"  Error de conexión al geocodificar '{location}': {e}")
        return None, None, None

def get_route(start, end, vehicle="car"):
    """
    Calcula una ruta entre dos puntos usando un tipo de vehículo específico.
    """
    url = "https://graphhopper.com/api/1/route"
    params = {
        "point": [f"{start[0]},{start[1]}", f"{end[0]},{end[1]}"],
        "vehicle": vehicle, # Aquí usamos la variable vehicle
        "locale": "es",
        "instructions": "true",
        "calc_points": "true",
        "key": API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Lanza una excepción para errores HTTP
        data = response.json()
        
        if data["paths"]:
            path = data["paths"][0]
            distance_km = path["distance"] / 1000
            time_sec = path["time"] / 1000
            
            # Consumo de combustible estimado, ajustado según el vehículo
            fuel = 0 # Valor por defecto

            if vehicle == "car":
                fuel = round(distance_km * 0.08, 2) # 8 litros/100km
            elif vehicle == "motorcycle":
                fuel = round(distance_km * 0.04, 2) # 4 litros/100km
            # Para otros vehículos como bicicleta, pie, camión, tren, avión, el consumo se mantiene en 0 o no se aplica

            return path["instructions"], distance_km, time_sec, fuel
        else:
            print("  No se encontraron rutas para la combinación de puntos y vehículo.")
            return None, None, None, None
    except requests.exceptions.RequestException as e:
        print(f"  Error de conexión al obtener la ruta: {e}")
        return None, None, None, None
    except KeyError:
        print("  Error: La respuesta de la API no tiene el formato esperado. ¿Ruta inválida?")
        return None, None, None, None


# --- PROGRAMA PRINCIPAL ---
print("*******************************************")
print("    Estimador de Ruta con Graphhopper")
print("*******************************************")

while True:
    origen = input("\nUbicación de inicio (o 's' para salir): ")
    if origen.lower() == "s":
        print("Saliendo del programa. ¡Hasta luego!")
        break

    destino = input("Ubicación de destino (o 's' para salir): ")
    if destino.lower() == "s":
        print("Saliendo del programa. ¡Hasta luego!")
        break

    # Selección del tipo de vehículo
    print("\nSelecciona el tipo de medio de transporte:")
    print("  1. Coche")
    print("  2. Bicicleta")
    print("  3. Moto")
    print("  4. A pie")
    print("  5. Camión")
    print("  6. Tren (solo rutas limitadas por vías férreas)") # Explicación para el usuario
    print("  7. Avión (solo puntos de inicio/fin en aeropuertos grandes)") # Explicación para el usuario
    
    # Mapeo de la elección del usuario a los valores que entiende la API de GraphHopper
    tipo_vehiculo_opciones = {
        "1": {"api_value": "car", "display_name": "Coche"},
        "2": {"api_value": "bike", "display_name": "Bicicleta"},
        "3": {"api_value": "motorcycle", "display_name": "Moto"},
        "4": {"api_value": "foot", "display_name": "A pie"},
        "5": {"api_value": "truck", "display_name": "Camión"},
        "6": {"api_value": "train", "display_name": "Tren"}, # Esto es experimental/limitado
        "7": {"api_value": "plane", "display_name": "Avión"}  # Esto es experimental/limitado
    }
    
    eleccion_vehiculo = input("Ingresa el número de tu elección (o 's' para salir): ")
    if eleccion_vehiculo.lower() == "s":
        print("Saliendo del programa. ¡Hasta luego!")
        break
    
    selected_vehicle_info = tipo_vehiculo_opciones.get(eleccion_vehiculo)
    if not selected_vehicle_info:
        print("  Opción de vehículo no válida. Por favor, elige un número del 1 al 7.")
        continue # Vuelve a pedir las ubicaciones

    vehicle_api_value = selected_vehicle_info["api_value"]
    vehicle_display_name = selected_vehicle_info["display_name"]

    lat1, lng1, origen_full = geocode(origen)
    if None in (lat1, lng1):
        continue # Vuelve a pedir las ubicaciones si el origen no se encuentra

    lat2, lng2, destino_full = geocode(destino)
    if None in (lat2, lng2):
        continue # Vuelve a pedir las ubicaciones si el destino no se encuentra

    print("\n***************************************")
    print(f"Desde: {origen_full}")
    print(f"Hasta: {destino_full}")
    print(f"Tipo de Vehículo: {vehicle_display_name}")
    print("***************************************")

    instrucciones, distancia, duracion, combustible = get_route((lat1, lng1), (lat2, lng2), vehicle=vehicle_api_value)

    if instrucciones:
        print(f"\nDistancia Recorrida: {round(distancia, 2)} km")
        print(f"Duración del Viaje: {round(duracion / 60, 2)} minutos")
        
        if combustible > 0:
            print(f"Consumo de Combustible Estimado: {combustible} litros")
        else:
            print("Consumo de Combustible: No aplicable o no calculado para este vehículo.")
        
        print("\nInstrucciones de Ruta:\n")
        
        for i, inst in enumerate(instrucciones):
            # Asegúrate de que 'distance' sea un número antes de redondear
            dist_str = ""
            if isinstance(inst.get('distance'), (int, float)):
                # Convertir a kilómetros si la distancia es muy grande para metros
                if inst['distance'] >= 1000:
                    dist_str = f"({round(inst['distance']/1000, 2)} km)"
                else:
                    dist_str = f"({round(inst['distance'], 1)} m)"
            print(f"  {i+1}. {inst['text']} {dist_str}")
    else:
        print("No se pudo obtener la ruta con los detalles especificados.")