# sms_service.py
import africastalking
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()



CELCO_URL = os.getenv("CELCO_URL")
CELCO_API_KEY = os.getenv("CELCO_API_KEY")
CELCO_PARTNER_ID = os.getenv("CELCO_PARTNER_ID")
CELCO_SHORTCODE = os.getenv("CELCO_SHORTCODE")


class SMSService:
    def __init__(self, username, api_key):
        print(f"🔧 Initializing SMS Service (HTTP API):")
        print(f"   Username: '{username}'")
        print(f"   API Key: '{api_key[:8]}...{api_key[-4:]}' (masked)" if api_key else "   API Key: None")
        
        self.username = username
        self.api_key = api_key
        self.base_url = "https://api.sandbox.africastalking.com/version1/messaging"
        print(f"   Using endpoint: {self.base_url}")

    def send_sms(self, phone_number, message, sender=None):
        """
        Send single SMS using Africa's Talking HTTP API directly
        """
        try:
            print(f"📤 SMS HTTP API Debug:")
            print(f"   Phone: '{phone_number}' (type: {type(phone_number)})")
            print(f"   Message: '{message}' (length: {len(message)})")
            print(f"   Sender: '{sender}'")
            
           
            # Prepare headers
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
                'apiKey': self.api_key
            }
            
            # Prepare data for form submission
            data = {
                'username': self.username,
                'to': phone_number,  # Single recipient
                'message': message,
                'bulkSMSMode': 1,  # Default bulk SMS mode
                'enqueue': 1       # Enable queue
            }
            
            # Add sender if provided
            if sender:
                data['from'] = sender
            
            print(f"   Headers: {headers}")
            print(f"   Data: {data}")
            print(f"   URL: {self.base_url}")
            
            # Make the HTTP POST request
            response = requests.post(
                self.base_url,
                headers=headers,
                data=data,  # Use data parameter for form encoding
                timeout=30
            )
            
            print(f"   HTTP Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            print(f"   Raw Response: {response.text}")
            
            # Handle response
            if response.status_code == 200 or response.status_code == 201:
                try:
                    json_response = response.json()
                    print(f"   Parsed Response: {json_response}")
                    return json_response
                except json.JSONDecodeError:
                    print(f"   Failed to parse JSON response")
                    return {"error": f"Invalid JSON response: {response.text}"}
            else:
                print(f"   HTTP Error: {response.status_code}")
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ HTTP Request Exception: {str(e)}")
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            print(f"❌ SMS Service Exception: {str(e)}")
            return {"error": f"SMS service error: {str(e)}"}


def send_sms_celcom(mobile, message):
    """Send SMS using Celcom Africa API"""
    payload = {
        "partnerID": CELCO_PARTNER_ID,
        "apikey": CELCO_API_KEY,
        "mobile": mobile,
        "message": message,
        "shortcode": CELCO_SHORTCODE,
        "pass_type": "plain"
    }

    headers = {"Content-Type": "application/json"}

    try:
        res = requests.post(CELCO_URL, json=payload, headers=headers)
        return res.json()
    except Exception as e:
        return {"error": str(e)}