import csv
import re
import pandas as pd
import nltk
nltk.download('vader_lexicon', quiet=True)
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import plotly.express as px
import plotly.graph_objects as go
from colorama import Fore, Style
from typing import Dict
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

def extract_video_id(youtube_link):
    video_id_regex = r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(video_id_regex, youtube_link)
    if match:
        video_id = match.group(1)
        return video_id
    else:
        return None

def preprocess_text_basic(text):
    """Basic text preprocessing for better sentiment analysis"""
    if not text or pd.isna(text):
        return ""
    
    # Convert to string and strip whitespace
    text = str(text).strip()
    
    # Basic emoji replacement (common ones)
    emoji_dict = {
        '😊': 'happy', '😀': 'happy', '😃': 'happy', '😄': 'happy', '😁': 'happy',
        '😍': 'love', '🥰': 'love', '😘': 'love', '💕': 'love', '❤️': 'love',
        '😢': 'sad', '😭': 'crying', '😞': 'sad', '☹️': 'sad',
        '😠': 'angry', '😡': 'angry', '🤬': 'angry', '😤': 'angry',
        '👍': 'good', '👌': 'good', '✅': 'good', '💯': 'perfect',
        '👎': 'bad', '❌': 'bad', '💩': 'bad'
    }
    
    for emoji, word in emoji_dict.items():
        text = text.replace(emoji, f' {word} ')
    
    # Clean up common social media artifacts
    text = re.sub(r'@\w+', '', text)  # Remove mentions
    text = re.sub(r'#\w+', '', text)  # Remove hashtags
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    
    return text.strip()

def analyze_sentiment(csv_file):
    """Lightweight sentiment analysis using only NLTK VADER"""
    
    # Initialize the sentiment analyzer (lightweight)
    sid = SentimentIntensityAnalyzer()
    st.success("✅ Using lightweight VADER sentiment analysis (fast & efficient)")
    
    # Read in the YouTube comments from the CSV file
    comments = []
    with open(csv_file, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            comments.append(row['Comment'])
    
    # Initialize counters
    num_neutral = 0
    num_positive = 0
    num_negative = 0
    confidence_scores = []
    processed_comments = 0
    
    # Progress bar for sentiment analysis
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Analyze each comment
    for i, comment in enumerate(comments):
        # Update progress
        progress = (i + 1) / len(comments)
        progress_bar.progress(progress)
        status_text.text(f"Analyzing comment {i+1}/{len(comments)} with VADER...")
        
        # Preprocess comment
        processed_comment = preprocess_text_basic(comment)
        
        # Analyze sentiment with VADER
        sentiment_scores = sid.polarity_scores(processed_comment)
        compound = sentiment_scores['compound']
        
        # Classify sentiment
        if compound >= 0.05:
            num_positive += 1
            confidence_scores.append(abs(compound))
        elif compound <= -0.05:
            num_negative += 1
            confidence_scores.append(abs(compound))
        else:
            num_neutral += 1
            confidence_scores.append(1 - abs(compound))
        
        processed_comments += 1
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    # Calculate average confidence
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    
    # Display analysis statistics
    st.success(f"✅ Analyzed {processed_comments} comments with {avg_confidence:.2f} average confidence")
    st.info(f"🚀 Analysis method: Lightweight VADER (fast, no heavy downloads)")
    
    # Return the results as a dictionary
    results = {
        'num_neutral': num_neutral, 
        'num_positive': num_positive, 
        'num_negative': num_negative,
        'avg_confidence': avg_confidence,
        'total_comments': len(comments)
    }
    return results

def bar_chart(csv_file: str) -> None:
    # Call analyze_sentiment function to get the results
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # Get the counts for each sentiment category
    num_neutral = results['num_neutral']
    num_positive = results['num_positive']
    num_negative = results['num_negative']

    # Create a Pandas DataFrame with the results
    df = pd.DataFrame({
        'Sentiment': ['Positive', 'Negative', 'Neutral'],
        'Number of Comments': [num_positive, num_negative, num_neutral]
    })

    # Create the enhanced bar chart using Plotly Express with glassmorphism styling
    fig = px.bar(df, x='Sentiment', y='Number of Comments', 
                 color='Sentiment',
                 color_discrete_map={
                     'Positive': 'rgba(16, 185, 129, 0.8)',
                     'Negative': 'rgba(239, 68, 68, 0.8)',
                     'Neutral': 'rgba(107, 114, 128, 0.8)'
                 },
                 title='')
    
    # Update layout for glassmorphism theme
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', family='Inter, sans-serif', size=12),
        title=dict(
            text='📊 Lightweight Sentiment Analysis',
            x=0.5,
            font=dict(size=20, color='white')
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=True,
            tickfont=dict(color='rgba(255,255,255,0.8)')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=False,
            showline=False,
            showticklabels=True,
            tickfont=dict(color='rgba(255,255,255,0.8)')
        ),
        showlegend=False,
        margin=dict(l=0, r=0, t=50, b=0),
        height=400
    )
    
    # Update traces for better styling
    fig.update_traces(
        marker=dict(
            line=dict(color='rgba(255,255,255,0.3)', width=2)
        ),
        hovertemplate='<b>%{x}</b><br>Comments: %{y}<extra></extra>'
    )

    # Show the chart
    st.plotly_chart(fig, use_container_width=True)    
    
def plot_sentiment(csv_file: str) -> None:
    # Call analyze_sentiment function to get the results
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # Get the counts for each sentiment category
    num_neutral = results['num_neutral']
    num_positive = results['num_positive']
    num_negative = results['num_negative']

    # Create enhanced pie chart with glassmorphism styling
    labels = ['Positive', 'Negative', 'Neutral']
    values = [num_positive, num_negative, num_neutral]
    colors = ['rgba(16, 185, 129, 0.8)', 'rgba(239, 68, 68, 0.8)', 'rgba(107, 114, 128, 0.8)']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        textinfo='label+percent',
        textfont=dict(color='white', size=14, family='Inter, sans-serif'),
        marker=dict(
            colors=colors,
            line=dict(color='rgba(255,255,255,0.3)', width=3)
        ),
        hovertemplate='<b>%{label}</b><br>Comments: %{value}<br>Percentage: %{percent}<extra></extra>',
        hole=0.4  # Creates a donut chart for modern look
    )])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', family='Inter, sans-serif'),
        title=dict(
            text='🥧 Fast Sentiment Breakdown',
            x=0.5,
            font=dict(size=20, color='white')
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            font=dict(color='rgba(255,255,255,0.8)')
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=400
    )
    
    # Add center text for donut chart
    fig.add_annotation(
        text=f"<b>Total</b><br>{sum(values)}<br>Comments",
        x=0.5, y=0.5,
        font=dict(size=16, color='white'),
        showarrow=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def print_sentiment(csv_file: str) -> None:
    # Call analyze_sentiment function to get the results
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # Get the counts for each sentiment category
    num_neutral = results['num_neutral']
    num_positive = results['num_positive']
    num_negative = results['num_negative']

    # Determine the overall sentiment
    if num_positive > num_negative:
        overall_sentiment = 'POSITIVE'
        color = Fore.GREEN
    elif num_negative > num_positive:
        overall_sentiment = 'NEGATIVE'
        color = Fore.RED
    else:
        overall_sentiment = 'NEUTRAL'
        color = Fore.YELLOW

    # Print the overall sentiment in color
    print('\n'+ Style.BRIGHT+ color + overall_sentiment.upper().center(50, ' ') + Style.RESET_ALL) 