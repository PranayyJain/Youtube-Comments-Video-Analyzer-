import csv
import re
import pandas as pd
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import plotly.express as px
import plotly.graph_objects as go
from colorama import Fore, Style
from typing import Dict
import streamlit as st
import emoji
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
import warnings
warnings.filterwarnings('ignore')

# Try to import translation, but make it optional
try:
    from googletrans import Translator
    TRANSLATION_AVAILABLE = True
except ImportError as e:
    TRANSLATION_AVAILABLE = False
    st.warning("⚠️ Translation features disabled due to Python 3.13 compatibility. Using English-only analysis.")

# Initialize advanced sentiment models
@st.cache_resource
def load_sentiment_models():
    """Load and cache sentiment analysis models"""
    models = {}
    
    try:
        # Multilingual sentiment model (works with multiple languages)
        models['multilingual'] = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment",
            tokenizer="nlptown/bert-base-multilingual-uncased-sentiment",
            device=0 if torch.cuda.is_available() else -1
        )
        st.success("✅ Multilingual sentiment model loaded successfully!")
    except Exception as e:
        st.warning(f"⚠️ Multilingual model failed to load: {str(e)}")
        models['multilingual'] = None
    
    try:
        # Social media optimized model (better for YouTube comments)
        models['social'] = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest",
            device=0 if torch.cuda.is_available() else -1
        )
        st.success("✅ Social media sentiment model loaded successfully!")
    except Exception as e:
        st.warning(f"⚠️ Social media model failed to load: {str(e)}")
        models['social'] = None
    
    # Fallback to VADER
    models['vader'] = SentimentIntensityAnalyzer()
    
    # Show translation status
    if TRANSLATION_AVAILABLE:
        st.success("✅ Translation features enabled for multilingual support!")
    else:
        st.info("ℹ️ Running in English-only mode (Python 3.13 compatibility)")
    
    return models

def preprocess_text(text):
    """Advanced text preprocessing for better sentiment analysis"""
    if not text or pd.isna(text):
        return ""
    
    # Convert to string and strip whitespace
    text = str(text).strip()
    
    # Convert emoji to text description for better analysis
    text = emoji.demojize(text, language='en')
    
    # Clean up common social media artifacts
    text = re.sub(r'@\w+', '', text)  # Remove mentions
    text = re.sub(r'#\w+', '', text)  # Remove hashtags
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    
    return text.strip()

def detect_language(text):
    """Detect the language of the text"""
    try:
        return detect(text)
    except (LangDetectException, Exception):
        return 'en'  # Default to English

def translate_text(text, target_lang='en'):
    """Translate text to target language"""
    if not TRANSLATION_AVAILABLE:
        return text  # Return original text if translation not available
    
    try:
        if len(text.strip()) == 0:
            return text
        
        translator = Translator()
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        st.warning(f"Translation failed: {str(e)}")
        return text

def analyze_sentiment_advanced(text, models):
    """Advanced sentiment analysis with multiple models"""
    if not text or len(text.strip()) == 0:
        return {'sentiment': 'neutral', 'confidence': 0.0, 'method': 'empty'}
    
    # Preprocess the text
    processed_text = preprocess_text(text)
    
    # Detect language
    lang = detect_language(processed_text)
    
    # If text is too short, use VADER
    if len(processed_text.split()) < 2:
        return analyze_with_vader(processed_text, models['vader'])
    
    # Try multilingual model first
    if models['multilingual'] is not None:
        try:
            result = models['multilingual'](processed_text)
            if result:
                sentiment = result[0]['label'].lower()
                confidence = result[0]['score']
                
                # Map multilingual model output to standard format
                if 'positive' in sentiment or sentiment in ['pos', '4 stars', '5 stars']:
                    return {'sentiment': 'positive', 'confidence': confidence, 'method': 'multilingual', 'language': lang}
                elif 'negative' in sentiment or sentiment in ['neg', '1 star', '2 stars']:
                    return {'sentiment': 'negative', 'confidence': confidence, 'method': 'multilingual', 'language': lang}
                else:
                    return {'sentiment': 'neutral', 'confidence': confidence, 'method': 'multilingual', 'language': lang}
        except Exception as e:
            st.warning(f"Multilingual model error: {str(e)}")
    
    # Try social media model for English text
    if lang == 'en' and models['social'] is not None:
        try:
            result = models['social'](processed_text)
            if result:
                sentiment = result[0]['label'].lower()
                confidence = result[0]['score']
                
                # Map social media model output
                if 'positive' in sentiment:
                    return {'sentiment': 'positive', 'confidence': confidence, 'method': 'social', 'language': lang}
                elif 'negative' in sentiment:
                    return {'sentiment': 'negative', 'confidence': confidence, 'method': 'social', 'language': lang}
                else:
                    return {'sentiment': 'neutral', 'confidence': confidence, 'method': 'social', 'language': lang}
        except Exception as e:
            st.warning(f"Social media model error: {str(e)}")
    
    # For non-English text, try translation + social model (only if translation available)
    if lang != 'en' and models['social'] is not None and TRANSLATION_AVAILABLE:
        try:
            translated_text = translate_text(processed_text, 'en')
            result = models['social'](translated_text)
            if result:
                sentiment = result[0]['label'].lower()
                confidence = result[0]['score'] * 0.8  # Reduce confidence due to translation
                
                if 'positive' in sentiment:
                    return {'sentiment': 'positive', 'confidence': confidence, 'method': 'translated+social', 'language': lang}
                elif 'negative' in sentiment:
                    return {'sentiment': 'negative', 'confidence': confidence, 'method': 'translated+social', 'language': lang}
                else:
                    return {'sentiment': 'neutral', 'confidence': confidence, 'method': 'translated+social', 'language': lang}
        except Exception as e:
            st.warning(f"Translation + social model error: {str(e)}")
    
    # Fallback to VADER
    return analyze_with_vader(processed_text, models['vader'])

