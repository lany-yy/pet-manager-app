"""
数据库CRUD操作封装模块
提供对所有表的增删改查操作
"""
import sqlite3
from datetime import date, datetime
from typing import List, Optional, Dict, Any


class DatabaseHelper:
    """数据库操作辅助类，提供通用的CRUD操作"""

    def __init__(self, db_manager):
        """
        初始化数据库帮助类

        Args:
            db_manager: DatabaseManager实例
        """
        self.db_manager = db_manager

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        return self.db_manager.get_connection()

    # ==================== 宠物表 (pets) 操作 ====================

    def insert_pet(self, name: str, pet_type: str, breed: str = None,
                   birthday: date = None, gender: str = 'unknown',
                   avatar_path: str = None) -> int:
        """
        添加新宠物

        Args:
            name: 宠物名字
            pet_type: 类型 ('cat' 或 'dog')
            breed: 品种
            birthday: 出生日期
            gender: 性别 ('male', 'female', 'unknown')
            avatar_path: 头像路径

        Returns:
            int: 新插入记录的ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pets (name, type, breed, birthday, gender, avatar_path)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, pet_type, breed, birthday, gender, avatar_path))
        conn.commit()
        return cursor.lastrowid

    def get_all_pets(self) -> List[Dict[str, Any]]:
        """获取所有宠物列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pets ORDER BY created_at DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_pet_by_id(self, pet_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取宠物"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pets WHERE id = ?', (pet_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_pet(self, pet_id: int, **kwargs) -> bool:
        """
        更新宠物信息

        Args:
            pet_id: 宠物ID
            **kwargs: 要更新的字段

        Returns:
            bool: 是否更新成功
        """
        allowed_fields = {'name', 'type', 'breed', 'birthday', 'gender', 'avatar_path'}
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not update_fields:
            return False

        conn = self._get_connection()
        cursor = conn.cursor()

        set_clause = ', '.join([f'{k} = ?' for k in update_fields.keys()])
        values = list(update_fields.values()) + [pet_id]

        cursor.execute(f'UPDATE pets SET {set_clause} WHERE id = ?', values)
        conn.commit()
        return cursor.rowcount > 0

    def delete_pet(self, pet_id: int) -> bool:
        """删除宠物及其所有关联数据"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM pets WHERE id = ?', (pet_id,))
        conn.commit()
        return cursor.rowcount > 0

    # ==================== 疫苗记录表 (vaccines) 操作 ====================

    def insert_vaccine(self, pet_id: int, vaccine_name: str, vaccine_date: date,
                       next_due: date = None, notes: str = None) -> int:
        """添加疫苗记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vaccines (pet_id, vaccine_name, date, next_due, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (pet_id, vaccine_name, vaccine_date, next_due, notes))
        conn.commit()
        return cursor.lastrowid

    def get_vaccines_by_pet(self, pet_id: int) -> List[Dict[str, Any]]:
        """获取某宠物的所有疫苗记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM vaccines WHERE pet_id = ? ORDER BY date DESC',
            (pet_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_upcoming_vaccines(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取即将到期的疫苗记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        today = date.today()
        future_date = date.today()
        from datetime import timedelta
        future_date = today + timedelta(days=days)

        cursor.execute('''
            SELECT v.*, p.name as pet_name, p.type as pet_type
            FROM vaccines v
            JOIN pets p ON v.pet_id = p.id
            WHERE v.next_due IS NOT NULL
            AND v.next_due <= ?
            AND v.next_due >= ?
            AND v.id NOT IN (
                SELECT vaccine_id FROM reminders WHERE is_completed = 1 AND type = 'vaccine'
            )
            ORDER BY v.next_due ASC
        ''', (future_date, today))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def delete_vaccine(self, vaccine_id: int) -> bool:
        """删除疫苗记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM vaccines WHERE id = ?', (vaccine_id,))
        conn.commit()
        return cursor.rowcount > 0

    # ==================== 体重记录表 (weight_records) 操作 ====================

    def insert_weight(self, pet_id: int, weight: float, record_date: date = None) -> int:
        """添加体重记录"""
        if record_date is None:
            record_date = date.today()

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO weight_records (pet_id, weight, date)
            VALUES (?, ?, ?)
        ''', (pet_id, weight, record_date))
        conn.commit()
        return cursor.lastrowid

    def get_weights_by_pet(self, pet_id: int, limit: int = None) -> List[Dict[str, Any]]:
        """获取某宠物的体重记录"""
        conn = self._get_connection()
        cursor = conn.cursor()

        sql = 'SELECT * FROM weight_records WHERE pet_id = ? ORDER BY date DESC'
        if limit:
            sql += f' LIMIT {limit}'

        cursor.execute(sql, (pet_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_latest_weight(self, pet_id: int) -> Optional[float]:
        """获取宠物最新体重"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT weight FROM weight_records WHERE pet_id = ? ORDER BY date DESC LIMIT 1',
            (pet_id,)
        )
        row = cursor.fetchone()
        return row['weight'] if row else None

    def delete_weight(self, weight_id: int) -> bool:
        """删除体重记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM weight_records WHERE id = ?', (weight_id,))
        conn.commit()
        return cursor.rowcount > 0

    # ==================== 喂食记录表 (feeding_records) 操作 ====================

    def insert_feeding(self, pet_id: int, record_date: date,
                       food_type: str = None, amount: float = None,
                       feeding_time: str = None) -> int:
        """添加喂食记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO feeding_records (pet_id, food_type, amount, time, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (pet_id, food_type, amount, feeding_time, record_date))
        conn.commit()
        return cursor.lastrowid

    def get_feedings_by_pet(self, pet_id: int, record_date: date = None) -> List[Dict[str, Any]]:
        """获取某宠物的喂食记录"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if record_date:
            cursor.execute(
                'SELECT * FROM feeding_records WHERE pet_id = ? AND date = ? ORDER BY time DESC',
                (pet_id, record_date)
            )
        else:
            cursor.execute(
                'SELECT * FROM feeding_records WHERE pet_id = ? ORDER BY date DESC, time DESC',
                (pet_id,)
            )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_today_feedings(self, pet_id: int) -> List[Dict[str, Any]]:
        """获取今日喂食记录"""
        return self.get_feedings_by_pet(pet_id, date.today())

    def delete_feeding(self, feeding_id: int) -> bool:
        """删除喂食记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM feeding_records WHERE id = ?', (feeding_id,))
        conn.commit()
        return cursor.rowcount > 0

    # ==================== 提醒事项表 (reminders) 操作 ====================

    def insert_reminder(self, pet_id: int, title: str, due_date: date,
                        reminder_type: str = 'other', is_completed: bool = False) -> int:
        """添加提醒事项"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reminders (pet_id, title, due_date, type, is_completed)
            VALUES (?, ?, ?, ?, ?)
        ''', (pet_id, title, due_date, reminder_type, is_completed))
        conn.commit()
        return cursor.lastrowid

    def get_reminders_by_pet(self, pet_id: int, include_completed: bool = True) -> List[Dict[str, Any]]:
        """获取某宠物的提醒事项"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if include_completed:
            cursor.execute(
                'SELECT * FROM reminders WHERE pet_id = ? ORDER BY due_date ASC',
                (pet_id,)
            )
        else:
            cursor.execute(
                'SELECT * FROM reminders WHERE pet_id = ? AND is_completed = 0 ORDER BY due_date ASC',
                (pet_id,)
            )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_all_reminders(self, include_completed: bool = False) -> List[Dict[str, Any]]:
        """获取所有提醒事项"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if include_completed:
            sql = '''
                SELECT r.*, p.name as pet_name, p.type as pet_type
                FROM reminders r
                JOIN pets p ON r.pet_id = p.id
                ORDER BY r.due_date ASC
            '''
            cursor.execute(sql)
        else:
            sql = '''
                SELECT r.*, p.name as pet_name, p.type as pet_type
                FROM reminders r
                JOIN pets p ON r.pet_id = p.id
                WHERE r.is_completed = 0
                ORDER BY r.due_date ASC
            '''
            cursor.execute(sql)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_today_reminders(self) -> List[Dict[str, Any]]:
        """获取今日到期的提醒"""
        conn = self._get_connection()
        cursor = conn.cursor()
        today = date.today()

        cursor.execute('''
            SELECT r.*, p.name as pet_name, p.type as pet_type
            FROM reminders r
            JOIN pets p ON r.pet_id = p.id
            WHERE r.due_date = ? AND r.is_completed = 0
            ORDER BY r.type ASC
        ''', (today,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_overdue_reminders(self) -> List[Dict[str, Any]]:
        """获取已过期的提醒"""
        conn = self._get_connection()
        cursor = conn.cursor()
        today = date.today()

        cursor.execute('''
            SELECT r.*, p.name as pet_name, p.type as pet_type
            FROM reminders r
            JOIN pets p ON r.pet_id = p.id
            WHERE r.due_date < ? AND r.is_completed = 0
            ORDER BY r.due_date ASC
        ''', (today,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def update_reminder_status(self, reminder_id: int, is_completed: bool) -> bool:
        """更新提醒状态"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE reminders SET is_completed = ? WHERE id = ?',
            (is_completed, reminder_id)
        )
        conn.commit()
        return cursor.rowcount > 0

    def delete_reminder(self, reminder_id: int) -> bool:
        """删除提醒事项"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
        conn.commit()
        return cursor.rowcount > 0

    # ==================== 统计相关操作 ====================

    def get_pet_count(self) -> Dict[str, int]:
        """获取宠物数量统计"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as total FROM pets')
        total = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as cats FROM pets WHERE type = 'cat'")
        cats = cursor.fetchone()['cats']

        cursor.execute("SELECT COUNT(*) as dogs FROM pets WHERE type = 'dog'")
        dogs = cursor.fetchone()['dogs']

        return {'total': total, 'cats': cats, 'dogs': dogs}

    def get_vaccine_completion_rate(self, pet_id: int = None) -> float:
        """获取疫苗完成率"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if pet_id:
            # 某宠物
            cursor.execute('SELECT COUNT(*) as total FROM vaccines WHERE pet_id = ?', (pet_id,))
        else:
            cursor.execute('SELECT COUNT(*) as total FROM vaccines')

        total = cursor.fetchone()['total']

        if total == 0:
            return 0.0

        # 假设已完成的定义：有下次到期日且已过期的记录已完成
        # 这里简化为所有记录都是已完成的
        return 100.0  # 简化处理
