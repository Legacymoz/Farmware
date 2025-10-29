import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def process_complete_advisory(message_id, title, secret_key, farmer_id, phone_number):
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
        print(f"Processing advisory {message_id} for farmer {farmer_id}")
        
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
    sms_message = f"{title}, {vc} {ussd_code}{vc}#"
    
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
        
        # TODO: Replace with actual Africa's Talking API call
        # Example future implementation:
        # import africastalking
        # africastalking.initialize(
        #     username=os.getenv('AFRICASTALKING_USERNAME'),
        #     api_key=os.getenv('AFRICASTALKING_API_KEY')
        # )
        # sms = africastalking.SMS
        # response = sms.send(sms_message, [phone_number])
        
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

