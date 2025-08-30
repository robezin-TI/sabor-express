import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import os

MODEL_PATH = "model.pkl"

def train_model():
    # Dados fake de treino
    X = np.array([[1], [2], [3], [4], [5]])
    y = np.array([100, 180, 260, 320, 400])

    model = LinearRegression()
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    return model

def predict(value):
    if not os.path.exists(MODEL_PATH):
        model = train_model()
    else:
        model = joblib.load(MODEL_PATH)
    return model.predict(np.array([[value]])).tolist()
