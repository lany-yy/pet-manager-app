"""
提醒事项业务逻辑模块
"""
from typing import List, Optional
from datetime import date

from database import DatabaseHelper, get_db_manager
from models.reminder import Reminder


class ReminderService:
    """提醒事项服务类"""

    def __init__(self):
        """初始化提醒服务"""
        db_manager = get_db_manager()
        self.db_helper = DatabaseHelper(db_manager)

    def add_reminder(self, pet_id: int, title: str, due_date: date,
                     reminder_type: str = 'other') -> Reminder:
        """
        添加提醒事项

        Args:
            pet_id: 宠物ID
            title: 提醒标题
            due_date: 到期日期
            reminder_type: 提醒类型

        Returns:
            Reminder: 新创建的提醒事项
        """
        reminder_id = self.db_helper.insert_reminder(
            pet_id, title, due_date, reminder_type
        )
        return self.get_reminder_by_id(reminder_id)

    def get_reminder_by_id(self, reminder_id: int) -> Optional[Reminder]:
        """
        根据ID获取提醒事项

        Args:
            reminder_id: 提醒事项ID

        Returns:
            Optional[Reminder]: 提醒事项对象
        """
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reminders WHERE id = ?', (reminder_id,))
        row = cursor.fetchone()
        return Reminder.from_dict(dict(row)) if row else None

    def get_reminders_by_pet(self, pet_id: int, include_completed: bool = True) -> List[Reminder]:
        """
        获取某宠物的提醒事项

        Args:
            pet_id: 宠物ID
            include_completed: 是否包含已完成的

        Returns:
            List[Reminder]: 提醒事项列表
        """
        reminders_data = self.db_helper.get_reminders_by_pet(pet_id, include_completed)
        return [Reminder.from_dict(data) for data in reminders_data]

    def get_all_reminders(self, include_completed: bool = False) -> List[Reminder]:
        """
        获取所有提醒事项

        Args:
            include_completed: 是否包含已完成的

        Returns:
            List[Reminder]: 提醒事项列表
        """
        reminders_data = self.db_helper.get_all_reminders(include_completed)
        return [Reminder.from_dict(data) for data in reminders_data]

    def get_today_reminders(self) -> List[Reminder]:
        """
        获取今日到期的提醒

        Returns:
            List[Reminder]: 今日提醒列表
        """
        reminders_data = self.db_helper.get_today_reminders()
        return [Reminder.from_dict(data) for data in reminders_data]

    def get_overdue_reminders(self) -> List[Reminder]:
        """
       获取已过期的提醒

        Returns:
            List[Reminder]: 逾期提醒列表
        """
        reminders_data = self.db_helper.get_overdue_reminders()
        return [Reminder.from_dict(data) for data in reminders_data]

    def get_upcoming_reminders(self, days: int = 7) -> List[Reminder]:
        """
        获取即将到期的提醒

        Args:
            days: 天数范围

        Returns:
            List[Reminder]: 即将到期的提醒列表
        """
        all_reminders = self.get_all_reminders(include_completed=False)
        upcoming = []
        today = date.today()

        for reminder in all_reminders:
            if reminder.due_date:
                days_until = (reminder.due_date - today).days
                if 0 <= days_until <= days:
                    upcoming.append(reminder)

        return upcoming

    def mark_completed(self, reminder_id: int) -> bool:
        """
        标记提醒为已完成

        Args:
            reminder_id: 提醒事项ID

        Returns:
            bool: 是否标记成功
        """
        return self.db_helper.update_reminder_status(reminder_id, True)

    def mark_uncompleted(self, reminder_id: int) -> bool:
        """
        标记提醒为未完成

        Args:
            reminder_id: 提醒事项ID

        Returns:
            bool: 是否标记成功
        """
        return self.db_helper.update_reminder_status(reminder_id, False)

    def delete_reminder(self, reminder_id: int) -> bool:
        """
        删除提醒事项

        Args:
            reminder_id: 提醒事项ID

        Returns:
            bool: 是否删除成功
        """
        return self.db_helper.delete_reminder(reminder_id)

    def get_reminder_count(self) -> dict:
        """
        获取提醒数量统计

        Returns:
            dict: {'today': int, 'overdue': int, 'upcoming': int}
        """
        return {
            'today': len(self.get_today_reminders()),
            'overdue': len(self.get_overdue_reminders()),
            'upcoming': len(self.get_upcoming_reminders())
        }
