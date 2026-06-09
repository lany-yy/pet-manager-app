"""
驱虫记录业务逻辑模块
"""
from typing import List, Optional
from datetime import date

from database import DatabaseHelper, get_db_manager


class DewormService:
    """驱虫记录服务类"""

    def __init__(self):
        """初始化驱虫服务"""
        db_manager = get_db_manager()
        self.db_helper = DatabaseHelper(db_manager)

    def add_deworm_record(self, pet_id: int, deworm_type: str, deworm_date: date,
                          next_due: date = None, notes: str = None) -> int:
        """
        添加驱虫记录

        Args:
            pet_id: 宠物ID
            deworm_type: 驱虫类型（体内/体外/内外同驱）
            deworm_date: 驱虫日期
            next_due: 下次驱虫日期
            notes: 备注

        Returns:
            int: 新创建的记录ID
        """
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO deworm_records (pet_id, deworm_type, date, next_due, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (pet_id, deworm_type, deworm_date, next_due, notes))
        conn.commit()
        
        record_id = cursor.lastrowid

        # 如果有下次日期，创建提醒
        if next_due:
            self._create_reminder(pet_id, deworm_type, next_due)

        return record_id

    def get_deworm_record_by_id(self, record_id: int) -> Optional[dict]:
        """
        根据ID获取驱虫记录

        Args:
            record_id: 记录ID

        Returns:
            Optional[dict]: 驱虫记录
        """
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM deworm_records WHERE id = ?', (record_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_deworm_records_by_pet(self, pet_id: int) -> List[dict]:
        """
        获取某宠物的驱虫记录

        Args:
            pet_id: 宠物ID

        Returns:
            List[dict]: 驱虫记录列表
        """
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM deworm_records WHERE pet_id = ? ORDER BY date DESC',
            (pet_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def delete_deworm_record(self, record_id: int) -> bool:
        """
        删除驱虫记录

        Args:
            record_id: 记录ID

        Returns:
            bool: 是否删除成功
        """
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM deworm_records WHERE id = ?', (record_id,))
        conn.commit()
        return cursor.rowcount > 0

    def _create_reminder(self, pet_id: int, deworm_type: str, next_due: date):
        """
        创建驱虫提醒

        Args:
            pet_id: 宠物ID
            deworm_type: 驱虫类型
            next_due: 下次日期
        """
        title = f"驱虫提醒：{deworm_type}"
        self.db_helper.insert_reminder(pet_id, title, next_due, 'deworm')
