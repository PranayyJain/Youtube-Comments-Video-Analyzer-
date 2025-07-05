import streamlit as st
import os
import time
from Senti import extract_video_id, analyze_sentiment, bar_chart, plot_sentiment
from YoutubeCommentScrapper import save_video_comments_to_csv, get_channel_info, youtube, get_channel_id, get_video_stats
from file_manager import FileManager

# Get current directory path early
directory_path = os.getcwd()

def delete_non_matching_csv_files(directory_path, video_id):
    """
    Clean up old CSV files with better error handling using FileManager
    """
    deleted_files = []
    locked_files = []
    
    try:
        for file_name in os.listdir(directory_path):
            if not file_name.endswith('.csv'):
                continue
            if file_name == f'{video_id}.csv':
                continue
            if file_name.startswith('temp_') or file_name.startswith('demo_'):
                continue  # Skip temporary and demo files
            
            file_path = os.path.join(directory_path, file_name)
            
            if FileManager.safe_remove_file(file_path):
                deleted_files.append(file_name)
            else:
                locked_files.append(file_name)
    
    except Exception as e:
        st.error(f"❌ Error during file cleanup: {str(e)}")
    
    # Provide feedback
    if deleted_files:
        st.info(f"🧹 Cleaned up {len(deleted_files)} old CSV files")
    if locked_files:
        st.warning(f"⚠️ {len(locked_files)} files are locked (may be open in Excel): {', '.join(locked_files)}")

# Enhanced Page Configuration
st.set_page_config(
    page_title='YouTube Sentiment Pro', 
    page_icon='🎬', 
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "# YouTube Sentiment Analysis Pro\nModern AI-powered sentiment analysis for YouTube comments with stunning glassmorphism UI!"
    }
)

# Custom CSS for Glassmorphism and Modern UI
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Variables */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --youtube-red: #ff0000;
        --glass-bg: rgba(255, 255, 255, 0.1);
        --glass-border: rgba(255, 255, 255, 0.2);
        --dark-glass-bg: rgba(0, 0, 0, 0.1);
        --text-primary: #1a1a1a;
        --text-secondary: #6b7280;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
    }
    
    /* Main Background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 2rem 0;
    }
    
    /* YouTube Logo */
    .youtube-logo {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #ff0000, #cc0000);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem auto;
        box-shadow: 0 6px 20px rgba(255, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    .youtube-logo:hover {
        transform: scale(1.1);
        box-shadow: 0 8px 25px rgba(255, 0, 0, 0.5);
    }
    
    .youtube-logo svg {
        width: 32px;
        height: 32px;
        fill: white;
    }
    
    /* Hero Input Section */
    .hero-input-section {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(25px);
        border-radius: 25px;
        padding: 3rem 2rem;
        margin: 2rem auto;
        max-width: 800px;
        border: 2px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 15px 50px 0 rgba(31, 38, 135, 0.4);
        text-align: center;
    }
    
    .hero-input-title {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        color: white;
        margin-bottom: 1rem;
        text-shadow: 0 3px 6px rgba(0,0,0,0.2);
    }
    
    .hero-input-subtitle {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 2rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Enhanced Input Field */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 20px;
        color: white;
        padding: 1.5rem 2rem;
        font-size: 1.1rem;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        text-align: center;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: rgba(255, 255, 255, 0.5);
        background: rgba(255, 255, 255, 0.25);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
        outline: none;
        transform: translateY(-2px);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.6);
        font-style: italic;
    }
    
    /* Glass Card Effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: all 0.3s ease;
        animation: slideUp 0.6s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px 0 rgba(31, 38, 135, 0.5);
    }
    
    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        transition: all 0.3s ease;
        animation: fadeInUp 0.8s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 0.2);
    }
    
    /* Typography */
    .main-title {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 3.5rem;
        text-align: center;
        background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        text-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }
    
    .section-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.8rem;
        color: white;
        margin-bottom: 1.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .metric-value {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2rem;
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.8);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
    }
    
    /* Channel Info Styling */
    .channel-info {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    
    .channel-logo {
        border-radius: 50%;
        border: 3px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
    }
    
    .channel-logo:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2);
    }
    
    /* Video Container */
    .video-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    
    /* Sentiment Cards */
    .sentiment-positive {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        color: white;
    }
    
    .sentiment-negative {
        background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
        color: white;
    }
    
    .sentiment-neutral {
        background: linear-gradient(135deg, #6b7280 0%, #9ca3af 100%);
        color: white;
    }
    
    /* Animations */
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        font-family: 'Inter', sans-serif;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    /* Success Message */
    .success-message {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    /* Error Message */
    .error-message {
        background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
    }
    
    /* Processing Message */
    .processing-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Features Grid */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.5);
    }
    
    /* Sidebar styling when collapsed */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown('<h1 class="main-title">🎬 YouTube Sentiment Pro</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: rgba(255,255,255,0.8); font-size: 1.3rem; margin-bottom: 3rem;">AI-Powered Comment Analysis with Stunning Insights</p>', unsafe_allow_html=True)

