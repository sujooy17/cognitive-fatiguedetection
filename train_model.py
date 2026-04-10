import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

def train_and_save_model():
    print("Loading dataset...")
    df = pd.read_csv(r'C:\PFSD PROJECT\cognitive-fatigue-detection\dataset.csv')
    
    # Features: typing_speed, error_rate, keypress_interval, session_time
    # Target: fatigue
    X = df[['typing_speed', 'error_rate', 'keypress_interval', 'session_time']]
    y = df['fatigue']
    
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save the model
    # Ensure models directory exists
    os.makedirs('app/models', exist_ok=True)
    model_path = 'app/models/model.pkl'
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
        
    print(f"Model saved successfully to {model_path}")

if __name__ == '__main__':
    train_and_save_model()
