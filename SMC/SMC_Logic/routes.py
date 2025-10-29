from flask import request, Blueprint, jsonify
from .crypto import generate_verification_code, regenerate_message_id 
import base64
import binascii

smc_routes_bp = Blueprint('smc_routes', __name__)


@smc_routes_bp.route('/get-vc', methods=['POST'])
def get_vc():
    """
    Endpoint to generate and return a verification code.
    
    Expected payload:
    {
        "message_id": "string",
        "secret_key": "bytes"
    }
    
    Returns:
    {
        "vc": "generated_verification_code"
    }
    """
    try:
        data = request.get_json()
        
        # Extract required fields
        message_id = data.get('message_id')
        secret_key = data.get('secret_key')
        
        # Basic validation
        if not all([message_id, secret_key]):
            return jsonify({
                'error': 'Missing required fields',
                'required': ['message_id', 'secret_key']
            }), 400
        
        # SMC receives string, converts to bytes
        secret_key_bytes = decode_secret_key(secret_key)
        verification_code = generate_verification_code(secret_key_bytes, message_id)

        
        
        return jsonify({
            "vc": verification_code
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Invalid request',
            'message': str(e)
        }), 400


@smc_routes_bp.route('/get-messageID', methods=['POST'])
def get_message_id():
    """
    Endpoint to retrieve message ID using verification code.
    
    Expected payload:
    {
        "vc": "verification_code",
        "secret_key": "string"
    }
    
    Returns:
    {
        "message_id": "retrieved_message_id"
    }
    """
    try:
        data = request.get_json()
        
        # Extract required fields
        vc = data.get('vc')
        secret_key = data.get('secret_key')
        
        # Basic validation
        if not all([vc, secret_key]):
            return jsonify({
                'error': 'Missing required fields',
                'required': ['vc', 'secret_key']
            }), 400
        
       
        secret_key_bytes = decode_secret_key(secret_key)
        message_id = regenerate_message_id ( secret_key_bytes, vc)
        
        # Placeholder response
        return jsonify({
            "message_id": message_id
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Invalid request',
            'message': str(e)
        }), 400


def decode_secret_key(secret_key_str: str) -> bytes:
    """
    Smart decoder that automatically detects and handles multiple secret key formats:
    - Base64 encoded strings (most common)
    - Hex encoded strings 
    - UTF-8 encoded raw bytes (your current format)
    
    Args:
        secret_key_str (str): Secret key as string in any supported format
        
    Returns:
        bytes: The actual secret key bytes for crypto operations
    """
    
    
    # Try Hex decoding
    try:
        # Hex validation: even length, only hex characters
        if (len(secret_key_str) % 2 == 0 and 
            all(c in '0123456789abcdefABCDEF' for c in secret_key_str)):
            
            decoded = bytes.fromhex(secret_key_str)
            print(f"✅ Decoded secret key from Hex format")
            return decoded
    except Exception:
        pass  # Not Hex, try next format
    
    # Try Base64 decoding first (most common alternative format)
    try:
        # Basic Base64 validation: length divisible by 4, valid characters
        if (len(secret_key_str) % 4 == 0 and 
            secret_key_str.replace('=', '').replace('+', '').replace('/', '').isalnum()):
            
            decoded = base64.b64decode(secret_key_str, validate=True)
            print(f"✅ Decoded secret key from Base64 format")
            return decoded
    except Exception:
        pass  # Not Base64, try next format
    
    
    
    # Fallback to UTF-8 encoding (your current method)
    try:
        decoded = secret_key_str.encode('utf-8')
        print(f"✅ Using secret key as UTF-8 string (current format)")
        return decoded
    except Exception as e:
        raise ValueError(f"Unable to decode secret key in any supported format: {e}")
        
    

    


'''
def decode_secret_key(secret_key_str: str) -> bytes:
    print(f"🔍 Trying to decode: '{secret_key_str}'")
    print(f"   Length: {len(secret_key_str)}")
    print(f"   Length % 2: {len(secret_key_str) % 2}")
    print(f"   Length % 4: {len(secret_key_str) % 4}")
    
    # Try Hex decoding
    try:
        print("   Testing HEX...")
        if (len(secret_key_str) % 2 == 0 and 
            all(c in '0123456789abcdefABCDEF' for c in secret_key_str)):
            print("   HEX validation passed, trying decode...")
            decoded = bytes.fromhex(secret_key_str)
            print(f"✅ Decoded secret key from Hex format")
            return decoded
        else:
            print("   HEX validation failed")
    except Exception as e:
        print(f"   HEX exception: {e}")
        pass
    
    # Try Base64 decoding
    try:
        print("   Testing BASE64...")
        if (len(secret_key_str) % 4 == 0 and 
            secret_key_str.replace('=', '').replace('+', '').replace('/', '').isalnum()):
            print("   BASE64 validation passed, trying decode...")
            decoded = base64.b64decode(secret_key_str, validate=True)
            print(f"✅ Decoded secret key from Base64 format")
            return decoded
        else:
            print("   BASE64 validation failed")
    except Exception as e:
        print(f"   BASE64 exception: {e}")
        pass
    
    # Fallback to UTF-8
    print("   Using UTF-8 fallback...")
    decoded = secret_key_str.encode('utf-8')
    print(f"✅ Using secret key as UTF-8 string (current format)")
    return decoded
'''