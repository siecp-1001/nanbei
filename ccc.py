from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import base64

# Generate keys
private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
public_key = private_key.public_key()

# Export to raw public key bytes
raw_public_key = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)

# Export private key bytes (just the raw integer value)
raw_private_key = private_key.private_numbers().private_value.to_bytes(32, 'big')

# Encode in Base64 (URL-safe)
vapid_public_key = base64.urlsafe_b64encode(raw_public_key).decode('utf-8')
vapid_private_key = base64.urlsafe_b64encode(raw_private_key).decode('utf-8')

# Print values
print("WEBPUSH_SETTINGS = {")
print(f'    "VAPID_PUBLIC_KEY": "{vapid_public_key}",')
print(f'    "VAPID_PRIVATE_KEY": "{vapid_private_key}",')
print(f'    "VAPID_ADMIN_EMAIL": "admin@example.com"')
print("}")
