"""
Session management module for persistent login sessions
"""
import json
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

SESSIONS_FILE = "sessions.json"
SESSION_TIMEOUT_HOURS = 24  # Sessions expire after 24 hours


def load_sessions() -> Dict:
    """
    Load active sessions from JSON file.
    
    Returns:
        Dictionary of active sessions
    """
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
                sessions = json.load(f)
                return sessions
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
            return {}
    return {}


def save_sessions(sessions: Dict) -> bool:
    """
    Save sessions to JSON file.
    
    Args:
        sessions: Dictionary of sessions to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving sessions: {e}")
        return False


def create_session(username: str, role: str) -> str:
    """
    Create a new session for a user.
    
    Args:
        username: Username
        role: User role
        
    Returns:
        Session token
    """
    # Generate a secure random session token
    session_token = secrets.token_urlsafe(32)
    
    sessions = load_sessions()
    
    # Remove old sessions for this user
    sessions = {k: v for k, v in sessions.items() if v.get('username') != username}
    
    # Create new session
    sessions[session_token] = {
        'username': username,
        'role': role,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'last_activity': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'expires_at': (datetime.now() + timedelta(hours=SESSION_TIMEOUT_HOURS)).strftime('%Y-%m-%d %H:%M:%S')
    }
    
    save_sessions(sessions)
    logger.info(f"Session created for user: {username}")
    
    return session_token


def validate_session(session_token: str) -> Optional[Dict]:
    """
    Validate a session token and return session data if valid.
    
    Args:
        session_token: Session token to validate
        
    Returns:
        Session data dictionary if valid, None otherwise
    """
    if not session_token:
        return None
    
    sessions = load_sessions()
    
    if session_token not in sessions:
        return None
    
    session = sessions[session_token]
    
    # Check if session has expired
    try:
        expires_at = datetime.strptime(session['expires_at'], '%Y-%m-%d %H:%M:%S')
        if datetime.now() > expires_at:
            # Session expired, remove it
            del sessions[session_token]
            save_sessions(sessions)
            logger.info(f"Session expired: {session_token}")
            return None
    except Exception as e:
        logger.error(f"Error checking session expiration: {e}")
        return None
    
    # Update last activity
    session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sessions[session_token] = session
    save_sessions(sessions)
    
    return session


def delete_session(session_token: str) -> bool:
    """
    Delete a session.
    
    Args:
        session_token: Session token to delete
        
    Returns:
        True if successful, False otherwise
    """
    sessions = load_sessions()
    
    if session_token in sessions:
        username = sessions[session_token].get('username', 'Unknown')
        del sessions[session_token]
        save_sessions(sessions)
        logger.info(f"Session deleted for user: {username}")
        return True
    
    return False


def cleanup_expired_sessions():
    """
    Remove all expired sessions from the sessions file.
    """
    sessions = load_sessions()
    current_time = datetime.now()
    expired_count = 0
    
    valid_sessions = {}
    for token, session in sessions.items():
        try:
            expires_at = datetime.strptime(session['expires_at'], '%Y-%m-%d %H:%M:%S')
            if current_time <= expires_at:
                valid_sessions[token] = session
            else:
                expired_count += 1
        except Exception:
            # Invalid expiration date, remove session
            expired_count += 1
    
    if expired_count > 0:
        save_sessions(valid_sessions)
        logger.info(f"Cleaned up {expired_count} expired sessions")
    
    return expired_count


def get_user_sessions(username: str) -> list:
    """
    Get all active sessions for a user.
    
    Args:
        username: Username
        
    Returns:
        List of session tokens for the user
    """
    sessions = load_sessions()
    user_sessions = []
    
    for token, session in sessions.items():
        if session.get('username', '').lower() == username.lower():
            user_sessions.append(token)
    
    return user_sessions

