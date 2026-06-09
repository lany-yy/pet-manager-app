"""
喂食记录实体类
"""
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Optional


@dataclass
class FeedingRecord:
    """喂食记录实体类"""

    id: Optional[int] = None
    pet_id: int = 0
    food_type: str = "干粮"  # 干粮/湿粮/零食/其他
    amount: float = 0.0  # 单位：克
    time: Optional[time] = None
    date: Optional[date] = None
    created_at: Optional[datetime] = None

    # 食物类型选项
    FOOD_TYPES = ["干粮", "湿粮", "零食", "罐头", "生骨肉", "其他"]

    @property
    def food_type_display(self) -> str:
        """获取食物类型显示文本"""
        return self.food_type

    @property
    def amount_display(self) -> str:
        """获取喂食量显示文本"""
        if self.amount > 0:
            return f"{self.amount:.0f}g"
        return "未知"

    @property
    def date_display(self) -> str:
        """获取日期显示文本"""
        if self.date:
            return self.date.strftime("%Y年%m月%d日")
        return "未知"

    @property
    def time_display(self) -> str:
        """获取时间显示文本"""
        if self.time:
            return self.time.strftime("%H:%M")
        return "未知"

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'food_type': self.food_type,
            'amount': self.amount,
            'time': self.time.strftime("%H:%M:%S") if self.time else None,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FeedingRecord':
        """从字典创建实例"""
        if isinstance(data.get('date'), str):
            data['date'] = date.fromisoformat(data['date'])
        if isinstance(data.get('time'), str):
            data['time'] = time.fromisoformat(data['time'])
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
