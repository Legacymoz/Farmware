import requests
import os
from dotenv import load_dotenv
from ..models import Farmer, Advisory, FarmingAdvisory
from ..SMS.utils import send_sms_to_farmer
from flask import current_app
from .. import db

# Load environment variables
load_dotenv()


def verify_full_message(phone_number, service_code, text):
    """
    Main Function that controls the whole advisory verification flow.
    """
    # Step 1: Extract VC from service_code
    if text =='':
        VC = extract_vc_from_service_code(service_code)
    else:
        VC = text
    
    print(f"🔍 Extracted VC: {VC}")
    print(f"🔍 Phone Number in verify full message: {phone_number}")
    
    #Step 2, Get the secret Key matching that Phone number from DB
    secret_key = get_secret_key_by_phone(phone_number)
    if not secret_key:
        return {'success': False, 'error': 'Farmer not found'}
    

    #Step 3 Send VC and Secret Key to SMC to get the message ID 
    response = send_vc_to_smc(secret_key, VC)
    if response is None or 'message_id' not in response:
        return {'success': False, 'error': 'Failed to verify VC with SMC'}
    message_id = response['message_id']


    # Step 4: Use the messageID, to get the full Advisory SMS
    full_advisory = get_full_advisory_by_message_id(message_id)
    if not full_advisory:
        return {'success': False, 'error': 'Advisory not found'}
    

    # Step 5: Send the Advisory SMS to the farmer's phone number
    sms_result = send_sms_to_farmer(phone_number, full_advisory)
    if not sms_result['success']:
        return {'success': False, 'error': f"Failed to send SMS: {sms_result['error']}"}
    
    return {
        'success': True,
        'message': 'Full advisory verified and sent successfully',
        'phone_number': phone_number,
        'verification_code': VC,
        'advisory_content': full_advisory,
        'sms_status': 'sent'
    }




def extract_vc_from_service_code(service_code):
    """
    Extract verification code (VC) from the USSD service code string.
    Example: *123*ABC123# -> ABC123
    """
    try:
        # Split by '*' and take the last part before '#'
        parts = service_code.split('*')
        if len(parts) < 2:
            return None
        print("Parts after split:", parts)
        last_part = parts[-1]
        vc = last_part.split('#')[0]
        return vc
    except Exception as e:
        print(f"Error extracting VC from service code: {str(e)}")
        return None

def send_vc_to_smc(secret_key, vc):
    """
    Send the extracted VC along with secret key to SMC for verification.
    
    Args:
        secret_key (bytes): Secret key from database (stored as LargeBinary)
        vc (str): Verification code to verify
        
    Returns:
        dict: SMC response containing message_id
    """
    try:
        smc_url = "http://localhost:5001/get-messageID"  
        
        # Convert bytes to string for JSON transmission
        # This is the HTTP/JSON layer - must be string
        if isinstance(secret_key, bytes):
            secret_key_str = secret_key.decode('utf-8')
        else:
            # If it's already a string (shouldn't happen from DB), keep it
            secret_key_str = str(secret_key)
        
        payload = {
            "vc": vc,
            "secret_key": secret_key_str  # String for JSON
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('SMC_API_KEY')}" 
            
        }
        print("")
        # DEBUG: Print what we're sending
        print(f"🔍 SMC Request Debug:")
        print(f"   URL: {smc_url}")
        print(f"   VC: '{vc}' (type: {type(vc)})")
        print(f"   Secret Key: '{secret_key_str}' (type: {type(secret_key_str)})")
        print(f"   API Key: '{os.getenv('SMC_API_KEY')}'")
        print(f"   Payload: {payload}")
        
        
        # Send POST request to SMC
        response = requests.post(
            smc_url, 
            json=payload, 
            headers=headers,
            
        )
        # ADD THIS DEBUG OUTPUT
        print(f"📄 SMC Response Debug:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print(f"   Response Text: '{response.text}'")

        #Check for non-200 status codes BEFORE raise_for_status()
        if response.status_code != 200:
            print(f"❌ SMC returned non-200 status: {response.status_code}")
            print(f"   Response body: {response.text}")
            return None

        
        
        return response.json()
        
    # except requests.exceptions.RequestException as e:
    #     print(f"Error sending to SMC: {e}")
    #     return None
    # except Exception as e:
    #     print(f"Unexpected error: {e}")
    #     return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending to SMC: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Error Status: {e.response.status_code}")
            print(f"   Error Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def get_secret_key_by_phone(phone_number):
    """
    Get the secret key associated with a phone number from the database.
    
    Args:
        phone_number (str): Farmer's phone number
        
    Returns:
        bytes: Secret key if found (as bytes from LargeBinary column), None otherwise
    """
    try:
        print(f"🔍 Looking up secret key for phone: {phone_number}")
        
        # Ensure we have application context
        with current_app.app_context():
            # Query the database for farmer with matching phone number
            farmer = Farmer.query.filter_by(phone=phone_number).first()
                
            if farmer:
                print(f"✅ Found farmer: {farmer.id} with secret key")
                # Return as bytes (from LargeBinary column)
                return farmer.secret_key  # This should be bytes from database
            else:
                print(f"❌ No farmer found for phone: {phone_number}")
                return None
                    
                
    except Exception as e:
        print(f"Error getting secret key: {str(e)}")
        return None

   


def get_full_advisory_by_message_id(message_id):
    """
    Get the full advisory content using the message ID.
    
    Args:
        message_id (str): Message ID returned from SMC
        
    Returns:
        str: Full advisory content if found, None otherwise
    """
    try:
        print(f"📄 Looking up full advisory for message ID: {message_id}")
        
        # Ensure we have application context
        with current_app.app_context():
            # Query the database for advisory with matching ID
            try:
                advisory_id = int(message_id)  # Convert to int if message_id is advisory ID
                advisory = Advisory.query.get(advisory_id)
            except ValueError:
                # If message_id is not an integer, try searching by title
                advisory = Advisory.query.filter_by(title=message_id).first()
            
            if advisory:
                print(f"✅ Found advisory: {advisory.title}")
                # Return only the message content
                return advisory.message
            else:
                print(f"❌ No advisory found for message ID: {message_id}")
                return None
                
            
    except Exception as e:
        print(f"Error getting advisory content: {str(e)}")
        return None
    