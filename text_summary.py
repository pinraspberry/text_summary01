#extractive summarizer

import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import base64
from io import BytesIO
import os

def generate_wordcloud(text):
    """Generate a word cloud image from text"""
    # Create a directory to save the image if it doesn't exist
    if not os.path.exists('static/images'):
        os.makedirs('static/images')
    
    # Create stopwords set
    stopwords = list(STOP_WORDS)
    
    # Generate word cloud
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        colormap='viridis',
        max_words=100,
        stopwords=stopwords,
        contour_width=3,
        contour_color='steelblue'
    ).generate(text)
    
    # Save image to a file
    wordcloud_path = 'static/images/wordcloud.png'
    wordcloud.to_file(wordcloud_path)
    
    return wordcloud_path

def extract_keywords(text, max_keywords=10):
    """Extract top keywords from text based on frequency"""
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    
    # Get word frequencies, excluding stopwords and punctuation
    word_freq = {}
    stopwords = list(STOP_WORDS)
    
    for word in doc:
        if word.text.lower() not in stopwords and word.text.lower() not in punctuation:
            if word.text.isalpha() and len(word.text) > 1:
                if word.text.lower() not in word_freq:
                    word_freq[word.text.lower()] = 1
                else:
                    word_freq[word.text.lower()] += 1
    
    # Get top keywords by frequency
    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:max_keywords]
    
    return keywords

def summarizer(rawdocs, summary_ratio=0.3):
    # Validate summary ratio
    summary_ratio = max(0.1, min(summary_ratio, 0.7))  # Limit between 10% and 70%
    
    # Check minimum word count
    word_count = len(rawdocs.split())
    if word_count < 20:  # Adjust this threshold as needed
        return "", rawdocs, word_count, 0, [], ""

    stopwords = list(STOP_WORDS)
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(rawdocs)
    
    tokens = [token.text for token in doc]
    word_freq = {}
    for word in doc:
        if word.text.lower() not in stopwords and word.text.lower() not in punctuation:
            if word.text not in word_freq.keys():
                word_freq[word.text] = 1
            else:
                word_freq[word.text] += 1

    max_freq = max(word_freq.values()) if word_freq else 1

    for word in word_freq:
        word_freq[word] /= max_freq

    sent_tokens = [sent for sent in doc.sents]

    # sentence frequency 
    sent_score = {}
    for sent in sent_tokens:
        for word in sent:
            if word.text in word_freq.keys():
                if sent not in sent_score.keys():
                    sent_score[sent] = word_freq[word.text]
                else:
                    sent_score[sent] += word_freq[word.text]

    # Dynamic selection length based on ratio
    select_length = max(1, int(len(sent_tokens) * summary_ratio))

    # select sentences from sent_score
    summary = nlargest(select_length, sent_score, key=sent_score.get)

    final_summary = [word.text for word in summary]
    summary_text = " ".join(final_summary)

    original_len = len(rawdocs.split())
    summary_len = len(summary_text.split())
    
    # Generate word cloud
    wordcloud_path = generate_wordcloud(rawdocs)
    
    # Extract top keywords
    keywords = extract_keywords(rawdocs)
    
    return summary_text, rawdocs, original_len, summary_len, keywords, wordcloud_path

def __main__():
    # Example usage with default and custom ratios
    text = "Your sample text here..."
    default_summary = summarizer(text)  # Uses default 30% ratio
    custom_summary = summarizer(text, summary_ratio=0.5)  # Uses 50% ratio