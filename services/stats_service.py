"""
统计服务模块
提供数据统计和报表生成功能
"""
from typing import List, Dict, Any
from datetime import date, timedelta

from database import DatabaseHelper, get_db_manager


class StatsService:
    """统计服务类"""

    def __init__(self):
        """初始化统计服务"""
        db_manager = get_db_manager()
        self.db_helper = DatabaseHelper(db_manager)

    def get_pet_stats(self, pet_id: int) -> Dict[str, Any]:
        """
        获取某宠物的统计数据

        Args:
            pet_id: 宠物ID

        Returns:
            Dict[str, Any]: 统计数据
        """
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()

        stats = {
            'pet_id': pet_id,
            'total_vaccines': 0,
            'completed_vaccines': 0,
            'vaccine_rate': 0.0,
            'total_weight_records': 0,
            'avg_weight': 0.0,
            'min_weight': 0.0,
            'max_weight': 0.0,
            'total_feedings': 0,
            'total_deworm': 0,
            'upcoming_reminders': 0
        }

        # 疫苗统计
        cursor.execute('SELECT COUNT(*) as total FROM vaccines WHERE pet_id = ?', (pet_id,))
        stats['total_vaccines'] = cursor.fetchone()['total']

        if stats['total_vaccines'] > 0:
            stats['completed_vaccines'] = stats['total_vaccines']
            stats['vaccine_rate'] = 100.0

        # 体重统计
        cursor.execute('SELECT COUNT(*), AVG(weight), MIN(weight), MAX(weight) FROM weight_records WHERE pet_id = ?', (pet_id,))
        row = cursor.fetchone()
        stats['total_weight_records'] = row[0]
        stats['avg_weight'] = round(row[1], 1) if row[1] else 0.0
        stats['min_weight'] = round(row[2], 1) if row[2] else 0.0
        stats['max_weight'] = round(row[3], 1) if row[3] else 0.0

        # 喂食统计
        cursor.execute('SELECT COUNT(*) FROM feeding_records WHERE pet_id = ?', (pet_id,))
        stats['total_feedings'] = cursor.fetchone()[0]

        # 驱虫统计
        cursor.execute('SELECT COUNT(*) FROM deworm_records WHERE pet_id = ?', (pet_id,))
        stats['total_deworm'] = cursor.fetchone()[0]

        # 即将到来的提醒
        today = date.today()
        future_date = today + timedelta(days=7)
        cursor.execute(
            'SELECT COUNT(*) FROM reminders WHERE pet_id = ? AND due_date BETWEEN ? AND ? AND is_completed = 0',
            (pet_id, today, future_date)
        )
        stats['upcoming_reminders'] = cursor.fetchone()[0]

        return stats

    def get_overall_stats(self) -> Dict[str, Any]:
        """
        获取整体统计数据

        Returns:
            Dict[str, Any]: 整体统计数据
        """
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()

        stats = {
            'total_pets': 0,
            'total_cats': 0,
            'total_dogs': 0,
            'total_vaccines': 0,
            'total_weight_records': 0,
            'total_feedings': 0,
            'total_deworm': 0,
            'active_reminders': 0
        }

        cursor.execute('SELECT COUNT(*) FROM pets')
        stats['total_pets'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM pets WHERE type = 'cat'")
        stats['total_cats'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM pets WHERE type = 'dog'")
        stats['total_dogs'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM vaccines')
        stats['total_vaccines'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM weight_records')
        stats['total_weight_records'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM feeding_records')
        stats['total_feedings'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM deworm_records')
        stats['total_deworm'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM reminders WHERE is_completed = 0')
        stats['active_reminders'] = cursor.fetchone()[0]

        return stats

    def get_weight_trend(self, pet_id: int, months: int = 6) -> List[Dict[str, Any]]:
        """
        获取体重趋势数据

        Args:
            pet_id: 宠物ID
            months: 月份范围

        Returns:
            List[Dict[str, Any]]: 体重趋势数据
        """
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()

        start_date = date.today() - timedelta(days=months * 30)
        cursor.execute(
            'SELECT date, weight FROM weight_records WHERE pet_id = ? AND date >= ? ORDER BY date ASC',
            (pet_id, start_date)
        )
        rows = cursor.fetchall()

        return [{'date': row['date'], 'weight': row['weight']} for row in rows]

    def get_feeding_frequency(self, pet_id: int) -> Dict[str, int]:
        """
        获取喂食频率分布

        Args:
            pet_id: 宠物ID

        Returns:
            Dict[str, int]: 喂食频率统计
        """
        conn = self.db_helper._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT strftime("%w", date) as day, COUNT(*) as count FROM feeding_records WHERE pet_id = ? GROUP BY strftime("%w", date)', (pet_id,))
        rows = cursor.fetchall()

        # 星期映射: 0=周日, 1=周一, ..., 6=周六
        day_map = {
            '0': '周日',
            '1': '周一',
            '2': '周二',
            '3': '周三',
            '4': '周四',
            '5': '周五',
            '6': '周六'
        }

        result = {day_map[str(i)]: 0 for i in range(7)}
        for row in rows:
            day_name = day_map.get(row['day'])
            if day_name:
                result[day_name] = row['count']

        return result

    def generate_health_report(self, pet_id: int) -> str:
        """
        生成健康报告

        Args:
            pet_id: 宠物ID

        Returns:
            str: 健康报告文本
        """
        from services import PetService
        pet_service = PetService()
        pet = pet_service.get_pet_by_id(pet_id)

        if not pet:
            return "宠物不存在"

        stats = self.get_pet_stats(pet_id)

        report = f"""宠物健康报告
==========

宠物信息
--------
姓名: {pet.name}
类型: {pet.type_display}
品种: {pet.breed or '未知'}
性别: {pet.gender_display}
年龄: {pet.age_display}

健康统计
--------
疫苗接种: {stats['completed_vaccines']}/{stats['total_vaccines']} ({stats['vaccine_rate']}%)
体重记录: {stats['total_weight_records']} 次
平均体重: {stats['avg_weight']}kg
体重范围: {stats['min_weight']}-{stats['max_weight']}kg
驱虫次数: {stats['total_deworm']} 次
喂食记录: {stats['total_feedings']} 次

即将到来的提醒
--------------
{stats['upcoming_reminders']} 项

生成时间: {date.today().strftime('%Y年%m月%d日')}
"""

        return report

    def export_report_to_file(self, pet_id: int, file_path: str) -> bool:
        """
        导出健康报告到文件

        Args:
            pet_id: 宠物ID
            file_path: 文件路径

        Returns:
            bool: 是否导出成功
        """
        report = self.generate_health_report(pet_id)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report)
            return True
        except Exception:
            return False
