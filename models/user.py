class User:
    def __init__(self, id=None, username=None, password=None, email=None, created_at=None):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'created_at': self.created_at
        }