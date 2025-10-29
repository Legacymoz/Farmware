from flask import request, Blueprint
from .SMS.utils import process_complete_advisory
from .USSD.utils import verify_full_message
import os

routes_bp = Blueprint('routes', __name__)



@routes_bp.route('/send-advisory', methods=['POST'])
def send_advisory():
    """
    Endpoint to send an advisory to the SMC then a farmer.

    their is another route called /begin, which calls it, it will pass the message ID, title, the Famers ID , Secret Key and Phone number
    
    """
    #Extract values from the request JSON data
    try:
        data = request.get_json()
        
        # Extract required fields
        message_id = data.get('message_id')  # Advisory ID
        title = data.get('title')
        farmer_id = data.get('farmer_id')
        secret_key = data.get('secret_key')
        phone_number = data.get('phone_number')
        
        # Basic validation - check if all required fields are present
        if not all([message_id, title, farmer_id, secret_key, phone_number]):
            return {
                'error': 'Missing required fields',
                'required': ['message_id', 'title', 'farmer_id', 'secret_key', 'phone_number']
            }, 400
        

          # Process the complete advisory workflow with ONE function call
        result = process_complete_advisory(message_id, title, secret_key, farmer_id, phone_number)
        
        # Return result
        if result['success']:
            return result, 200
        else:
            return result, 500
            
    except Exception as e:
        return {'error': 'Invalid JSON data', 'message': str(e)}, 400
    


@routes_bp.route('/verify-advisory', methods=['POST'])
def verify_advisory():
    """
    Internal endpoint to verify advisory message ID.
    Extracts VC and handles verification logic.
    """
    try:
        data = request.get_json()
        
        # Extract required fields
        phone_number = data.get('phone_number')
        service_code = data.get('service_code')  # Will extract VC from here
        session_id = data.get('session_id', '')
        
        # Basic validation
        if not all([phone_number, service_code]):
            return {
                'error': 'Missing required fields',
                'required': ['phone_number', 'service_code']
            }, 400
        
        response = verify_full_message(phone_number, service_code)
        
        # Return the actual response from verify_full_message
        if response.get('success'):
            return response, 200
        else:
            return response, 500
        
    except Exception as e:
        return {
            'error': 'Verification failed',
            'message': str(e)
        }, 500



@routes_bp.route('/ussd-callback', methods=['POST'])
def ussd_callback():
    """
    USSD callback that immediately responds to user and processes verification asynchronously.
    This ensures the user gets immediate feedback while the verification happens in the background.
    """
    try:
        data = request.form
        
        session_id = data.get('sessionId')
        service_code = data.get('serviceCode')
        phone_number = data.get('phoneNumber')
        
        if not all([session_id, service_code, phone_number]):
            return "END Sorry, invalid request parameters.", 200
        
        # Start background verification task
        import threading
        
        def background_verification():
            """Background task to handle verification without blocking USSD response"""
            try:
                # Process verification in background
                response = verify_full_message(phone_number, service_code)
                if response.get('success'):
                    print(f"✅ Background verification successful for {phone_number}")
                else:
                    print(f"❌ Background verification failed: {response.get('error')}")
            except Exception as e:
                print(f"❌ Error in background verification: {e}")
        
        # Start the background thread
        thread = threading.Thread(target=background_verification)
        thread.daemon = True  # Thread will die when main program exits
        thread.start()
        
        # Immediately respond to user - don't wait for verification
        return "END Thank you! You will receive your full message shortly.", 200
    
    except Exception as e:
        print(f"❌ Error in USSD callback: {e}")
        return "END Sorry, there was an error processing your request.", 200