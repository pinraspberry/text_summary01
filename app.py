from flask import Flask, render_template, request
from text_summary import summarizer
import os

app = Flask(__name__)
# app.run(host='0.0.0.0', port=5000)

# Ensure static/images directory exists
if not os.path.exists('static/images'):
    os.makedirs('static/images')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyse', methods=['GET', 'POST'])
def analyse():
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        # Get summary ratio from form, default to 0.3 if not provided
        try:
            summary_ratio = float(request.form.get('summary_ratio', 0.3))
            # Ensure ratio is between 0.1 and 0.7
            summary_ratio = max(0.1, min(summary_ratio, 0.7))
        except ValueError:
            summary_ratio = 0.3

        # Check if text is empty or too short
        if not rawtext.strip():
            return render_template('index.html', error="No Text Found")
        
        # Check word count before attempting summarization
        word_count = len(rawtext.split())
        
        if word_count < 20:  # Adjust this threshold as needed
            return render_template('index.html', error="No Text Found")
        
        summary, orgtext, len_orgtext, len_sum, keywords, wordcloud_path = summarizer(rawtext, summary_ratio)
    return render_template('summary.html', 
                           summary=summary, 
                           orgtext=orgtext, 
                           len_orgtext=len_orgtext, 
                           len_sum=len_sum,
                           summary_ratio=summary_ratio,
                           keywords=keywords,
                           wordcloud_path=wordcloud_path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)