import requests
import os
from dotenv import load_dotenv
from .sms_service import SMSService
from .sms_service import send_sms_celcom
import os

# Load environment variables
load_dotenv()



# Initialize once
sms_client = SMSService(
    username=os.getenv("AFRICASTALKING_USERNAME", "sandbox"),
    api_key=os.getenv("AFRICASTALKING_API_KEY")
)



def process_complete_advisory(message_id, phone_number):
    """
    MAIN ORCHESTRATOR FUNCTION - Handles the complete advisory workflow.
    This is the only function that should be called from routes.
    
    Args:
        message_id (str): Advisory message ID
        title (str): Advisory title
        secret_key (str): Secret key for SMC
        farmer_id (str): Farmer ID
        phone_number (str): Farmer's phone number
        
    Returns:
        dict: Complete response with success/failure and all details
    """
    try:
        

        # Step 0A: Get farmer ID from database using phone number
        farmer_success, farmer_result = get_farmer_id(phone_number)
        if not farmer_success:
            return {
                'success': False,
                'error': farmer_result,
                'step': 'FARMER_LOOKUP'
            }
        
        farmer_id = farmer_result
        print(f"✅ Found farmer ID: {farmer_id}")
        
        # Step 0B: Get secret key from database using phone number
        from ..USSD.utils import get_secret_key_by_phone
        
        secret_key = get_secret_key_by_phone(phone_number)
        if not secret_key:
            return {
                'success': False,
                'error': f'No secret key found for phone number: {phone_number}',
                'step': 'SECRET_KEY_LOOKUP'
            }
        
        print(f"✅ Found farmer with secret key")
        
        # Step 0C: Get advisory title from database
        advisory_success, advisory_result = get_advisory_title(message_id)
        if not advisory_success:
            return {
                'success': False,
                'error': advisory_result,
                'step': 'ADVISORY_LOOKUP'
            }
        
        title = advisory_result
        print(f"✅ Found advisory title: {title}")
        

        # Step 1: Send to SMC
        smc_response = send_to_smc(message_id, secret_key)
        if smc_response is None:
            return {
                'success': False,
                'error': 'Failed to communicate with SMC service',
                'step': 'SMC_PROCESSING'
            }
        
        # Extract verification code from SMC response
        verification_code = smc_response.get('vc')
        if not verification_code:
            return {
                'success': False,
                'error': 'No verification code received from SMC',
                'step': 'SMC_PROCESSING'
            }
        
        print(f"SMC processing successful. VC: {verification_code}")
        
        # Step 2: Craft SMS message
        sms_message = craft_sms(title, verification_code)
        print(f"SMS crafted for {phone_number}: {sms_message}")
        
        # Step 3: Send SMS to farmer
        sms_result = send_sms_to_farmer(phone_number, sms_message)
        if not sms_result['success']:
            return {
                'success': False,
                'error': sms_result['error'],
                'step': 'SMS_SENDING'
            }
        
        # Success - return complete result
        return {
            'success': True,
            'message': 'Advisory processed and SMS sent successfully',
            'verification_code': verification_code,
            'farmer_id': farmer_id,
            'phone_number': phone_number,
            'sms_content': sms_message,
            'sms_status': 'sent'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error in advisory processing: {str(e)}',
            'step': 'GENERAL_ERROR'
        }
    

