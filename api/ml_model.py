from sklearn.linear_model import LinearRegression
import numpy as np

class DeliveryTimePredictor:
    """Modelo ML simples para prever tempo de entrega baseado na distância."""
    def __init__(self):
        self.model = LinearRegression()
        X = np.array([[1], [5], [10], [20], [30]])
        y = np.array([5, 15, 25, 45, 60])  # minutos simulados
        self.model.fit(X, y)

    def predict(self, distance_km):
        return float(self.model.predict([[distance_km]])[0])
