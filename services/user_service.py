import hashlib
from database import get_db_manager, DatabaseHelper

class UserService:
    def __init__(self):
        db_manager = get_db_manager()
        self.db_helper = DatabaseHelper(db_manager)

    def hash_password(self, password):
        return hashlib.md5(password.encode()).hexdigest()

    def register_user(self, username, password, email=None):
        if self.is_username_exists(username):
            return False, '用户名已存在'
        
        hashed_password = self.hash_password(password)
        try:
            conn = self.db_helper._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password, email)
                VALUES (?, ?, ?)
            ''', (username, hashed_password, email))
            conn.commit()
            return True, '注册成功'
        except Exception as e:
            return False, str(e)

    def login_user(self, username, password):
        hashed_password = self.hash_password(password)
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, email FROM users
            WHERE username = ? AND password = ?
        ''', (username, hashed_password))
        result = cursor.fetchone()
        
        if result:
            user = {
                'id': result[0],
                'username': result[1],
                'email': result[2]
            }
            return True, '登录成功', user
        return False, '用户名或密码错误', None

    def is_username_exists(self, username):
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        return cursor.fetchone() is not None

    def get_user_by_id(self, user_id):
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'email': result[2]
            }
        return None