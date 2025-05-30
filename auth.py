import hashlib
import hmac

def hash_password(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def verify_password(senha, senha_hash):
    return hmac.compare_digest(hash_password(senha), senha_hash)