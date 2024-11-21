from datetime import datetime, timedelta
import json

def prepare_consultation_questionnaire(symptoms_data):
    """
    Prepare initial consultation questionnaire for healthcare providers
    """
    urgent_symptoms = ['chest_pain', 'difficulty_breathing', 'severe_headache']
    consultation_data = {
        'symptoms': symptoms_data,
        'requires_urgent_care': any(symptom in urgent_symptoms for symptom in symptoms_data),
        'consultation_type': 'emergency' if any(symptom in urgent_symptoms for symptom in symptoms_data) else 'regular'
    }
    
    return {
        'questionnaire_data': consultation_data,
        'recommendation': get_consultation_type(consultation_data)
    }

def get_consultation_type(consultation_data):
    """Determine appropriate consultation type based on symptoms"""
    if consultation_data['requires_urgent_care']:
        return "Please seek immediate medical attention at the nearest emergency facility"
    else:
        return "Schedule a consultation with an appropriate healthcare provider"

def get_screening_questions(screening_type):
    """
    Return standardized screening questions based on screening type
    """
    questions = {
        'mental': [
            'How often do you feel nervous or anxious?',
            'Do you have trouble concentrating on tasks?',
            'How is your sleep quality?',
            'Do you often feel overwhelmed?'
        ],
        'general': [
            'Have you experienced any unexplained weight changes?',
            'Do you have any ongoing medical conditions?',
            'Are you currently taking any medications?',
            'How would you rate your overall health?'
        ],
        'cardio': [
            'Do you experience chest pain during physical activity?',
            'Have you ever had high blood pressure?',
            'Is there a family history of heart disease?',
            'How often do you exercise?'
        ],
        'dermatology': [
            'Have you noticed any changes in your skin?',
            'Do you have any concerning moles or spots?',
            'Do you use sun protection regularly?',
            'Any history of skin conditions in your family?'
        ]
    }
    
    return questions.get(screening_type, questions['general'])