def send_to_smc(message_id, secret_key):
    """
    Send message ID and secret key to SMC service via POST request.
    
    Args:
        message_id (str): The message/advisory ID to send
        secret_key (str): The secret key for authentication
        
    Returns:
        dict: Response from SMC API containing verification code (vc)
        None: If request fails
    """
    try:
        # SMC endpoint URL - replace with actual URL later
        smc_url = "http://localhost:5001/get-vc" # Dummy URL
        
        # Prepare payload - ensure secret_key is converted to string for JSON
        if isinstance(secret_key, bytes):
            secret_key_str = secret_key.decode('utf-8')
        else:
            secret_key_str = str(secret_key)
            
        payload = {
            "message_id": message_id,
            "secret_key": secret_key_str
        }
        
        # Headers for the request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('SMC_API_KEY')}"
        }
        
        # Send POST request to SMC
        response = requests.post(
            smc_url, 
            json=payload, 
            headers=headers,
            timeout=30  # 30 second timeout
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Return the JSON response (should contain {"vc": vc})
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error sending to SMC: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def craft_sms(title, vc):
    """
    Craft an SMS message with title, verification code, and USSD code.
    
    Args:
        title (str): The advisory title/subject
        vc (str): Verification code from SMC
        
    Returns:
        str: Formatted SMS message ready to send
    """
    # Get USSD code from environment variables
    ussd_code = os.getenv('USSD_CODE', 'DEFAULT_USSD')
    
    # Format: Title, VC, then USSD code with VC
    sms_message = (
    f"{title},\n"
    f"This is your verification code: {vc}\n"
    f"Dial {ussd_code}{vc}# to verify."
)
    
    return sms_message


def send_sms_to_farmer(phone_number, sms_message):
    """
    Send SMS to farmer using Africa's Talking API.
    Currently a dummy function - will be replaced with actual API integration.
    
    Args:
        phone_number (str): Farmer's phone number
        sms_message (str): SMS message to send
        
    Returns:
        dict: Success/failure response
    """
    try:
        # Dummy implementation - replace with Africa's Talking API
        print(f"📱 Sending the following SMS to farmer:")
        print(f"   📞 Phone: {phone_number}")
        print(f"   💬 Message: {sms_message}")
        print(f"   ✅ SMS sent successfully (dummy)")

        # # ADD THESE DEBUG PRINTS
        # print("🔍 Checking Africa's Talking Credentials:")
        # print(f"   Username: '{os.getenv('AFRICASTALKING_USERNAME', 'sandbox')}'")
        # print(f"   API Key: '{os.getenv('AFRICASTALKING_API_KEY')}'")
        # print(f"   API Key length: {len(os.getenv('AFRICASTALKING_API_KEY', '')) if os.getenv('AFRICASTALKING_API_KEY') else 0}")

        
        # print(f"📨 Sending SMS to {phone_number}...")

        # response = sms_client.send_sms(
        #     phone_number,
        #     sms_message,
        #     sender="12594"
        # )


        result = send_sms_celcom(phone_number, sms_message)
        print("✅ SMS sent:", result)
        
        return {
            'success': True,
            'message': 'SMS sent successfully',
            'phone_number': phone_number,
            'sms_content': sms_message
        }
        
    except Exception as e:
        print(f"❌ Error sending SMS: {e}")
        return {
            'success': False,
            'error': f'Failed to send SMS: {str(e)}',
            'phone_number': phone_number
        }

def get_advisory_title(message_id):
    """
    Get advisory title from database using message ID.
    
    Args:
        message_id (str): Advisory message ID
        
    Returns:
        tuple: (success, title_or_error)
            - If success: (True, "Advisory Title")
            - If failure: (False, "Error message")
    """
    try:
        from ..models import Advisory
        from flask import current_app
        
        print(f"🔍 Looking up advisory title for message ID: {message_id}")
        
        with current_app.app_context():
            # Try to convert message_id to integer
            try:
                advisory_id = int(message_id)
            except ValueError:
                return False, f"Invalid message_id format: {message_id} (must be integer)"
            
            # Query the database for advisory
            advisory = Advisory.query.get(advisory_id)
            
            if not advisory:
                return False, f"No advisory found with ID: {message_id}"
            
            print(f"✅ Found advisory: {advisory.title}")
            return True, advisory.title
                
    except Exception as e:
        print(f"❌ Error getting advisory title: {str(e)}")
        return False, f"Database error while getting advisory: {str(e)}"


def get_farmer_id(phone_number):
    """
    Get farmer ID from database using phone number.
    
    Args:
        phone_number (str): Farmer's phone number
        
    Returns:
        tuple: (success, farmer_id_or_error)
            - If success: (True, farmer_id)
            - If failure: (False, "Error message")
    """
    try:
        from ..models import Farmer
        from flask import current_app
        
        print(f"🔍 Looking up farmer ID for phone: {phone_number}")
        
        with current_app.app_context():
            # Query the database for farmer
            farmer = Farmer.query.filter_by(phone=phone_number).first()
            
            if not farmer:
                return False, f"No farmer found with phone number: {phone_number}"
            
            print(f"✅ Found farmer ID: {farmer.id}")
            return True, farmer.id
                
    except Exception as e:
        print(f"❌ Error getting farmer ID: {str(e)}")
        return False, f"Database error while getting farmer: {str(e)}"

