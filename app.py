import os
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from model import load_trained_model, build_model

app = Flask(__name__)
CORS(app)

MODEL_PATH = 'signature_model.pkl'
IMG_HEIGHT = 64
IMG_WIDTH = 64

# Load model globally
model = load_trained_model(MODEL_PATH)
if model is None:
    print("Model not found. Predictions will be random until trained.")
    # Create a temporary dummy model in memory
    model = build_model()
    # Fit with dummy samples (one for each class) so it's initialized
    # Scikit-learn requires at least 2 classes to fit
    dummy_X = np.random.rand(2, IMG_HEIGHT * IMG_WIDTH)
    dummy_y = [0, 1] # 0=Forged, 1=Real
    model.fit(dummy_X, dummy_y)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Save temp file
        img_path = 'temp_upload.png'
        
        try:
            # Check if directory is writeable, etc. or just process directly from stream
            # But PIL Image.open supports stream
            
            img = Image.open(file.stream).convert('L')
            img = img.resize((IMG_WIDTH, IMG_HEIGHT))
            img_array = np.array(img).flatten()
            img_array = img_array.reshape(1, -1)
            img_array = img_array / 255.0

            # Predict
            # Classes are likely [0, 1] -> [Forged, Real]
            prediction = model.predict(img_array)
            probabilities = model.predict_proba(img_array)[0] # [prob_0, prob_1]
            
            predicted_class = prediction[0] # 0 or 1
            confidence = probabilities[predicted_class]
            
            result = "Real" if predicted_class == 1 else "Forged"
            
            return jsonify({
                'result': result,
                'confidence': f"{confidence*100:.2f}%",
                'raw_score': float(confidence)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if os.path.exists(img_path):
                try:
                    os.remove(img_path)
                except:
                    pass

if __name__ == '__main__':
    app.run(debug=True, port=5000)
