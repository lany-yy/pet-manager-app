"""
提醒事项实体类
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Reminder:
    """提醒事项实体类"""

    id: Optional[int] = None
    pet_id: int = 0
    title: str = ""
    due_date: Optional[date] = None
    type: str = "other"  # 'vaccine', 'deworm', 'bath', 'other'
    is_completed: bool = False
    created_at: Optional[datetime] = None

    # 提醒类型选项
    REMINDER_TYPES = [
        ("vaccine", "疫苗接种"),
        ("deworm", "驱虫"),
        ("bath", "洗澡"),
        ("other", "其他")
    ]

    @property
    def type_display(self) -> str:
        """获取类型显示文本"""
        type_map = dict(self.REMINDER_TYPES)
        return type_map.get(self.type, "其他")

    @property
    def is_overdue(self) -> bool:
        """是否已过期"""
        if self.due_date and not self.is_completed:
            return date.today() > self.due_date
        return False

    @property
    def days_until_due(self) -> Optional[int]:
        """距离到期还有多少天"""
        if self.due_date:
            delta = self.due_date - date.today()
            return delta.days
        return None

    @property
    def status_display(self) -> str:
        """获取状态显示文本"""
        if self.is_completed:
            return "已完成"
        if self.is_overdue:
            return f"已逾期{abs(self.days_until_due)}天"
        elif self.days_until_due is not None:
            if self.days_until_due == 0:
                return "今日到期"
            elif self.days_until_due == 1:
                return "明日到期"
            elif self.days_until_due <= 7:
                return f"还有{self.days_until_due}天到期"
            return "即将到期"
        return "未知"

    @property
    def due_date_display(self) -> str:
        """获取到期日期显示文本"""
        if self.due_date:
            return self.due_date.strftime("%Y年%m月%d日")
        return "未知"

    @property
    def urgency_level(self) -> int:
        """
        获取紧急程度等级
        0: 已完成
        1: 已逾期
        2: 今日到期
        3: 3天内到期
        4: 7天内到期
        5: 未来
        """
        if self.is_completed:
            return 0
        if self.is_overdue:
            return 1
        days = self.days_until_due
        if days is not None:
            if days == 0:
                return 2
            elif days <= 3:
                return 3
            elif days <= 7:
                return 4
        return 5

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'title': self.title,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'type': self.type,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Reminder':
        """从字典创建实例"""
        if isinstance(data.get('due_date'), str):
            data['due_date'] = date.fromisoformat(data['due_date'])
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
