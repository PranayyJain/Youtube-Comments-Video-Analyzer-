import csv
from googleapiclient.discovery import build
from collections import Counter
import streamlit as st
from Senti import extract_video_id
from googleapiclient.errors import HttpError
import os
import time
import tempfile
from file_manager import FileManager

import warnings
warnings.filterwarnings('ignore')

# Replace with your own API key
DEVELOPER_KEY = st.secrets["YOUTUBE_API_KEY"]
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
# Create a client object to interact with the YouTube API
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

#video_id=extract_video_id(youtube_link)

def get_channel_id(video_id):
    response = youtube.videos().list(part='snippet', id=video_id).execute()
    channel_id = response['items'][0]['snippet']['channelId']
    return channel_id

#channel_id=get_channel_id(video_id)
    
def safe_file_operation(filepath, operation, max_retries=3):
    """
    Safely perform file operations with retry logic
    """
    for attempt in range(max_retries):
        try:
            return operation(filepath)
        except PermissionError as e:
            if attempt < max_retries - 1:
                st.warning(f"🔄 File is locked, retrying in {attempt + 1} seconds...")
                time.sleep(attempt + 1)
            else:
                st.error(f"❌ Cannot access file after {max_retries} attempts. Please close any applications that might be using the file.")
                raise e
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            raise e

def safe_delete_file(filepath):
    """
    Safely delete a file with error handling
    """
    def delete_operation(fp):
        if os.path.exists(fp):
            os.remove(fp)
        return True
    
    try:
        return safe_file_operation(filepath, delete_operation)
    except PermissionError:
        st.warning(f"⚠️ Could not delete {os.path.basename(filepath)}. It may be open in another application.")
        return False
    except Exception as e:
        st.error(f"❌ Error deleting file: {str(e)}")
        return False

def save_video_comments_to_csv(video_id):
    """
    Retrieve comments for the specified video and save to CSV with robust error handling
    """
    comments = []
    
    try:
        # Get comments from YouTube API with enhanced limits
        results = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='plainText',
            maxResults=100,  # YouTube API max per request
            order='relevance'  # Get most relevant comments first
        ).execute()
        
        # Extract the text content of each comment
        pages_fetched = 0
        max_pages = 15  # Allow up to 15 pages (1500 comments max)
        
        while results and pages_fetched < max_pages:
            for item in results['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                username = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                comments.append([username, comment])
            
            # Get next page if available
            if 'nextPageToken' in results and len(comments) < 1200:  # Increased limit to 1200 comments
                nextPage = results['nextPageToken']
                try:
                    results = youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        textFormat='plainText',
                        pageToken=nextPage,
                        maxResults=100,
                        order='relevance'
                    ).execute()
                    pages_fetched += 1
                except Exception as e:
                    st.warning(f"⚠️ Stopped fetching at {len(comments)} comments due to API limit")
                    break
            else:
                break
        
        # Generate base filename
        base_filename = f"{video_id}.csv"
        final_filename = base_filename  # Default to base filename
        
        # Handle existing file conflicts
        if os.path.exists(base_filename):
            if FileManager.is_file_locked(base_filename):
                # Create backup of locked file and use base name
                st.info(f"📄 File {base_filename} is locked, creating backup...")
                FileManager.backup_locked_file(base_filename)
                final_filename = base_filename
            else:
                # File exists but not locked, we can overwrite it
                try:
                    FileManager.safe_remove_file(base_filename)
                    final_filename = base_filename
                except:
                    # If we can't remove it, create unique filename
                    final_filename = FileManager.create_unique_filename(base_filename)
                    st.info(f"📄 Creating new file: {final_filename}")
        
        # Save comments to CSV
        try:
            with open(final_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Username', 'Comment'])
                for comment in comments:
                    writer.writerow([comment[0], comment[1]])
            
            st.success(f"✅ Successfully saved {len(comments)} comments to {final_filename}!")
            return final_filename
            
        except PermissionError as e:
            st.error(f"❌ Permission denied when writing to {final_filename}")
            st.info("💡 This usually happens when the file is open in Excel or another application.")
            st.info("🔧 Please close any applications that might be using the file and try again.")
            
            # Create a temporary file as fallback
            temp_filename = f"temp_{video_id}_{int(time.time())}.csv"
            try:
                with open(temp_filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Username', 'Comment'])
                    for comment in comments:
                        writer.writerow([comment[0], comment[1]])
                
                st.warning(f"⚠️ Created temporary file: {temp_filename}")
                return temp_filename
            except Exception as temp_error:
                st.error(f"❌ Could not create temporary file: {str(temp_error)}")
                raise temp_error
            
    except HttpError as e:
        st.error(f"❌ YouTube API Error: {str(e)}")
        if "quotaExceeded" in str(e):
            st.error("🚫 YouTube API quota exceeded. Please try again tomorrow or use a different API key.")
        elif "videoNotFound" in str(e):
            st.error("📹 Video not found. Please check if the video exists and is public.")
        else:
            st.error("🔌 Please check your internet connection and API key configuration.")
        
        # Create a demo file for testing - use existing file if available
        if os.path.exists(base_filename):
            st.info(f"📝 Using existing file: {base_filename}")
            return base_filename
        else:
            demo_filename = f"demo_{video_id}.csv"
            with open(demo_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Username', 'Comment'])
                writer.writerow(['DemoUser1', 'This is a positive demo comment! Great video!'])
                writer.writerow(['DemoUser2', 'This is a negative demo comment. Not good.'])
                writer.writerow(['DemoUser3', 'This is a neutral demo comment.'])
            
            st.info(f"📝 Created demo file for testing: {demo_filename}")
            return demo_filename
        
    except Exception as e:
        st.error(f"❌ Unexpected error while saving comments: {str(e)}")
        
        # Try to use existing file if available
        if os.path.exists(base_filename):
            st.warning(f"⚠️ Using existing file: {base_filename}")
            return base_filename
        else:
            raise e

def get_video_stats(video_id):
    try:
        response = youtube.videos().list(
            part='statistics',
            id=video_id
        ).execute()

        return response['items'][0]['statistics']

    except HttpError as error:
        st.error(f'❌ Error getting video stats: {error}')
        return {
            'viewCount': 'N/A',
            'likeCount': 'N/A',
            'commentCount': 'N/A'
        }
    
    
       
    
def get_channel_info(youtube, channel_id):
    try:
        response = youtube.channels().list(
            part='snippet,statistics,brandingSettings',
            id=channel_id
        ).execute()

        channel_title = response['items'][0]['snippet']['title']
        video_count = response['items'][0]['statistics']['videoCount']
        channel_logo_url = response['items'][0]['snippet']['thumbnails']['high']['url']
        channel_created_date = response['items'][0]['snippet']['publishedAt']
        subscriber_count = response['items'][0]['statistics']['subscriberCount']
        channel_description = response['items'][0]['snippet']['description']
        

        channel_info = {
            'channel_title': channel_title,
            'video_count': video_count,
            'channel_logo_url': channel_logo_url,
            'channel_created_date': channel_created_date,
            'subscriber_count': subscriber_count,
            'channel_description': channel_description
        }

        return channel_info

    except HttpError as error:
        st.error(f'❌ Error getting channel info: {error}')
        return {
            'channel_title': 'Unknown Channel',
            'video_count': 'N/A',
            'channel_logo_url': 'https://via.placeholder.com/150',
            'channel_created_date': 'Unknown',
            'subscriber_count': 'N/A',
            'channel_description': 'Channel information not available.'
        }

    

