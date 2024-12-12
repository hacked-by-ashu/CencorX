import socket
import threading
import re
from tkinter import *
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import nltk
import string
from nltk.corpus import stopwords
import joblib


try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
stopword = set(stopwords.words("english"))


print("Training the classifier...")
df = pd.read_csv("twitter_data.csv")
df['labels'] = df['class'].map({0: "hate speech detected", 1: "offensive language detected", 3: "no hate and offensive speech"})
df = df.dropna(subset=['labels'])
df = df[['tweet', 'labels']]

def clean(text):
    text = str(text).lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'https?://\s+|www\.\s+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub(r'[{}]'.format(re.escape(string.punctuation)), '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    text = [word for word in text.split() if word not in stopword]
    text = " ".join(text)
    return text

df["tweet"] = df["tweet"].apply(clean)
x = np.array(df["tweet"])
y = np.array(df["labels"])

cv = CountVectorizer()
x = cv.fit_transform(x)
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)
clf = DecisionTreeClassifier()
clf.fit(x_train, y_train)


joblib.dump(clf, 'hate_speech_model.pkl')
joblib.dump(cv, 'vectorizer.pkl')
print("Classifier training complete. Model and vectorizer saved.")

def filter_and_classify(message, bad_word_list):
    """
    Replaces profanity in the given text with asterisks and classifies the text.
    """
    # yahan par Replace bad words with ****
    pattern = r'\b(?:' + '|'.join(bad_word_list) + r')\b'
    filtered_message = re.sub(pattern, lambda match: '*' * len(match.group()), message, flags=re.IGNORECASE)

    cleaned_message = clean(message)
    transformed_message = cv.transform([cleaned_message]).toarray()

    if hasattr(clf, "predict_proba"):
        probabilities = clf.predict_proba(transformed_message)[0]
        max_prob = max(probabilities)
        if max_prob < 0.6:  
            classification = "neutral"
        else:
            classification = clf.classes_[np.argmax(probabilities)]
    else:
        classification = clf.predict(transformed_message)[0]

    return filtered_message, classification


def load_bad_words(file_path):
    """
    Loads the list of bad words from a file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            bad_words = [line.strip() for line in file]
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as file:
            bad_words = [line.strip() for line in file]
    return bad_words

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def handle_client(client_socket, addr):
        
        bad_words_file = 'bad_words.txt'
        bad_words = load_bad_words(bad_words_file)

        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    
                    filtered_message, classification = filter_and_classify(message, bad_words)

                    
                    chat_log.config(state='normal')
                    chat_log.insert('end', f"{addr[0]}: {filtered_message} ({classification})\n")
                    chat_log.config(state='disabled')
                    chat_log.see('end')

                    for conn in clients:
                        if conn != client_socket:
                            conn.sendall(f"{filtered_message} ({classification})".encode())
                else:
                    break
            except Exception as e:
                print(f"Error: {e}")
                break
        client_socket.close()
        clients.remove(client_socket)
        print(f"Disconnected from {addr}")

    def accept_connections():
        while True:
            client_socket, addr = server.accept()
            print(f"Connected to {addr}")
            clients.append(client_socket)
            threading.Thread(target=handle_client, args=(client_socket, addr)).start()

    port = int(port_entry.get())
    server.bind(('0.0.0.0', port))
    server.listen(5)
    threading.Thread(target=accept_connections, daemon=True).start()
    chat_log.config(state='normal')
    chat_log.insert('end', "Server started, waiting for connections...\n")
    chat_log.config(state='disabled')


root = Tk()
root.title("Receiver")

port_label = Label(root, text="Port:")
port_label.pack()
port_entry = Entry(root)
port_entry.pack()
start_button = Button(root, text="Start Server", command=start_server)
start_button.pack()

chat_log = Text(root, state='disabled', height=20, width=50)
chat_log.pack()


clients = []

root.mainloop()
