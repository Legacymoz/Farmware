from ff3 import FF3Cipher
import hashlib
import hmac

# ----------------------------------------------------
# MODULE PURPOSE: Format-Preserving Encryption (FPE) for Verification Codes
# ----------------------------------------------------
# This module provides stateless encryption/decryption functions using the FF3-1 algorithm.
# It converts a short Message ID (the input, e.g., "78321") into a short, fixed-length Verification Code (the output, e.g., "931084"), and vice-versa, using the farmer's secret key.

# --- Configuration Constants ---
# MAX_MESSAGE_LENGTH (int): Defines the fixed length of the Verification Code (VC). 
# This must be the maximum length of your Message ID, up to 6 digits for the prototype.
# CRITICAL: If a Message ID longer than 6 is used, this constant MUST be increased.
MAX_MESSAGE_LENGTH = 6 

# --- Private Key Derivation Helper (Cryptographic Firewall) ---

# The Master Key is the single secret key (K_f) retrieved from the database. i.e the farmer's secret key.
# It serves as the secure seed for all operations.

def derive_ff3_components(master_key: bytes) -> tuple[bytes, bytes]:
    """
    Derives the specialized 16-byte FF3 Key and 8-byte Tweak from the single  Master Key using HMAC-SHA256. 
    This ensures the two required FF3 inputs are cryptographically independent for added security for the farmer's secret key.
    """
    
    # 1. Derive the 16-byte FF3 Key (128 bits)
    # The 'FF3_KEY...' context string ensures this output is unique.
    key_hash = hmac.new(master_key, b'FF3_KEY_DERIVATION_CONTEXT', hashlib.sha256).digest()
    ff3_key = key_hash[:16] 

    # 2. Derive the 8-byte Tweak (64 bits)
    # A different context string ensures this output is cryptographically separate from the key.
    tweak_hash = hmac.new(master_key, b'FF3_TWEAK_DERIVATION_CONTEXT', hashlib.sha256).digest()
    ff3_tweak = tweak_hash[:8] 
    
    return ff3_key, ff3_tweak

def get_cipher(farmer_key: bytes) -> FF3Cipher:
    """
    Initializes and returns the FF3Cipher object using derived key components.
    The 'farmer_key' (Master Key) is transformed into the required FF3 components on-the-fly to maintain security.
    """
    ff3_key, ff3_tweak = derive_ff3_components(farmer_key)

    # FF3Cipher requires key/tweak inputs to be hexadecimal strings
    key_hex = ff3_key.hex()
    tweak_hex = ff3_tweak.hex()
    
    # radix=10 enforces numeric-only VCs (digits 0-9)
    return FF3Cipher(key_hex, tweak_hex, radix=10)

def generate_verification_code(farmer_key: bytes, message_id: str) -> str:
    """
    Encrypts a Message ID (max 6 digits) into a 6-digit VC.
    """
    # The cipher is instantiated on-the-fly for each operation
    cipher = get_cipher(farmer_key)
    
    if not message_id.isdigit():
        raise ValueError("Input Message ID must be numeric.")
    
    # Validation: Fails if the Message ID is too long for the 6-digit VC.
    if len(message_id) > MAX_MESSAGE_LENGTH:
        raise ValueError(f"Message ID length ({len(message_id)}) exceeds maximum allowed length of {MAX_MESSAGE_LENGTH}.")

    # Padding: Zeros are added to the left (e.g., "12345" -> "012345") to meet the fixed 6-digit length required for FF3.
    padded_message_id = message_id.zfill(MAX_MESSAGE_LENGTH)
    
    # Encryption generates the VC
    verification_code = cipher.encrypt(padded_message_id)
    
    return verification_code

def regenerate_message_id(farmer_key: bytes, verification_code: str) -> str:
    """
    Decrypts the 6-digit VC back into the original Message ID.
    """
    # The cipher is instantiated on-the-fly for each operation
    cipher = get_cipher(farmer_key)
    
    if not verification_code.isdigit():
        raise ValueError("Verification code must be numeric.")

    # Validation: VC length must be exactly 6 digits for decryption to work.
    if len(verification_code) != MAX_MESSAGE_LENGTH:
        raise ValueError(f"Verification code must be exactly {MAX_MESSAGE_LENGTH} digits, got: {len(verification_code)}.")

    # Direct decryption recovers the original padded ID
    decrypted = cipher.decrypt(verification_code)
    
    # Unpadding: Leading zeros are removed (e.g., "012345" -> "12345") to restore the Message ID to its original length.
    message_id = decrypted.lstrip('0') or '0'
    
    return message_id