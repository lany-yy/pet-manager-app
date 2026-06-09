"""
统计报表界面
"""
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, DictProperty, ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
import os


class StatisticsScreen(Screen):
    """统计报表界面"""
    pet_id = StringProperty("")
    pet_name = StringProperty("")
    stats = DictProperty({})
    pets = ListProperty([])
    selected_pet_id = NumericProperty(0)

    def on_enter(self):
        """进入界面时加载数据"""
        self.load_pets()
        self.load_stats()

    def load_pets(self):
        """加载宠物列表"""
        from services import PetService
        pet_service = PetService()
        self.pets = pet_service.get_all_pets()

    def load_stats(self):
        """加载统计数据"""
        from services import StatsService
        stats_service = StatsService()
        
        if self.selected_pet_id:
            self.stats = stats_service.get_pet_stats(self.selected_pet_id)
            # 获取宠物名字
            from services import PetService
            pet_service = PetService()
            pet = pet_service.get_pet_by_id(self.selected_pet_id)
            self.pet_name = pet.name if pet else ""
        else:
            self.stats = stats_service.get_overall_stats()
            self.pet_name = "全部宠物"

    def select_pet(self, pet_id):
        """选择宠物"""
        self.selected_pet_id = pet_id
        self.load_stats()

    def on_pet_selected(self, pet_name):
        """宠物选择器回调"""
        if pet_name == '全部宠物':
            self.selected_pet_id = 0
        else:
            for p in self.pets:
                if p.name == pet_name:
                    self.selected_pet_id = p.id
                    break
        self.load_stats()

    def get_active_reminders(self):
        """获取待处理提醒数量"""
        val = self.stats.get('upcoming_reminders', 0)
        if val == 0:
            val = self.stats.get('active_reminders', 0)
        return val

    def go_back(self):
        """返回"""
        self.manager.current = 'main'

    def export_report(self):
        """导出健康报告"""
        if not self.selected_pet_id:
            self.show_error("请先选择一只宠物")
            return

        from services import StatsService
        stats_service = StatsService()

        # 生成文件名
        filename = f"{self.pet_name}_健康报告.txt"
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        file_path = os.path.join(desktop_path, filename)

        if stats_service.export_report_to_file(self.selected_pet_id, file_path):
            self.show_success(f"报告已导出到:\n{file_path}")
        else:
            self.show_error("导出失败")

    def show_error(self, message):
        """显示错误提示"""
        popup = Popup(
            title='错误',
            content=Label(text=message, font_size='14sp'),
            size_hint=(0.7, 0.3)
        )
        popup.open()

    def show_success(self, message):
        """显示成功提示"""
        popup = Popup(
            title='成功',
            content=Label(text=message, font_size='14sp', color=(0, 0.5, 0, 1)),
            size_hint=(0.7, 0.3)
        )
        popup.open()


class StatsCard(BoxLayout):
    """统计卡片组件"""
    title = StringProperty("")
    value = StringProperty("")
    color = ListProperty([0.2, 0.6, 0.8, 1])
