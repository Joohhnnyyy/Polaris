import os
import json
import firebase_admin
from firebase_admin import credentials, messaging

class FirebasePushClient:
    def __init__(self):
        self.initialized = False
        service_account_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            "firebase-service-account.json"
        )
        
        if not os.path.exists(service_account_path):
            print("firebase-service-account.json not found. Push notifications will be bypassed.")
            return

        try:
            # Validate if it's a real config or the template
            with open(service_account_path) as f:
                config = json.load(f)
                if "your-firebase-project-id" in config.get("project_id", ""):
                    print("Firebase service account template found. Please replace it with real credentials.")
                    return

            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            self.initialized = True
            print("Firebase Admin SDK successfully initialized.")
        except Exception as e:
            print(f"Error initializing Firebase Admin SDK: {e}")

    def send_push_notification(self, token: str, title: str, body: str, data: dict = None) -> bool:
        """
        Sends a single push notification to a device token.
        """
        if not self.initialized:
            print("Firebase client not initialized. Bypassing push send.")
            return False

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token,
            data=data or {}
        )

        try:
            response = messaging.send(message)
            print(f"Successfully sent Firebase message: {response}")
            return True
        except Exception as e:
            print(f"Failed to send Firebase message: {e}")
            return False
            
    def broadcast_to_topic(self, topic: str, title: str, body: str, data: dict = None) -> bool:
        """
        Broadcasts a push notification to all devices subscribed to a topic (e.g. zone notifications).
        """
        if not self.initialized:
            print("Firebase client not initialized. Bypassing topic broadcast.")
            return False

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            topic=topic,
            data=data or {}
        )

        try:
            response = messaging.send(message)
            print(f"Successfully broadcasted to topic {topic}: {response}")
            return True
        except Exception as e:
            print(f"Failed to broadcast to topic {topic}: {e}")
            return False
