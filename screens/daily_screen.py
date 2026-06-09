"""
日常管理界面
"""
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, NumericProperty, BooleanProperty
from kivy.uix.popup import Popup
from datetime import date, time

from services import FeedingService, PetService


class DailyManagementScreen(Screen):
    """日常管理界面"""
    pet_id = StringProperty("")
    pet_name = StringProperty("")
    feedings = ListProperty([])
    today_total_amount = NumericProperty(0)
    
    show_add_feeding = BooleanProperty(False)
    food_type_input = StringProperty("干粮")
    amount_input = StringProperty("")
    time_input = StringProperty("")

    def on_enter(self):
        """进入界面时加载数据"""
        if self.pet_id:
            self.load_pet_info()
            self.load_feedings()
        self.show_add_feeding = False

    def load_pet_info(self):
        """加载宠物信息"""
        if self.pet_id:
            pet_service = PetService()
            pet = pet_service.get_pet_by_id(int(self.pet_id))
            if pet:
                self.pet_name = pet.name

    def load_feedings(self):
        """加载喂食记录"""
        if self.pet_id:
            feeding_service = FeedingService()
            self.feedings = feeding_service.get_today_feedings(int(self.pet_id))
            self.today_total_amount = feeding_service.get_total_amount_today(int(self.pet_id))

    def go_back(self):
        """返回"""
        self.manager.get_screen('pet_detail').pet_id = self.pet_id
        self.manager.current = 'pet_detail'

    def toggle_add_feeding(self):
        """显示/隐藏添加表单"""
        self.show_add_feeding = not self.show_add_feeding
        if not self.show_add_feeding:
            self.reset_feeding_form()

    def reset_feeding_form(self):
        """重置表单"""
        self.food_type_input = "干粮"
        self.amount_input = ""
        self.time_input = ""

    def add_feeding(self):
        """添加喂食记录"""
        if not self.pet_id:
            return

        if not self.amount_input:
            self.show_error("请输入喂食量")
            return

        try:
            amount = float(self.amount_input)
            if amount <= 0:
                self.show_error("请输入有效的喂食量")
                return
        except ValueError:
            self.show_error("请输入有效的数字")
            return

        # 获取当前时间
        now = time.now()
        feeding_time = time(now.hour, now.minute)

        feeding_service = FeedingService()
        feeding_service.add_feeding(
            pet_id=int(self.pet_id),
            record_date=date.today(),
            food_type=self.food_type_input,
            amount=amount,
            feeding_time=feeding_time
        )

        self.load_feedings()
        self.toggle_add_feeding()
        self.show_success("喂食记录添加成功")

    def delete_feeding(self, feeding_id):
        """删除喂食记录"""
        feeding_service = FeedingService()
        feeding_service.delete_feeding(feeding_id)
        self.load_feedings()
        self.show_success("喂食记录已删除")

    def record_walk(self):
        """记录遛狗"""
        self.show_success("遛狗记录已添加")

    def record_litter(self):
        """记录猫砂更换"""
        self.show_success("猫砂更换记录已添加")

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


from kivy.uix.label import Label