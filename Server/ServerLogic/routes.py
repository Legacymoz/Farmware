from flask import request, Blueprint, jsonify, render_template
from .models import Advisory, Farmer
from .SMS.utils import process_complete_advisory
from .USSD.utils import verify_full_message
import os
from flask import current_app

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
        
        # Extract required fields from request
        message_id = data.get('message_id')
        phone_number = data.get('phone_number')
        
        # Validate required fields
        if not message_id or not phone_number:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: message_id and phone_number are required'
            }), 400
        
        print(f"📨 Processing advisory request:")
        print(f"   Message ID: {message_id}")
        print(f"   Phone Number: {phone_number}")
        
        # Process the complete advisory workflow
        result = process_complete_advisory(message_id, phone_number)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return {'error': 'Invalid JSON data', 'message': str(e)}, 400
    


@routes_bp.route('/verify-advisory', methods=['POST'])
def verify_advisory():
    """
    Internal endpoint to verify advisory message ID.
    Extracts VC and handles verification logic.
    """
    try:
        # print("Received request to /verify-advisory")
        data = request.get_json()
        # print("Request data:", data)
        
        # Extract required fields
        phone_number = data.get('phone_number')
        service_code = data.get('service_code')  # Will extract VC from here
        text = data.get('text', '')
        
        # Basic validation
        if not all([phone_number, service_code, text]):
            return {
                'error': 'Missing required fields',
                'required': ['phone_number', 'service_code', 'text']
            }, 400
        
        response = verify_full_message(phone_number, service_code, text)
        
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
        # print("Received USSD callback request")
        data = request.form
        
        
        session_id = data.get('sessionId')
        service_code = data.get('serviceCode')
        phone_number = data.get('phoneNumber')
        text= data.get('text', '')

        
        if not all([session_id, service_code, phone_number]):
            return "END Sorry, invalid request parameters.", 200
        
        # Start background verification task
        import threading
        import requests
        # print("Received USSD callback request, just out side the thread")
        def background_verification():
            """Background task to handle verification without blocking USSD response"""

            # print("Inside background verification thread, but before try block")
            try:
                # print("before Importing current_app")
                from flask import current_app
                # print("After Importing current_app")
                
                # Get the base URL for internal API calls
                base_url =  'http://localhost:5000'
                # print("After getting base_url")
                
                # Prepare payload for /verify-advisory endpoint
                payload = {
                    'phone_number': phone_number,
                    'service_code': service_code,
                    'session_id': session_id,
                    'text': text

                }
                # print("About to call /verify-advisory endpoint with payload:")
                
                # Call the /verify-advisory API internally
                response = requests.post(
                    f"{base_url}/verify-advisory",
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=30  # 30 second timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Background verification successful for {phone_number}")
                    print(f"📄 Response: {result}")
                else:
                    print(f"❌ Background verification failed with status {response.status_code}")
                    print(f"📄 Error: {response.text}")
                    
            except requests.exceptions.Timeout:
                print(f"⏰ Background verification timed out for {phone_number}")
            except requests.exceptions.ConnectionError:
                print(f"🔌 Connection error during background verification for {phone_number}")
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
    


@routes_bp.route('/')
def dashboard():
    """Render the main dashboard"""
    return render_template('dashboard.html')

@routes_bp.route('/api/farmers')
def get_farmers_api():
    """API endpoint to get farmers data"""
    try:
        farmers = Farmer.query.all()
        farmers_data = []
        
        for farmer in farmers:
            farmers_data.append({
                'id': farmer.id,
                'phone': farmer.phone,
                'secret_key_preview': farmer.secret_key[:10].decode('utf-8', errors='ignore') + '...',
                'created_at': farmer.created_at.isoformat() if farmer.created_at else None
            })
        
        return jsonify({
            'success': True,
            'farmers': farmers_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@routes_bp.route('/api/advisories')
def get_advisories_api():
    """API endpoint to get advisories data"""
    try:
        advisories = Advisory.query.all()
        advisories_data = []
        
        for advisory in advisories:
            advisories_data.append({
                'id': advisory.id,
                'title': advisory.title,
                'message': advisory.message,
                'created_at': advisory.created_at.isoformat() if advisory.created_at else None
            })
        
        return jsonify({
            'success': True,
            'advisories': advisories_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500