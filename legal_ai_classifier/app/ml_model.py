import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.joblib')
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_legal_data.csv')

def train_and_save_model():
    print("Loading data...")
    # Read the dataset
    df = pd.read_csv(DATA_PATH)
    
    # Create a simple NLP pipeline: TF-IDF followed by Naive Bayes
    print("Training model...")
    model = make_pipeline(
        TfidfVectorizer(stop_words='english'),
        MultinomialNB()
    )
    
    # Train the model
    model.fit(df['text'], df['category'])
    
    # Save the model
    print(f"Saving model to {MODEL_PATH}...")
    joblib.dump(model, MODEL_PATH)
    print("Model trained and saved successfully.")

def load_model():
    if not os.path.exists(MODEL_PATH):
        print("Model not found. Training a new one...")
        train_and_save_model()
    return joblib.load(MODEL_PATH)

if __name__ == "__main__":
    train_and_save_model()
