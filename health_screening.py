from datetime import datetime, timedelta
from flask import flash

def schedule_health_screening(user, screening_type, preferred_date, preferred_time, notes=None):
    """
    Schedule a conventional health screening appointment
    """
    try:
        if not all([user, screening_type, preferred_date, preferred_time]):
            raise ValueError("Missing required fields")

        # Validate screening type
        valid_types = ['general', 'mental', 'dermatology', 'cardio']
        if screening_type not in valid_types:
            raise ValueError("Invalid screening type")

        # Validate date (must be future date)
        preferred_date = datetime.strptime(preferred_date, '%Y-%m-%d').date()
        if preferred_date < datetime.now().date():
            raise ValueError("Cannot schedule appointment in the past")

        # Create screening record
        screening = {
            'user_id': user.id,
            'screening_type': screening_type,
            'preferred_date': preferred_date,
            'preferred_time': preferred_time,
            'notes': notes,
            'status': 'scheduled',
            'created_at': datetime.utcnow()
        }
        
        return screening, True
    except Exception as e:
        flash(f'Error scheduling screening: {str(e)}', 'error')
        return None, False

def get_available_slots(screening_type, preferred_date):
    """
    Get available time slots for a specific screening type and date
    Returns time slots based on screening type and typical medical office hours
    """
    if preferred_date:
        # Convert string to date if needed
        if isinstance(preferred_date, str):
            preferred_date = datetime.strptime(preferred_date, '%Y-%m-%d').date()
        
        # Don't show slots for past dates
        if preferred_date < datetime.now().date():
            return {'morning': [], 'afternoon': [], 'evening': []}

        # Different slots based on screening type
        slots = {
            'general': {
                'morning': ['9:00 AM', '10:00 AM', '11:00 AM'],
                'afternoon': ['1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM'],
                'evening': ['5:00 PM', '6:00 PM']
            },
            'mental': {
                'morning': ['9:30 AM', '10:30 AM'],
                'afternoon': ['2:00 PM', '3:00 PM', '4:00 PM'],
                'evening': ['5:00 PM']
            },
            'dermatology': {
                'morning': ['9:00 AM', '10:00 AM', '11:00 AM'],
                'afternoon': ['1:30 PM', '2:30 PM', '3:30 PM'],
                'evening': []
            },
            'cardio': {
                'morning': ['8:00 AM', '9:00 AM', '10:00 AM'],
                'afternoon': ['1:00 PM', '2:00 PM', '3:00 PM'],
                'evening': ['5:00 PM']
            }
        }
        
        return slots.get(screening_type, slots['general'])
    
    return {'morning': [], 'afternoon': [], 'evening': []}
