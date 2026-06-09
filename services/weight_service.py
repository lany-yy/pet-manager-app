"""
体重记录业务逻辑模块
"""
from typing import List, Optional
from datetime import date

from database import DatabaseHelper, get_db_manager
from models.weight import WeightRecord


class WeightService:
    """体重记录服务类"""

    def __init__(self):
        """初始化体重服务"""
        db_manager = get_db_manager()
        self.db_helper = DatabaseHelper(db_manager)

    def add_weight(self, pet_id: int, weight: float, record_date: date = None) -> WeightRecord:
        """
        添加体重记录

        Args:
            pet_id: 宠物ID
            weight: 体重（kg）
            record_date: 记录日期

        Returns:
            WeightRecord: 新创建的体重记录
        """
        if record_date is None:
            record_date = date.today()

        weight_id = self.db_helper.insert_weight(pet_id, weight, record_date)
        return self.get_weight_by_id(weight_id)

    def get_weight_by_id(self, weight_id: int) -> Optional[WeightRecord]:
        """
        根据ID获取体重记录

        Args:
            weight_id: 体重记录ID

        Returns:
            Optional[WeightRecord]: 体重记录对象
        """
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM weight_records WHERE id = ?', (weight_id,))
        row = cursor.fetchone()
        return WeightRecord.from_dict(dict(row)) if row else None

    def get_weights_by_pet(self, pet_id: int, limit: int = None) -> List[WeightRecord]:
        """
        获取某宠物的体重记录

        Args:
            pet_id: 宠物ID
            limit: 限制返回数量

        Returns:
            List[WeightRecord]: 体重记录列表
        """
        weights_data = self.db_helper.get_weights_by_pet(pet_id, limit)
        return [WeightRecord.from_dict(data) for data in weights_data]

    def get_latest_weight(self, pet_id: int) -> Optional[float]:
        """
        获取宠物最新体重

        Args:
            pet_id: 宠物ID

        Returns:
            Optional[float]: 最新体重
        """
        return self.db_helper.get_latest_weight(pet_id)

    def delete_weight(self, weight_id: int) -> bool:
        """
        删除体重记录

        Args:
            weight_id: 体重记录ID

        Returns:
            bool: 是否删除成功
        """
        return self.db_helper.delete_weight(weight_id)

    def get_weight_trend(self, pet_id: int, months: int = 6) -> List[dict]:
        """
        获取体重趋势数据（用于绘图）

        Args:
            pet_id: 宠物ID
            months: 月份范围

        Returns:
            List[dict]: 趋势数据 [{'date': date, 'weight': float}]
        """
        weights = self.get_weights_by_pet(pet_id)
        # 转换日期为字符串便于JSON序列化
        return [
            {'date': w.date.isoformat(), 'weight': w.weight}
            for w in weights
            if w.date
        ]