# Center Hero Input Section
st.markdown("""
<div class="hero-input-section">
    <div class="youtube-logo">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M23.498 6.186a2.997 2.997 0 0 0-2.111-2.111C19.505 3.546 12 3.546 12 3.546s-7.505 0-9.387.529A2.997 2.997 0 0 0 .502 6.186C0 8.068 0 12 0 12s0 3.932.502 5.814a2.997 2.997 0 0 0 2.111 2.111C4.495 20.454 12 20.454 12 20.454s7.505 0 9.387-.529a2.997 2.997 0 0 0 2.111-2.111C24 15.932 24 12 24 12s0-3.932-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
        </svg>
    </div>
    <div class="hero-input-title">Enter YouTube URL</div>
    <div class="hero-input-subtitle">Paste any YouTube video URL to analyze its comments with AI</div>
</div>
""", unsafe_allow_html=True)

# Center the input field
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    youtube_link = st.text_input(
        "", 
        placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        help="Paste any YouTube video URL here",
        key="youtube_url_input"
    )

# URL Examples below input
if not youtube_link:
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem;">
        <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border-radius: 15px; padding: 1.5rem; margin: 1rem auto; max-width: 600px; border: 1px solid rgba(255, 255, 255, 0.2);">
            <h4 style="color: rgba(255, 255, 255, 0.9); font-size: 1.1rem; margin-bottom: 1rem; font-weight: 600;">✨ Supported URL formats:</h4>
            <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin: 0.5rem 0; font-family: 'Monaco', monospace;">https://www.youtube.com/watch?v=VIDEO_ID</p>
            <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin: 0.5rem 0; font-family: 'Monaco', monospace;">https://youtu.be/VIDEO_ID</p>
            <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin: 0.5rem 0; font-family: 'Monaco', monospace;">youtube.com/watch?v=VIDEO_ID</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar with file management only
with st.sidebar:
    st.markdown("### 🗂️ File Management")
    
    if st.button("🧹 Clean Old Files"):
        FileManager.cleanup_old_files(directory_path, max_age_hours=1)
        st.success("Files cleaned!")
    
    # Show current CSV files
    try:
        csv_files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]
        if csv_files:
            st.write("📁 Current CSV files:")
            for file in csv_files[:5]:  # Show max 5 files
                file_info = FileManager.get_file_info(os.path.join(directory_path, file))
                status = "🔒" if file_info.get('locked', False) else "✅"
                st.write(f"{status} {file}")
        else:
            st.write("📭 No CSV files found")
    except Exception as e:
        st.write(f"⚠️ Error accessing files: {str(e)}")

