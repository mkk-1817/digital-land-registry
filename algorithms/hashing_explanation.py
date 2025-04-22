# Hashing Techniques for Document Verification
def explain_hashing():
    import hashlib
    import hmac
    import base64
    
    print("Hashing Techniques for Document Verification")
    print("-------------------------------------------")
    print("1. We use HMAC-SHA256 for secure document hashing")
    print("2. Each document's content is hashed with a secret key")
    print("3. The hash is stored alongside the document")
    print("4. When verifying, we recalculate the hash and compare")
    print("5. This ensures document integrity and authenticity")
    
    # Example
    print("\nExample:")
    document_content = "This is a land deed for Property #123 in Mumbai, owned by John Doe."
    secret_key = "land_registry_secret"
    
    print(f"Document content: {document_content}")
    print(f"Secret key: {secret_key}")
    
    # Generate hash
    def generate_hash(content, key):
        h = hmac.new(key.encode('utf-8'), content.encode('utf-8'), hashlib.sha256)
        return base64.b64encode(h.digest()).decode('utf-8')
    
    original_hash = generate_hash(document_content, secret_key)
    print(f"\nGenerated hash: {original_hash}")
    
    # Verify original document
    def verify_hash(content, hash_value, key):
        calculated_hash = generate_hash(content, key)
        return hmac.compare_digest(calculated_hash, hash_value)
    
    print("\nVerification tests:")
    
    # Test 1: Original document
    result = verify_hash(document_content, original_hash, secret_key)
    print(f"1. Original document verification: {'Success' if result else 'Failed'}")
    
    # Test 2: Tampered document
    tampered_content = document_content.replace("John Doe", "Jane Smith")
    result = verify_hash(tampered_content, original_hash, secret_key)
    print(f"2. Tampered document verification: {'Success' if result else 'Failed'}")
    
    # Test 3: Property data hashing
    property_data = {
        "registrationNumber": "REG123456",
        "location": "Mumbai, Maharashtra",
        "area": 1200,
        "ownerId": "USER789"
    }
    
    def hash_property_data(data):
        canonical = f"{data['registrationNumber']}|{data['location']}|{data['area']}|{data['ownerId']}"
        return generate_hash(canonical, secret_key)
    
    property_hash = hash_property_data(property_data)
    print(f"\nProperty data hash: {property_hash}")
    
    # Verify property data
    tampered_property = property_data.copy()
    tampered_property["ownerId"] = "USER456"  # Changed owner
    
    original_verified = hash_property_data(property_data) == property_hash
    tampered_verified = hash_property_data(tampered_property) == property_hash
    
    print(f"Original property verification: {'Success' if original_verified else 'Failed'}")
    print(f"Tampered property verification: {'Success' if tampered_verified else 'Failed'}")

explain_hashing()
