"""
疫苗记录实体类
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Vaccine:
    """疫苗记录实体类"""

    id: Optional[int] = None
    pet_id: int = 0
    vaccine_name: str = ""
    date: Optional[date] = None
    next_due: Optional[date] = None
    notes: str = ""
    created_at: Optional[datetime] = None

    # 预设疫苗名称选项
    PRESET_VACCINES = [
        "狂犬疫苗",
        "猫三联疫苗",
        "犬五联疫苗",
        "犬八联疫苗",
        "猫白血病疫苗",
        "犬窝咳疫苗",
        "钩端螺旋体疫苗",
        "弓形虫疫苗",
        "其他"
    ]

    @property
    def is_overdue(self) -> bool:
        """是否已过期"""
        if self.next_due:
            return date.today() > self.next_due
        return False

    @property
    def days_until_due(self) -> Optional[int]:
        """距离到期还有多少天"""
        if self.next_due:
            delta = self.next_due - date.today()
            return delta.days
        return None

    @property
    def status_display(self) -> str:
        """获取状态显示文本"""
        if self.is_overdue:
            return f"已过期{abs(self.days_until_due)}天"
        elif self.days_until_due is not None:
            if self.days_until_due <= 7:
                return f"还有{self.days_until_due}天到期"
            elif self.days_until_due <= 30:
                return f"还有{self.days_until_due}天到期"
            return "正常"
        return "无下次提醒"

    @property
    def date_display(self) -> str:
        """获取日期显示文本"""
        if self.date:
            return self.date.strftime("%Y年%m月%d日")
        return "未知"

    @property
    def next_due_display(self) -> str:
        """获取下次到期显示文本"""
        if self.next_due:
            return self.next_due.strftime("%Y年%m月%d日")
        return "无"

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'vaccine_name': self.vaccine_name,
            'date': self.date.isoformat() if self.date else None,
            'next_due': self.next_due.isoformat() if self.next_due else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Vaccine':
        """从字典创建实例"""
        if isinstance(data.get('date'), str):
            data['date'] = date.fromisoformat(data['date'])
        if isinstance(data.get('next_due'), str):
            data['next_due'] = date.fromisoformat(data['next_due'])
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
