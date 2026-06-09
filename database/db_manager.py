"""
数据库连接与表结构创建模块
负责初始化SQLite数据库并创建所有表结构
"""
import sqlite3
import os
from datetime import datetime


class DatabaseManager:
    """数据库管理器，负责数据库连接和表结构初始化"""

    def __init__(self, db_path=None):
        """
        初始化数据库管理器

        Args:
            db_path: 数据库文件路径，默认为当前目录下的pet_manager.db
        """
        if db_path is None:
            # 获取当前应用目录
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(current_dir, 'pet_manager.db')

        self.db_path = db_path
        self.conn = None

    def get_connection(self):
        """
        获取数据库连接

        Returns:
            sqlite3.Connection: 数据库连接对象
        """
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def init_tables(self):
        """初始化所有数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 0. 用户表 (users)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 1. 宠物表 (pets)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('cat', 'dog')),
                breed TEXT,
                birthday DATE,
                gender TEXT CHECK(gender IN ('male', 'female', 'unknown')),
                avatar_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. 疫苗记录表 (vaccines)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vaccines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                vaccine_name TEXT NOT NULL,
                date DATE NOT NULL,
                next_due DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
            )
        ''')

        # 3. 体重记录表 (weight_records)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weight_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                weight REAL NOT NULL,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
            )
        ''')

        # 4. 喂食记录表 (feeding_records)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feeding_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                food_type TEXT,
                amount REAL,
                time TIME,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
            )
        ''')

        # 5. 驱虫记录表 (deworm_records)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deworm_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                deworm_type TEXT CHECK(deworm_type IN ('体内', '体外', '内外同驱')),
                date DATE NOT NULL,
                next_due DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
            )
        ''')

        # 6. 提醒事项表 (reminders)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                due_date DATE NOT NULL,
                type TEXT CHECK(type IN ('vaccine', 'deworm', 'bath', 'other')),
                is_completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
            )
        ''')

        # 创建索引提高查询性能
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vaccines_pet_id ON vaccines(pet_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_weight_records_pet_id ON weight_records(pet_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feeding_records_pet_id ON feeding_records(pet_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_deworm_records_pet_id ON deworm_records(pet_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reminders_pet_id ON reminders(pet_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reminders_due_date ON reminders(due_date)')

        conn.commit()
        print(f"[DatabaseManager] 数据库初始化完成: {self.db_path}")

    def reset_database(self):
        """重置数据库，删除所有表并重新创建"""
        conn = self.get_connection()
        cursor = conn.cursor()

        tables = ['reminders', 'feeding_records', 'weight_records', 'vaccines', 'pets']
        for table in tables:
            cursor.execute(f'DROP TABLE IF EXISTS {table}')

        conn.commit()
        self.init_tables()
        print("[DatabaseManager] 数据库已重置")


# 全局数据库管理器实例
_db_manager = None


def get_db_manager():
    """获取全局数据库管理器实例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.init_tables()
    return _db_manager
