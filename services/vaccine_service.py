"""
疫苗记录业务逻辑模块
"""
from typing import List, Optional
from datetime import date, timedelta

from database import DatabaseHelper, get_db_manager
from models.vaccine import Vaccine
from models.reminder import Reminder


class VaccineService:
    """疫苗记录服务类"""

    def __init__(self):
        """初始化疫苗服务"""
        db_manager = get_db_manager()
        self.db_helper = DatabaseHelper(db_manager)

    def add_vaccine(self, pet_id: int, vaccine_name: str, vaccine_date: date,
                    next_due: date = None, notes: str = None) -> Vaccine:
        """
        添加疫苗记录

        Args:
            pet_id: 宠物ID
            vaccine_name: 疫苗名称
            vaccine_date: 接种日期
            next_due: 下次到期日
            notes: 备注

        Returns:
            Vaccine: 新创建的疫苗记录
        """
        vaccine_id = self.db_helper.insert_vaccine(
            pet_id, vaccine_name, vaccine_date, next_due, notes
        )

        # 如果有下次到期日，自动创建提醒
        if next_due:
            self._create_reminder_from_vaccine(vaccine_id, pet_id, vaccine_name, next_due)

        return self.get_vaccine_by_id(vaccine_id)

    def get_vaccine_by_id(self, vaccine_id: int) -> Optional[Vaccine]:
        """
        根据ID获取疫苗记录

        Args:
            vaccine_id: 疫苗记录ID

        Returns:
            Optional[Vaccine]: 疫苗记录对象
        """
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vaccines WHERE id = ?', (vaccine_id,))
        row = cursor.fetchone()
        return Vaccine.from_dict(dict(row)) if row else None

    def get_vaccines_by_pet(self, pet_id: int) -> List[Vaccine]:
        """
        获取某宠物的所有疫苗记录

        Args:
            pet_id: 宠物ID

        Returns:
            List[Vaccine]: 疫苗记录列表
        """
        vaccines_data = self.db_helper.get_vaccines_by_pet(pet_id)
        return [Vaccine.from_dict(data) for data in vaccines_data]

    def get_upcoming_vaccines(self, days: int = 7) -> List[Vaccine]:
        """
        获取即将到期的疫苗记录

        Args:
            days: 天数范围

        Returns:
            List[Vaccine]: 即将到期的疫苗记录列表
        """
        vaccines_data = self.db_helper.get_upcoming_vaccines(days)
        return [Vaccine.from_dict(data) for data in vaccines_data]

    def delete_vaccine(self, vaccine_id: int) -> bool:
        """
        删除疫苗记录

        Args:
            vaccine_id: 疫苗记录ID

        Returns:
            bool: 是否删除成功
        """
        return self.db_helper.delete_vaccine(vaccine_id)

    def calculate_next_due(self, vaccine_date: date, years: int = 1) -> date:
        """
        计算下次到期日期

        Args:
            vaccine_date: 本次接种日期
            years: 年数

        Returns:
            date: 下次到期日期
        """
        try:
            next_date = vaccine_date.replace(year=vaccine_date.year + years)
            return next_date
        except ValueError:
            if vaccine_date.month == 2 and vaccine_date.day == 29:
                target_year = vaccine_date.year + years
                if (target_year % 4 == 0 and target_year % 100 != 0) or (target_year % 400 == 0):
                    return date(target_year, 2, 29)
                else:
                    return date(target_year, 2, 28)
            return vaccine_date

    def _create_reminder_from_vaccine(self, vaccine_id: int, pet_id: int,
                                       vaccine_name: str, next_due: date):
        """
        从疫苗记录创建提醒

        Args:
            vaccine_id: 疫苗记录ID
            pet_id: 宠物ID
            vaccine_name: 疫苗名称
            next_due: 下次到期日
        """
        title = f"疫苗接种：{vaccine_name}"
        self.db_helper.insert_reminder(pet_id, title, next_due, 'vaccine')
