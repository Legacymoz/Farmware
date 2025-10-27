from flask import request, Blueprint

routes_bp = Blueprint('routes', __name__)



@routes_bp.route('/advisory', methods=['POST'])
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
            
    except Exception as e:
        return {'error': 'Invalid JSON data'}, 400