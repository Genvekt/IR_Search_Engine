import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')


def normalize(text):
    # Replace all symbols that are not letters and not * with space.
    t1 = re.sub(r"[^a-zA-z *]+", ' ', text.lower())
    # Replace many spaces with one
    t2 = re.sub(r"[\s]+", ' ', t1)
    return t2


def tokenize(text):
    return nltk.word_tokenize(text)


def lemmatization(tokens):
    lemmatizer = WordNetLemmatizer()
    res = [lemmatizer.lemmatize(t) for t in tokens]
    return res


def remove_stop_words(tokens):
    stop_words = set(stopwords.words('english'))
    filtered_sentence = [t for t in tokens if not t in stop_words]
    return filtered_sentence


def preprocess(text, lemmatize=True, without_stop_words=True):
    text = normalize(text)
    clear_text = tokenize(text)
    if lemmatize:
        clear_text = lemmatization(clear_text)
    if without_stop_words:
        clear_text = remove_stop_words(clear_text)
    return clear_text
