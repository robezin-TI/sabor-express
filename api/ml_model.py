import numpy as np
from sklearn.linear_model import LinearRegression

class DeliveryTimeModel:
    """
    Modelo simples de exemplo: estima tempo (min) a partir de distância total (km) e nº de paradas.
    """
    def __init__(self):
        # Treino sintético rápido
        rng = np.random.default_rng(7)
        distances = rng.uniform(0.5, 25.0, 200)  # km
        stops = rng.integers(2, 15, 200)
        noise = rng.normal(0, 3, 200)
        y = 3 + distances*2.1 + stops*1.2 + noise  # minutos
        X = np.c_[distances, stops]
        self.model = LinearRegression().fit(X, y)

    def predict(self, distance_km: float, stops: int) -> float:
        X = np.array([[float(distance_km), int(stops)]])
        y = self.model.predict(X)[0]
        return float(max(0.0, y))

# instância única
MODEL = DeliveryTimeModel()
