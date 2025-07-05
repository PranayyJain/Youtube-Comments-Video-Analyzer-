import os
import time
import shutil
import tempfile
import streamlit as st
from datetime import datetime

class FileManager:
    """
    A utility class for handling file operations with better error handling
    """
    
    @staticmethod
    def is_file_locked(filepath):
        """
        Check if a file is locked by another process
        """
        try:
            with open(filepath, 'r+'):
                return False
        except (IOError, OSError):
            return True
    
    @staticmethod
    def safe_remove_file(filepath, max_retries=3):
        """
        Safely remove a file with retry logic
        """
        if not os.path.exists(filepath):
            return True
        
        for attempt in range(max_retries):
            try:
                os.remove(filepath)
                return True
            except PermissionError:
                if attempt < max_retries - 1:
                    st.warning(f"🔄 File is locked, retrying in {attempt + 1} seconds...")
                    time.sleep(attempt + 1)
                else:
                    # Try to rename the file instead
                    return FileManager.backup_locked_file(filepath)
            except Exception as e:
                st.error(f"❌ Error removing file: {str(e)}")
                return False
        
        return False
    
    @staticmethod
    def backup_locked_file(filepath):
        """
        If file is locked, rename it with timestamp instead of deleting
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{filepath}.backup_{timestamp}"
            shutil.move(filepath, backup_name)
            st.info(f"📁 Moved locked file to: {os.path.basename(backup_name)}")
            return True
        except Exception as e:
            st.error(f"❌ Could not backup locked file: {str(e)}")
            return False
    
    @staticmethod
    def create_unique_filename(base_filename):
        """
        Create a unique filename if the original is locked
        """
        if not os.path.exists(base_filename):
            return base_filename
        
        if not FileManager.is_file_locked(base_filename):
            return base_filename
        
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(base_filename)
        return f"{name}_{timestamp}{ext}"
    
    @staticmethod
    def cleanup_old_files(directory, pattern="*.csv", max_age_hours=24):
        """
        Clean up old files that are older than max_age_hours
        """
        current_time = time.time()
        cleaned_files = []
        
        try:
            for filename in os.listdir(directory):
                if not filename.endswith('.csv'):
                    continue
                
                filepath = os.path.join(directory, filename)
                file_age = current_time - os.path.getmtime(filepath)
                
                if file_age > (max_age_hours * 3600):  # Convert hours to seconds
                    if FileManager.safe_remove_file(filepath):
                        cleaned_files.append(filename)
            
            if cleaned_files:
                st.info(f"🧹 Cleaned up {len(cleaned_files)} old files")
                
        except Exception as e:
            st.error(f"❌ Error during cleanup: {str(e)}")
    
    @staticmethod
    def get_file_info(filepath):
        """
        Get detailed information about a file
        """
        try:
            stat = os.stat(filepath)
            return {
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                'locked': FileManager.is_file_locked(filepath)
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def force_close_file_handles(filepath):
        """
        Windows-specific method to force close file handles (requires admin privileges)
        """
        try:
            import subprocess
            # This requires Windows Resource Kit or similar tools
            # For now, we'll just show a helpful message
            st.warning("🔧 To force close file handles, please close Excel or any text editors that might have the file open.")
            return False
        except Exception:
            return False 