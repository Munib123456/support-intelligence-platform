"""
classifier.py
Phase 2: The NLP text classifier.

What this file does, in plain words:
- Reads real complaint text (the CFPB 'narrative' column) and its category ('product_5').
- Turns the text into numbers using TF-IDF (computers can't read words directly).
- Trains a Logistic Regression model to predict the category from the text.
- Tests it on data it has never seen, and prints how accurate it is.
- Saves the trained model to disk so we don't have to retrain every time.
"""

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score


def train_classifier(path="data/complaints.csv", save_to="models/classifier.pkl"):
    # 1. Load the data and keep only the two columns we need.
    df = pd.read_csv(path)
    df = df[["narrative", "product_5"]].dropna()

    X = df["narrative"]      # the complaint text
    y = df["product_5"]      # the category label

    # 2. Split: 80% to train on, 20% held back to test honestly.
    #    'stratify=y' keeps the same category mix in both halves.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 3. Build a pipeline: turn text into TF-IDF numbers, then classify.
    #    - max_features=5000 keeps only the 5000 most useful words (keeps it fast).
    #    - stop_words='english' ignores filler words like "the", "and".
    #    - class_weight='balanced' handles the imbalance (rare categories get fair attention).
    model = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000, stop_words="english")),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])

    # 4. Train.
    print("Training the classifier... (this can take a minute)")
    model.fit(X_train, y_train)

    # 5. Test on the held-back data and print the scores.
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"\nAccuracy on unseen test data: {accuracy:.3f}")
    print("\nDetailed report (precision / recall / f1 per category):")
    print(classification_report(y_test, predictions))

    # 6. Save the trained model to disk.
    joblib.dump(model, save_to)
    print(f"Model saved to {save_to}")

    return model


def predict_category(text, model_path="models/classifier.pkl"):
    """Load the saved model and predict the category of one piece of text."""
    model = joblib.load(model_path)
    return model.predict([text])[0]


if __name__ == "__main__":
    model = train_classifier()

    # Quick hand-test with made-up complaints.
    print("\n--- Hand-test on made-up complaints ---")
    tests = [
        "I was charged twice on my credit card this month",
        "A debt collector keeps calling me about a loan I already paid",
        "My credit report shows an account that is not mine",
    ]
    for t in tests:
        print(f"  '{t[:50]}...' -> {model.predict([t])[0]}")