# Main content area
if youtube_link:
    video_id = extract_video_id(youtube_link)
    
    if video_id:
        # Show processing message
        st.markdown('<div class="processing-message">🔄 Processing your request...</div>', unsafe_allow_html=True)
        
        try:
            # Processing indicator
            with st.spinner('🔄 Processing your request...'):
                channel_id = get_channel_id(video_id)
                
                # Save comments
                csv_file = save_video_comments_to_csv(video_id)
                delete_non_matching_csv_files(directory_path, video_id)
                
                st.markdown('<div class="success-message">✅ Comments successfully analyzed!</div>', unsafe_allow_html=True)
                
                # Download button
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    st.download_button(
                        label="📥 Download Comments CSV",
                        data=open(csv_file, 'rb').read(),
                        file_name=os.path.basename(csv_file),
                        mime="text/csv"
                    )
                
                # Get channel and video info
                channel_info = get_channel_info(youtube, channel_id)
                stats = get_video_stats(video_id)
                
                # Channel Information Section
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<h2 class="section-title">📺 Channel Information</h2>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f'<img src="{channel_info["channel_logo_url"]}" class="channel-logo" style="width: 150px; height: 150px; display: block; margin: 0 auto;">', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'<h3 style="color: white; font-family: Inter; font-weight: 600; margin-bottom: 1rem; text-align: center;">{channel_info["channel_title"]}</h3>', unsafe_allow_html=True)
                    
                    # Channel metrics
                    subcol1, subcol2, subcol3 = st.columns(3)
                    
                    with subcol1:
                        st.markdown(f'''
                        <div class="metric-card">
                            <div class="metric-value">{channel_info["video_count"]}</div>
                            <div class="metric-label">Videos</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    with subcol2:
                        st.markdown(f'''
                        <div class="metric-card">
                            <div class="metric-value">{channel_info["subscriber_count"]}</div>
                            <div class="metric-label">Subscribers</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    with subcol3:
                        created_date = channel_info["channel_created_date"][:10]
                        st.markdown(f'''
                        <div class="metric-card">
                            <div class="metric-value">{created_date}</div>
                            <div class="metric-label">Created</div>
                        </div>
                        ''', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Video Statistics Section
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<h2 class="section-title">📊 Video Statistics</h2>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-value">👀 {stats["viewCount"]}</div>
                        <div class="metric-label">Views</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-value">👍 {stats["likeCount"]}</div>
                        <div class="metric-label">Likes</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-value">💬 {stats["commentCount"]}</div>
                        <div class="metric-label">Comments</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Video Player Section
                st.markdown('<div class="video-container">', unsafe_allow_html=True)
                st.markdown('<h2 class="section-title">🎥 Video Player</h2>', unsafe_allow_html=True)
                _, container, _ = st.columns([1, 3, 1])
                with container:
                    st.video(data=youtube_link)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Sentiment Analysis Section
                results = analyze_sentiment(csv_file)
                
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<h2 class="section-title">🎭 Sentiment Analysis</h2>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f'''
                    <div class="metric-card sentiment-positive">
                        <div class="metric-value">😊 {results["num_positive"]}</div>
                        <div class="metric-label">Positive</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'''
                    <div class="metric-card sentiment-negative">
                        <div class="metric-value">😠 {results["num_negative"]}</div>
                        <div class="metric-label">Negative</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f'''
                    <div class="metric-card sentiment-neutral">
                        <div class="metric-value">😐 {results["num_neutral"]}</div>
                        <div class="metric-label">Neutral</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Charts Section
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<h2 class="section-title">📈 Data Visualization</h2>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<h3 style="color: white; text-align: center; margin-bottom: 1rem;">📊 Distribution</h3>', unsafe_allow_html=True)
                    bar_chart(csv_file)
                
                with col2:
                    st.markdown('<h3 style="color: white; text-align: center; margin-bottom: 1rem;">🥧 Proportion</h3>', unsafe_allow_html=True)
                    plot_sentiment(csv_file)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Channel Description Section
                if channel_info["channel_description"]:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.markdown('<h2 class="section-title">📝 Channel Description</h2>', unsafe_allow_html=True)
                    st.markdown(f'<p style="color: rgba(255,255,255,0.9); line-height: 1.6; font-size: 1rem; text-align: center;">{channel_info["channel_description"]}</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.markdown(f'<div class="error-message">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="error-message">❌ Invalid YouTube link. Please check the URL format.</div>', unsafe_allow_html=True)
else:
    # Welcome Section - Only show when no URL is entered
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🚀 Welcome to YouTube Sentiment Pro</h2>', unsafe_allow_html=True)
    st.markdown('''
    <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; line-height: 1.6; text-align: center;">
    Experience the future of comment analysis with our <strong>advanced multilingual AI</strong> sentiment engine. 
    Simply paste a YouTube link above to get started with beautiful, 
    insightful analytics powered by cutting-edge transformer models.
    </p>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced Features Section
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">✨ Advanced AI Features</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('''
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🌍</div>
            <div class="metric-label">Multilingual Support</div>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-top: 0.5rem;">Supports Hindi, English, Spanish, French, German, and 100+ languages</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🤖</div>
            <div class="metric-label">AI Transformer Models</div>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-top: 0.5rem;">Advanced BERT & RoBERTa models trained on social media data</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown('''
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">😊</div>
            <div class="metric-label">Emoji Intelligence</div>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-top: 0.5rem;">Advanced emoji processing and context understanding</p>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Technical Capabilities Section
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🔧 Technical Capabilities</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('''
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">📊</div>
            <div class="metric-label">Enhanced Analytics</div>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-top: 0.5rem;">Up to 1200+ comments analyzed with confidence scoring and language detection</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🎯</div>
            <div class="metric-label">Smart Processing</div>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-top: 0.5rem;">Automatic language detection, translation, and context-aware sentiment analysis</p>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Start Guide
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🎬 Quick Start Guide</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('''
        <div class="metric-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">1️⃣</div>
            <div class="metric-label">Paste YouTube URL</div>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-top: 0.5rem;">Copy any YouTube video link and paste it in the input above</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="metric-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">2️⃣</div>
            <div class="metric-label">AI Analysis</div>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-top: 0.5rem;">Our advanced AI models analyze comments in multiple languages</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown('''
        <div class="metric-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">3️⃣</div>
            <div class="metric-label">Get Insights</div>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-top: 0.5rem;">View beautiful charts, statistics, and download results as CSV</p>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
        
        
  
    
    
        



