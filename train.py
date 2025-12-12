import os
import numpy as np
from PIL import Image
from model import build_model, save_model

# Configuration
DATA_DIR = '../data'
IMG_HEIGHT = 64 # Reduced for MLP performance
IMG_WIDTH = 64
MODEL_SAVE_PATH = 'signature_model.pkl'

def load_images_from_folder(folder, label):
    images = []
    labels = []
    if not os.path.exists(folder):
        return [], []
        
    for filename in os.listdir(folder):
        try:
            img_path = os.path.join(folder, filename)
            img = Image.open(img_path).convert('L') # Convert to Grayscale
            img = img.resize((IMG_WIDTH, IMG_HEIGHT))
            img_array = np.array(img).flatten() # Flatten 2D image to 1D vector
            images.append(img_array)
            labels.append(label)
        except Exception as e:
            print(f"Skipping {filename}: {e}")
            
    return images, labels

def train():
    real_dir = os.path.join(DATA_DIR, 'real')
    forged_dir = os.path.join(DATA_DIR, 'forged')
    
    print("Loading data...")
    # Label 1 = Real, 0 = Forged
    real_imgs, real_labels = load_images_from_folder(real_dir, 1)
    forged_imgs, forged_labels = load_images_from_folder(forged_dir, 0)
    
    X = real_imgs + forged_imgs
    y = real_labels + forged_labels
    
    if len(X) == 0:
        print("No data found. Creating a dummy model structure for demo.")
        # Create dummy data to fit the model structure
        X_dummy = np.random.rand(10, IMG_WIDTH * IMG_HEIGHT)
        y_dummy = np.random.randint(0, 2, 10)
        
        model = build_model()
        model.fit(X_dummy, y_dummy)
        save_model(model, MODEL_SAVE_PATH)
        print(f"Dummy model saved to {MODEL_SAVE_PATH}")
        return

    print(f"Training on {len(X)} signatures...")
    X = np.array(X)
    X = X / 255.0 # Normalize
    y = np.array(y)
    
    model = build_model()
    model.fit(X, y)
    
    save_model(model, MODEL_SAVE_PATH)
    print(f"Model trained and saved to {MODEL_SAVE_PATH}")

if __name__ == '__main__':
    train()
