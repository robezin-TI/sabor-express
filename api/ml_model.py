from sklearn.linear_model import LinearRegression
import numpy as np

model = None

def train_model(features, targets):
    global model
    X = np.array(features)
    y = np.array(targets)
    model = LinearRegression()
    model.fit(X, y)
    return {"coef": model.coef_.tolist(), "intercept": model.intercept_.tolist()}

def predict_sales(features):
    global model
    if model is None:
        return "Modelo não treinado!"
    X = np.array([features])
    return model.predict(X).tolist()[0]
