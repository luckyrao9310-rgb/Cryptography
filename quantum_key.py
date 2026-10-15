import secrets

def generate_quantum_key(length=32):
    key = secrets.token_bytes(length)
    return key

if __name__ == "__main__":
    key = generate_quantum_key()
    print(f"Simulated Quantum Key: {key.hex()}")
