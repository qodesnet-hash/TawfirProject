import firebase_admin
from firebase_admin import credentials, messaging
import os

# Initialize Firebase
cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

def send_push_notification(token, title, body, data=None):
    """
    Send push notification to a device
    """
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=token,
        )
        
        response = messaging.send(message)
        return {'success': True, 'response': response}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def send_multicast_notification(tokens, title, body, data=None):
    """
    Send notification to multiple devices
    """
    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            tokens=tokens,
        )
        
        response = messaging.send_multicast(message)
        return {
            'success': True,
            'success_count': response.success_count,
            'failure_count': response.failure_count
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
