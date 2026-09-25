import random
import sqlite3

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


FALLBACKS = [
    "I do not have a good answer for that yet. Could you rephrase your question?",
    "I am still learning about that topic. Try asking about our hours, location, or services.",
]
GREETINGS = {
    "hi": "Hello! I am Emerspark Assistant. How can I help you?",
    "hello": "Hello! I am Emerspark Assistant. How can I help you?",
    "hey": "Hi! I am Emerspark Assistant. What would you like to know?",
}


class RetrievalEngine:
    def __init__(self, database_path, threshold=0.2):
        self.database_path = database_path
        self.threshold = threshold
        self.reload()

    def reload(self):
        connection = sqlite3.connect(self.database_path)
        rows = connection.execute("SELECT question, answer FROM knowledge_base ORDER BY id").fetchall()
        connection.close()
        self.questions = [row[0] for row in rows]
        self.answers = [row[1] for row in rows]
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words="english")
        self.matrix = self.vectorizer.fit_transform(self.questions) if self.questions else None

    def respond(self, message):
        normalized_message = message.lower().strip().rstrip("!?.,")
        if normalized_message in GREETINGS:
            return GREETINGS[normalized_message], 1.0
        if self.matrix is None:
            return random.choice(FALLBACKS), 0.0
        query_vector = self.vectorizer.transform([message])
        scores = cosine_similarity(query_vector, self.matrix)[0]
        best_index = scores.argmax()
        best_score = float(scores[best_index])
        if best_score < self.threshold:
            return random.choice(FALLBACKS), best_score
        return self.answers[best_index], best_score
