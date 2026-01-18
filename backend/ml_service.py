import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import pickle
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to script location
MODEL_PATH = os.path.join(SCRIPT_DIR, "doctor_recommender.pkl")
DATA_PATH = os.path.join(SCRIPT_DIR, "training_data.csv")

def train_model():
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: training_data.csv not found at {DATA_PATH}")
        print(f"   Expected location: {DATA_PATH}")
        return False

    try:
        print(f"📚 Loading training data from: {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)
        
        # Create a pipeline that vectorizes text then classifies it
        model = make_pipeline(TfidfVectorizer(), MultinomialNB())
        
        # Train
        print("🤖 Training model...")
        model.fit(df['symptoms'], df['department'])
        
        # Save
        print(f"💾 Saving model to: {MODEL_PATH}")
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        print("✅ Model trained and saved!")
        return True
        
    except Exception as e:
        print(f"❌ Error during model training: {e}")
        return False

def predict_department(text):
    """
    Predicts the department based on symptom text.
    Trains the model if it doesn't exist.
    
    Args:
        text (str): Symptom description
        
    Returns:
        tuple: (department_name, confidence_score)
        
    Raises:
        Exception: If model cannot be trained or loaded
    """
    if not os.path.exists(MODEL_PATH):
        print("🔧 Model not found. Training now...")
        success = train_model()
        if not success:
            raise Exception("Failed to train model. Training data not found.")
    
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
            
        # Returns the predicted department name (e.g., "Cardiology")
        prediction = model.predict([text])[0]
        
        # Get probability/confidence
        probs = model.predict_proba([text]).max()
        
        return prediction, probs
        
    except Exception as e:
        print(f"❌ Error loading/using model: {e}")
        raise


if __name__ == "__main__":
    # 1. Train the model first to ensure it's fresh
    print("Training model...")
    train_model()
    print("\n--- MODEL READY ---")
    print("Type a symptom to test (or 'quit' to exit)")
    print("---------------------------------")

    # 2. Loop to let you test multiple times
    while True:
        user_input = input("\nEnter symptom: ")
        if user_input.lower() == 'quit':
            break
        
        # Predict
        dept, confidence = predict_department(user_input)
        
        print(f"Prediction: {dept}")
        print(f"Confidence: {confidence:.2f}")
