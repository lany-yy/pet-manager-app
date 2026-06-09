"""
体重记录实体类
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class WeightRecord:
    """体重记录实体类"""

    id: Optional[int] = None
    pet_id: int = 0
    weight: float = 0.0
    date: Optional[date] = None
    created_at: Optional[datetime] = None

    @property
    def weight_display(self) -> str:
        """获取体重显示文本"""
        return f"{self.weight:.1f}kg"

    @property
    def date_display(self) -> str:
        """获取日期显示文本"""
        if self.date:
            return self.date.strftime("%Y年%m月%d日")
        return "未知"

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'weight': self.weight,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WeightRecord':
        """从字典创建实例"""
        if isinstance(data.get('date'), str):
            data['date'] = date.fromisoformat(data['date'])
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
