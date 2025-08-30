import random

# Simulação de coordenadas geográficas
def get_coordinates(address: str):
    return {
        "lat": -23.55 + random.uniform(-0.05, 0.05),
        "lng": -46.63 + random.uniform(-0.05, 0.05)
    }
