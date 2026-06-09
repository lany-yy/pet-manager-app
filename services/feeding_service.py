"""
喂食记录业务逻辑模块
"""
from typing import List, Optional
from datetime import date, time

from database import DatabaseHelper, get_db_manager


class FeedingService:
    """喂食记录服务类"""

    def __init__(self):
        """初始化喂食服务"""
        db_manager = get_db_manager()
        self.db_helper = DatabaseHelper(db_manager)

    def add_feeding(self, pet_id: int, record_date: date,
                    food_type: str = None, amount: float = None,
                    feeding_time: time = None) -> int:
        """
        添加喂食记录

        Args:
            pet_id: 宠物ID
            record_date: 记录日期
            food_type: 食物类型
            amount: 喂食量（克）
            feeding_time: 喂食时间

        Returns:
            int: 新创建的记录ID
        """
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()
        
        time_str = feeding_time.strftime("%H:%M:%S") if feeding_time else None
        
        cursor.execute('''
            INSERT INTO feeding_records (pet_id, food_type, amount, time, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (pet_id, food_type, amount, time_str, record_date))
        conn.commit()
        
        return cursor.lastrowid

    def get_feeding_by_id(self, feeding_id: int) -> Optional[dict]:
        """
        根据ID获取喂食记录

        Args:
            feeding_id: 记录ID

        Returns:
            Optional[dict]: 喂食记录
        """
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM feeding_records WHERE id = ?', (feeding_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_feedings_by_pet(self, pet_id: int, record_date: date = None) -> List[dict]:
        """
        获取某宠物的喂食记录

        Args:
            pet_id: 宠物ID
            record_date: 记录日期（可选）

        Returns:
            List[dict]: 喂食记录列表
        """
        conn = self.db_helper._get_connection()
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

    def get_today_feedings(self, pet_id: int) -> List[dict]:
        """
        获取今日喂食记录

        Args:
            pet_id: 宠物ID

        Returns:
            List[dict]: 今日喂食记录
        """
        return self.get_feedings_by_pet(pet_id, date.today())

    def get_total_amount_today(self, pet_id: int) -> float:
        """
        获取今日喂食总量

        Args:
            pet_id: 宠物ID

        Returns:
            float: 今日喂食总量（克）
        """
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT COALESCE(SUM(amount), 0) FROM feeding_records WHERE pet_id = ? AND date = ?',
            (pet_id, date.today())
        )
        result = cursor.fetchone()
        return float(result[0]) if result[0] else 0.0

    def delete_feeding(self, feeding_id: int) -> bool:
        """
        删除喂食记录

        Args:
            feeding_id: 记录ID

        Returns:
            bool: 是否删除成功
        """
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM feeding_records WHERE id = ?', (feeding_id,))
        conn.commit()
        return cursor.rowcount > 0
