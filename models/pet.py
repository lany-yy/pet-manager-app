"""
宠物实体类
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Pet:
    """宠物实体类"""

    id: Optional[int] = None
    name: str = ""
    type: str = "dog"  # 'cat' 或 'dog'
    breed: str = ""
    birthday: Optional[date] = None
    gender: str = "unknown"  # 'male', 'female', 'unknown'
    avatar_path: Optional[str] = None
    created_at: Optional[datetime] = None

    # 计算属性
    @property
    def age(self) -> Optional[int]:
        """计算年龄（岁）"""
        if self.birthday:
            today = date.today()
            age = today.year - self.birthday.year
            # 减去生日尚未到来的年份
            if (today.month, today.day) < (self.birthday.month, self.birthday.day):
                age -= 1
            return age
        return None

    @property
    def age_months(self) -> Optional[int]:
        """计算月龄"""
        if self.birthday:
            today = date.today()
            months = (today.year - self.birthday.year) * 12 + (today.month - self.birthday.month)
            if today.day < self.birthday.day:
                months -= 1
            return months
        return None

    @property
    def type_display(self) -> str:
        """获取类型显示文本"""
        return "猫咪" if self.type == "cat" else "狗狗"

    @property
    def gender_display(self) -> str:
        """获取性别显示文本"""
        gender_map = {"male": "公", "female": "母", "unknown": "未知"}
        return gender_map.get(self.gender, "未知")

    @property
    def age_display(self) -> str:
        """获取年龄显示文本"""
        if self.age is None:
            return "未知"
        if self.age == 0:
            months = self.age_months
            if months and months > 0:
                return f"{months}个月"
            return "幼年"
        return f"{self.age}岁"

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'breed': self.breed,
            'birthday': self.birthday.isoformat() if self.birthday else None,
            'gender': self.gender,
            'avatar_path': self.avatar_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Pet':
        """从字典创建实例"""
        if isinstance(data.get('birthday'), str):
            data['birthday'] = date.fromisoformat(data['birthday'])
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
