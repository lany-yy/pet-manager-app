"""
日期工具模块
提供日期相关的辅助函数
"""
from datetime import date, datetime, timedelta
from typing import Optional


class DateHelper:
    """日期辅助工具类"""

    @staticmethod
    def calculate_age(birthday: date) -> int:
        """
        计算年龄（岁）

        Args:
            birthday: 出生日期

        Returns:
            int: 年龄
        """
        today = date.today()
        age = today.year - birthday.year
        if (today.month, today.day) < (birthday.month, birthday.day):
            age -= 1
        return age

    @staticmethod
    def calculate_age_months(birthday: date) -> int:
        """
        计算月龄

        Args:
            birthday: 出生日期

        Returns:
            int: 月龄
        """
        today = date.today()
        months = (today.year - birthday.year) * 12 + (today.month - birthday.month)
        if today.day < birthday.day:
            months -= 1
        return months

    @staticmethod
    def calculate_next_due_date(current_date: date, years: int = 1) -> date:
        """
        计算下次到期日期

        Args:
            current_date: 当前日期
            years: 年数

        Returns:
            date: 下次到期日期
        """
        try:
            # 尝试在同年同月增加年数
            next_date = current_date.replace(year=current_date.year + years)
            return next_date
        except ValueError:
            # 如果日期无效（如2月29日），使用最后一天
            if current_date.month == 2 and current_date.day == 29:
                # 检查目标年份是否是闰年
                target_year = current_date.year + years
                if (target_year % 4 == 0 and target_year % 100 != 0) or (target_year % 400 == 0):
                    return date(target_year, 2, 29)
                else:
                    return date(target_year, 2, 28)
            return current_date

    @staticmethod
    def get_date_string(d: date, format_str: str = "%Y年%m月%d日") -> str:
        """
        格式化日期字符串

        Args:
            d: 日期
            format_str: 格式字符串

        Returns:
            str: 格式化后的日期字符串
        """
        if d is None:
            return "未知"
        return d.strftime(format_str)

    @staticmethod
    def get_age_string(birthday: date) -> str:
        """
        获取年龄描述字符串

        Args:
            birthday: 出生日期

        Returns:
            str: 年龄描述
        """
        if birthday is None:
            return "未知"

        age = DateHelper.calculate_age(birthday)
        if age == 0:
            months = DateHelper.calculate_age_months(birthday)
            if months <= 3:
                return "幼年"
            return f"{months}个月"
        elif age == 1:
            return "1岁"
        else:
            return f"{age}岁"

    @staticmethod
    def parse_date(date_str: str) -> Optional[date]:
        """
        解析日期字符串

        Args:
            date_str: 日期字符串 (YYYY-MM-DD)

        Returns:
            date: 日期对象，解析失败返回None
        """
        if not date_str:
            return None
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            return None

    @staticmethod
    def is_today(d: date) -> bool:
        """判断日期是否是今天"""
        return d == date.today()

    @staticmethod
    def is_past(d: date) -> bool:
        """判断日期是否是过去"""
        return d < date.today()

    @staticmethod
    def is_future(d: date) -> bool:
        """判断日期是否是未来"""
        return d > date.today()

    @staticmethod
    def days_between(start: date, end: date) -> int:
        """计算两个日期之间的天数"""
        return (end - start).days
