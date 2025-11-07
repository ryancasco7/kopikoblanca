"""
Activity logging module for tracking system activities
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

ACTIVITIES_FILE = "activities.json"
MAX_ACTIVITIES = 100  # Keep only the most recent 100 activities


def load_activities() -> List[Dict]:
    """
    Load activities from JSON file.
    
    Returns:
        List of activity dictionaries
    """
    if os.path.exists(ACTIVITIES_FILE):
        try:
            with open(ACTIVITIES_FILE, 'r', encoding='utf-8') as f:
                activities = json.load(f)
                # Ensure it's a list
                if isinstance(activities, list):
                    return activities
                else:
                    return []
        except Exception as e:
            logger.error(f"Error loading activities: {e}")
            return []
    return []


def save_activities(activities: List[Dict]) -> bool:
    """
    Save activities to JSON file.
    
    Args:
        activities: List of activity dictionaries
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Keep only the most recent activities
        if len(activities) > MAX_ACTIVITIES:
            activities = activities[-MAX_ACTIVITIES:]
        
        with open(ACTIVITIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(activities, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving activities: {e}")
        return False


def log_activity(activity_type: str, user: str, description: str, details: Optional[Dict] = None) -> bool:
    """
    Log an activity to the activities file.
    
    Args:
        activity_type: Type of activity (e.g., 'login', 'logout', 'download', 'assessment', 'export')
        user: Username who performed the activity
        description: Human-readable description of the activity
        details: Optional dictionary with additional details
        
    Returns:
        True if successful, False otherwise
    """
    try:
        activities = load_activities()
        
        activity = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': activity_type,
            'user': user,
            'description': description,
            'details': details or {}
        }
        
        activities.append(activity)
        return save_activities(activities)
    except Exception as e:
        logger.error(f"Error logging activity: {e}")
        return False


def get_recent_activities(limit: int = 50) -> List[Dict]:
    """
    Get recent activities, sorted by timestamp (most recent first).
    
    Args:
        limit: Maximum number of activities to return
        
    Returns:
        List of activity dictionaries, sorted by timestamp descending
    """
    activities = load_activities()
    # Sort by timestamp descending (most recent first)
    activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return activities[:limit]


def get_activities_by_type(activity_type: str, limit: int = 50) -> List[Dict]:
    """
    Get recent activities filtered by type.
    
    Args:
        activity_type: Type of activity to filter by
        limit: Maximum number of activities to return
        
    Returns:
        List of filtered activity dictionaries
    """
    activities = load_activities()
    filtered = [a for a in activities if a.get('type') == activity_type]
    filtered.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return filtered[:limit]


def get_activities_by_user(username: str, limit: int = 50) -> List[Dict]:
    """
    Get recent activities filtered by user.
    
    Args:
        username: Username to filter by
        limit: Maximum number of activities to return
        
    Returns:
        List of filtered activity dictionaries
    """
    activities = load_activities()
    filtered = [a for a in activities if a.get('user', '').lower() == username.lower()]
    filtered.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return filtered[:limit]

