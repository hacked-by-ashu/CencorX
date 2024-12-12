# this project is only for practice purpose the same logic is sused in the receiver script
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text  import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

import re
import nltk
from nltk.util import pr
stemmer = nltk.SnowballStemmer ("english")
from nltk.corpus import stopwords
import string
stopword = set(stopwords.words("english"))

df = pd.read_csv("twitter_data.csv")
#print(df.head())

#dataset ke labels mein jo class hai uske numbers se script identify karegi ki jo text hai woh konse category mein aata hai
df['labels'] = df['class'].map({0:"hate speech detected",1:"offensive language detected",3:"no hate and offensive speech"})
df = df.dropna(subset=['labels'])
df = df[['tweet','labels']]
print(df.head())


#cleaning unwanted things in the dataset - text messages
def clean(text):
    text = str(text).lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'https?://\s+|www\.\s+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub(r'[{}]'.format(re.escape(string.punctuation)), '', text)  # Corrected line
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    text = [word for word in text.split() if word not in stopword]
    text = " ".join(text)
    return text

df["tweet"] = df["tweet"].apply(clean)
print(df.head())

x = np.array(df["tweet"])
y = np.array(df["labels"])

cv = CountVectorizer()
x = cv.fit_transform(x)
x_train, x_test , y_train, y_test = train_test_split(x,y, test_size=0.33, random_state=42)
clf = DecisionTreeClassifier()
clf.fit(x_train,y_train)

test_data= "i will kill you"
df = cv.transform ([test_data]).toarray()
print(clf.predict(df))
