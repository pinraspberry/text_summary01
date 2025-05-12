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

text = " Matt told her to reach for the stars, but Veronica thought it was the most ridiculous advice she'd ever received. Sure, it had been well-meaning when he said it, but she" \
" didn't understand why anyone would want to suggest something that would literally kill you if you actually managed to achieve it. They decided to find the end of the rainbow. " \
"While they hoped they would find a pot of gold, neither of them truly believed that the mythical pot would actually be there. Nor did they believe they could actually find the end "\
"of the rainbow. Still, it seemed like a fun activity for the day, and pictures of them chasing rainbows would look great on their Instagram accounts. They would have never believed "\
"they would actually find the end of a rainbow, and when they did, what they actually found there. Sarah watched the whirlpool mesmerized. She couldn't take her eyes off the water "\
"swirling around and around. She stuck in small twigs and leaves to watch the whirlpool catch them and then suck them down. It bothered her more than a little bit that this could "\
"also be used as a metaphor for her life. It was difficult to explain to them how the diagnosis of certain death had actually given him life. While everyone around him was in "\
"tears and upset, he actually felt more at ease. The doctor said it would be less than a year. That gave him a year to live, something he'd failed to do with his daily drudgery "\
"of a routine that had passed as life until then. They had always called it the green river. It made sense. The river was green. The river likely had a different official name, "\
"but to everyone in town, it was and had always been the green river. So it was with great surprise that on this day the green river was a fluorescent pink."


def summarizer(rawdocs, summary_ratio=0.3):
    summary_ratio = max(0.1, min(summary_ratio, 0.7))  # Limit between 10% and 70%
    
    # Check minimum word count
    word_count = len(rawdocs.split())
    if word_count < 20:  # Adjust this threshold as needed
        return "", rawdocs, word_count, 0

    stopwords=list(STOP_WORDS)
    # print(stopwords)
    nlp = spacy.load('en_core_web_sm')
    doc=nlp(rawdocs)
    # print(doc)
    tokens= [token.text for token in doc]
    word_freq = {}
    for word in doc:
        if word.text.lower() not in stopwords and word.text.lower() not in punctuation:
            if word.text not in word_freq.keys():
                word_freq[word.text] = 1
            else:
                word_freq[word.text] += 1

    # print(word_freq)

    max_freq=max(word_freq.values())
    # print(max_freq)

    for word in word_freq:
        word_freq[word]/=max_freq
    # print(word_freq)

    sent_tokens= [sent for sent in doc.sents]
    # print(sent_tokens)

    #sentence frquency 
    sent_score = {}
    for sent in sent_tokens:
        for word in sent:
            if word.text in word_freq.keys():
                if sent not in sent_score.keys():
                    sent_score[sent] = word_freq[word.text]
                else:
                    sent_score[sent] += word_freq[word.text]

    # print(sent_score)

    # Dynamic selection length based on ratio
    select_length = max(1, int(len(sent_tokens) * summary_ratio))

    # print(select_length)

    #selected select_length amount of sentences from sent_score
    summary = nlargest(select_length , sent_score, key=sent_score.get)
    # print(summary)

    final_summary = [word.text for word in summary]
    summary = " ".join(final_summary)
    # print(summary)

    original_len = len(rawdocs.split(" "))
    summary_len = len(summary.split(" ")) 

    # print(f"{summary}, {rawdocs}, {orginal_len}, {summary_len}")
    #print(summary)
    
    wordcloud_path = generate_wordcloud(rawdocs)
    
    # Extract top keywords
    keywords = extract_keywords(rawdocs)
    
    return summary_text, rawdocs, original_len, summary_len, keywords, wordcloud_path


def __main__():
    summarizer(text)
    # print(f"{summary}, ")
