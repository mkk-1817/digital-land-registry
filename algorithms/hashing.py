import hashlib
import hmac
import base64

def generate_document_hash(content, secret_key='land_registry_secret'):
    """
    Generates a secure hash for document content.
    
    Args:
        content: Document content (bytes or string)
        secret_key: Secret key for HMAC
        
    Returns:
        Hash string
    """
    if isinstance(content, str):
        content = content.encode('utf-8')
    
    # Use HMAC-SHA256 for secure hashing
    h = hmac.new(secret_key.encode('utf-8'), content, hashlib.sha256)
    return base64.b64encode(h.digest()).decode('utf-8')

def verify_document_hash(hash_value, content, secret_key='land_registry_secret'):
    """
    Verifies if a document hash matches the content.
    
    Args:
        hash_value: Hash to verify
        content: Document content
        secret_key: Secret key for HMAC
        
    Returns:
        Boolean indicating if hash is valid
    """
    calculated_hash = generate_document_hash(content, secret_key)
    return hmac.compare_digest(calculated_hash, hash_value)

def hash_property_data(property_data):
    """
    Creates a hash of property data for verification.
    
    Args:
        property_data: Dictionary containing property data
        
    Returns:
        Hash string
    
    """
    # Create a canonical representation of the property data
    canonical = f"{property_data['registrationNumber']}|{property_data['location']}|{property_data['area']}|{property_data['ownerId']}"
    return generate_document_hash(canonical)