def analyze_with_vader(text, vader_analyzer):
    """Fallback VADER analysis"""
    try:
        sentiment_scores = vader_analyzer.polarity_scores(text)
        compound = sentiment_scores['compound']
        
        if compound >= 0.05:
            return {'sentiment': 'positive', 'confidence': abs(compound), 'method': 'vader', 'language': 'en'}
        elif compound <= -0.05:
            return {'sentiment': 'negative', 'confidence': abs(compound), 'method': 'vader', 'language': 'en'}
        else:
            return {'sentiment': 'neutral', 'confidence': 1 - abs(compound), 'method': 'vader', 'language': 'en'}
    except Exception:
        return {'sentiment': 'neutral', 'confidence': 0.0, 'method': 'error', 'language': 'unknown'}

def extract_video_id(youtube_link):
    video_id_regex = r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(video_id_regex, youtube_link)
    if match:
        video_id = match.group(1)
        return video_id
    else:
        return None

def analyze_sentiment(csv_file):
    """Enhanced sentiment analysis with advanced NLP models"""
    
    # Load models
    with st.spinner("🤖 Loading advanced AI models..."):
        models = load_sentiment_models()
    
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
    language_stats = {}
    method_stats = {}
    
    # Progress bar for sentiment analysis
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Analyze each comment
    for i, comment in enumerate(comments):
        # Update progress
        progress = (i + 1) / len(comments)
        progress_bar.progress(progress)
        status_text.text(f"Analyzing comment {i+1}/{len(comments)} using advanced AI...")
        
        # Analyze sentiment
        result = analyze_sentiment_advanced(comment, models)
        
        # Count sentiments
        if result['sentiment'] == 'positive':
            num_positive += 1
        elif result['sentiment'] == 'negative':
            num_negative += 1
        else:
            num_neutral += 1
        
        # Track statistics
        confidence_scores.append(result['confidence'])
        
        # Language statistics
        lang = result.get('language', 'unknown')
        language_stats[lang] = language_stats.get(lang, 0) + 1
        
        # Method statistics
        method = result.get('method', 'unknown')
        method_stats[method] = method_stats.get(method, 0) + 1
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    # Calculate average confidence
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    
    # Display analysis statistics
    st.success(f"✅ Analyzed {len(comments)} comments with {avg_confidence:.2f} average confidence")
    
    # Display language distribution
    if language_stats:
        st.info(f"🌐 Languages detected: {', '.join([f'{lang}: {count}' for lang, count in language_stats.items() if count > 0])}")
    
    # Display method distribution  
    if method_stats:
        st.info(f"🔧 Analysis methods: {', '.join([f'{method}: {count}' for method, count in method_stats.items() if count > 0])}")
    
    # Return the results as a dictionary
    results = {
        'num_neutral': num_neutral, 
        'num_positive': num_positive, 
        'num_negative': num_negative,
        'avg_confidence': avg_confidence,
        'language_stats': language_stats,
        'method_stats': method_stats,
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
            text='📊 Advanced AI Sentiment Analysis',
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
            text='🥧 Multilingual Sentiment Breakdown',
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
    
def create_scatterplot(csv_file: str, x_column: str, y_column: str) -> None:
    # Load data from CSV
    data = pd.read_csv(csv_file)

    # Create enhanced scatter plot using Plotly with glassmorphism styling
    fig = px.scatter(data, x=x_column, y=y_column, color='Category',
                     color_discrete_sequence=['rgba(16, 185, 129, 0.8)', 'rgba(239, 68, 68, 0.8)', 'rgba(107, 114, 128, 0.8)'])

    # Update layout for glassmorphism theme
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', family='Inter, sans-serif', size=12),
        title=dict(
            text='📈 Scatter Plot Analysis',
            x=0.5,
            font=dict(size=20, color='white')
        ),
        xaxis=dict(
            title=x_column,
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=False,
            showline=False,
            tickfont=dict(color='rgba(255,255,255,0.8)')
        ),
        yaxis=dict(
            title=y_column,
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=False,
            showline=False,
            tickfont=dict(color='rgba(255,255,255,0.8)')
        ),
        legend=dict(
            font=dict(color='rgba(255,255,255,0.8)')
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=400
    )
    
    # Update traces for better styling
    fig.update_traces(
        marker=dict(
            size=8,
            line=dict(color='rgba(255,255,255,0.3)', width=1)
        )
    )

    # Display plot in Streamlit
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



