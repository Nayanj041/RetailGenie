import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re
import joblib
import os

class SentimentAnalyzer:
    def __init__(self):
        """
        Initialize the SentimentAnalyzer instance with model, vectorizer, and stemmer attributes, and ensure required NLTK resources are available.
        """
        self.model = None
        self.vectorizer = None
        self.stemmer = PorterStemmer()
        self.setup_nltk()
        
    def setup_nltk(self):
        """
        Ensures that required NLTK data packages for tokenization and stopword removal are available, downloading them if missing.
        """
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
    
    def preprocess_text(self, text):
        """
        Preprocesses input text by cleaning, tokenizing, removing stopwords, and applying stemming.
        
        Returns:
            str: The processed text as a single string of stemmed tokens, or an empty string if input is not a string.
        """
        if not isinstance(text, str):
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and stem
        stop_words = set(stopwords.words('english'))
        tokens = [self.stemmer.stem(token) for token in tokens if token not in stop_words]
        
        return ' '.join(tokens)
    
    def create_sample_data(self):
        """
        Return a pandas DataFrame containing hardcoded sample text data labeled with positive, negative, and neutral sentiments.
        
        Returns:
            DataFrame: Sample data with 'text' and 'sentiment' columns for use in training or testing the sentiment analysis model.
        """
        sample_data = [
            ("Great product, love it!", "positive"),
            ("Amazing quality and fast delivery", "positive"),
            ("Excellent customer service", "positive"),
            ("Perfect for my needs", "positive"),
            ("Highly recommend this product", "positive"),
            ("Best purchase I've made", "positive"),
            ("Outstanding quality", "positive"),
            ("Very satisfied with my order", "positive"),
            ("Terrible product, waste of money", "negative"),
            ("Poor quality, broke immediately", "negative"),
            ("Awful customer service", "negative"),
            ("Not as described, very disappointed", "negative"),
            ("Expensive for what you get", "negative"),
            ("Would not recommend", "negative"),
            ("Defective product", "negative"),
            ("Shipping was delayed", "negative"),
            ("It's okay, nothing special", "neutral"),
            ("Average product", "neutral"),
            ("Decent quality for the price", "neutral"),
            ("Could be better", "neutral"),
            ("Not bad, not great", "neutral"),
            ("Standard product", "neutral"),
            ("Works as expected", "neutral"),
            ("Fair value", "neutral")
        ]
        
        return pd.DataFrame(sample_data, columns=['text', 'sentiment'])
    
    def train_model(self, data=None):
        """
        Train the sentiment analysis model using labeled text data.
        
        If no data is provided, uses a built-in sample dataset. Texts are preprocessed, split into training and test sets, and a pipeline with TF-IDF vectorization and a multinomial Naive Bayes classifier is trained. Prints evaluation metrics and returns the model's accuracy on the test set.
        
        Parameters:
            data (pandas.DataFrame, optional): DataFrame with 'text' and 'sentiment' columns. If None, sample data is used.
        
        Returns:
            float: Accuracy of the trained model on the test set.
        """
        if data is None:
            data = self.create_sample_data()
        
        # Preprocess texts
        data['processed_text'] = data['text'].apply(self.preprocess_text)
        
        # Prepare features and labels
        X = data['processed_text']
        y = data['sentiment']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Create pipeline
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
            ('classifier', MultinomialNB(alpha=0.1))
        ])
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model trained successfully!")
        print(f"Accuracy: {accuracy:.3f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        return accuracy
    
    def predict_sentiment(self, text):
        """
        Predicts the sentiment of a single input text and returns the predicted label, confidence score, and class probabilities.
        
        Parameters:
            text (str): The input text to analyze.
        
        Returns:
            dict: A dictionary containing the predicted sentiment label ('sentiment'), the confidence score ('confidence'), and a nested dictionary of class probabilities for 'negative', 'neutral', and 'positive'.
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train_model() first.")
        
        processed_text = self.preprocess_text(text)
        prediction = self.model.predict([processed_text])[0]
        probabilities = self.model.predict_proba([processed_text])[0]
        
        # Get confidence score
        confidence = max(probabilities)
        
        return {
            'sentiment': prediction,
            'confidence': float(confidence),
            'probabilities': {
                'negative': float(probabilities[0]),
                'neutral': float(probabilities[1]) if len(probabilities) > 2 else 0.0,
                'positive': float(probabilities[1 if len(probabilities) == 2 else 2])
            }
        }
    
    def analyze_feedback_batch(self, feedback_list):
        """
        Analyzes a batch of feedback texts, predicting sentiment and aggregating statistics.
        
        Parameters:
            feedback_list (list of str): List of feedback texts to analyze.
        
        Returns:
            dict: Contains individual prediction results for each text and aggregated statistics, including total feedback count, counts per sentiment, average confidence, and the most frequent sentiment.
        """
        results = []
        for text in feedback_list:
            result = self.predict_sentiment(text)
            result['text'] = text
            results.append(result)
        
        # Calculate overall statistics
        sentiments = [r['sentiment'] for r in results]
        stats = {
            'total_feedback': len(results),
            'positive_count': sentiments.count('positive'),
            'negative_count': sentiments.count('negative'),
            'neutral_count': sentiments.count('neutral'),
            'average_confidence': np.mean([r['confidence'] for r in results]),
            'overall_sentiment': max(set(sentiments), key=sentiments.count)
        }
        
        return {
            'results': results,
            'statistics': stats
        }
    
    def save_model(self, filepath):
        """
        Save the trained sentiment analysis model to the specified file path.
        
        Parameters:
            filepath (str): The destination file path where the model will be saved.
        
        Raises:
            ValueError: If no model has been trained prior to saving.
        """
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.model, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """
        Load a pre-trained sentiment analysis model from the specified file path, or train and save a new model if the file does not exist.
        
        Parameters:
            filepath (str): Path to the model file to load or save.
        """
        if os.path.exists(filepath):
            self.model = joblib.load(filepath)
            print(f"Model loaded from {filepath}")
        else:
            print(f"Model file not found: {filepath}")
            print("Training new model...")
            self.train_model()
            self.save_model(filepath)

# Example usage and testing
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = SentimentAnalyzer()
    
    # Train model
    analyzer.train_model()
    
    # Test predictions
    test_texts = [
        "This product is amazing, I love it!",
        "Terrible quality, waste of money",
        "It's okay, nothing special",
        "Best purchase ever, highly recommend!",
        "Product broke after one day, very disappointed"
    ]
    
    print("\nTesting individual predictions:")
    for text in test_texts:
        result = analyzer.predict_sentiment(text)
        print(f"Text: {text}")
        print(f"Sentiment: {result['sentiment']} (confidence: {result['confidence']:.3f})")
        print("-" * 50)
    
    # Test batch analysis
    print("\nBatch analysis results:")
    batch_results = analyzer.analyze_feedback_batch(test_texts)
    print(f"Overall sentiment: {batch_results['statistics']['overall_sentiment']}")
    print(f"Positive: {batch_results['statistics']['positive_count']}")
    print(f"Negative: {batch_results['statistics']['negative_count']}")
    print(f"Neutral: {batch_results['statistics']['neutral_count']}")
