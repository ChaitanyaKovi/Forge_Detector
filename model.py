from sklearn.neural_network import MLPClassifier
import joblib
import os

def build_model():
    """
    Builds a MLP Classifier (Neural Network) for signature verification.
    """
    # Hidden layers: 100 neurons, 50 neurons
    model = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, alpha=1e-4,
                          solver='adam', verbose=10, random_state=1,
                          learning_rate_init=.01)
    return model

def save_model(model, path='signature_model.pkl'):
    joblib.dump(model, path)

def load_trained_model(path='signature_model.pkl'):
    if os.path.exists(path):
        return joblib.load(path)
    return None
