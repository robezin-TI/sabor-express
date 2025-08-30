import heapq
from math import radians, sin, cos, sqrt, atan2

def haversine(coord1, coord2):
    R = 6371.0
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

def a_star(points):
    """
    points: lista de pontos [{'lat':, 'lng':}]
    Retorna caminho otimizado simples (ordenação por proximidade)
    """
    if not points:
        return []

    start = points[0]
    unvisited = points[1:]
    path = [start]

    while unvisited:
        nearest = min(unvisited, key=lambda p: haversine(
            (path[-1]["lat"], path[-1]["lng"]),
            (p["lat"], p["lng"])
        ))
        path.append(nearest)
        unvisited.remove(nearest)

    return path
