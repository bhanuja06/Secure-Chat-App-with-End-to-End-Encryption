from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import base64

def generate_rsa_keys():
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Generate public key
    public_key = private_key.public_key()
    
    # Serialize keys
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem.decode('utf-8'), public_pem.decode('utf-8')

def encrypt_message(public_key_pem, message):
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode('utf-8'),
        backend=default_backend()
    )
    
    encrypted = public_key.encrypt(
        message.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt_message(private_key_pem, encrypted_message):
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None,
        backend=default_backend()
    )
    
    decrypted = private_key.decrypt(
        base64.b64decode(encrypted_message.encode('utf-8')),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return decrypted.decode('utf-8')

def generate_aes_key():
    return Fernet.generate_key()

def encrypt_aes_key(public_key_pem, aes_key):
    return encrypt_message(public_key_pem, aes_key.decode('utf-8'))

def decrypt_aes_key(private_key_pem, encrypted_aes_key):
    return decrypt_message(private_key_pem, encrypted_aes_key).encode('utf-8')

def encrypt_with_aes(aes_key, message):
    f = Fernet(aes_key)
    return f.encrypt(message.encode('utf-8')).decode('utf-8')

def decrypt_with_aes(aes_key, encrypted_message):
    f = Fernet(aes_key)
    return f.decrypt(encrypted_message.encode('utf-8')).decode('utf-8')