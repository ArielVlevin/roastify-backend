import uuid

def generate_id():
    return str(uuid.uuid4()).replace('-', '')[:16] 