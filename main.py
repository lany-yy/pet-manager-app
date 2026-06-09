"""
猫狗宠物管理系统 - 主入口
基于Kivy框架的宠物管理应用
"""
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock
from datetime import date

# 初始化数据库
from database import get_db_manager

# 当前登录用户
current_user = None


class MainScreen(Screen):
    """主界面"""
    pet_count = NumericProperty(0)
    reminder_count = NumericProperty(0)

    def on_enter(self):
        """进入界面时刷新数据"""
        self.refresh_counts()

    def refresh_counts(self):
        """刷新统计数据"""
        from services import PetService, ReminderService
        pet_service = PetService()
        reminder_service = ReminderService()

        count = pet_service.get_pet_count()
        self.pet_count = count['total']

        reminder_data = reminder_service.get_reminder_count()
        self.reminder_count = reminder_data['today'] + reminder_data['overdue']


class PetListScreen(Screen):
    """宠物列表界面"""
    pets = ListProperty([])
    selected_filter = StringProperty('all')

    def on_enter(self):
        """进入界面时刷新数据"""
        self.load_pets()

    def on_leave(self):
        """离开界面时清空搜索"""
        self.ids.search_input.text = ""

    def load_pets(self):
        """加载宠物列表"""
        from services import PetService
        pet_service = PetService()
        self.pets = pet_service.get_all_pets()
        self.update_pet_cards()

    def update_pet_cards(self):
        """更新宠物卡片列表"""
        container = self.ids.pet_cards_container
        container.clear_widgets()

        for pet in self.pets:
            from widgets import PetCard
            card = PetCard(
                pet_id=pet.id,
                name=pet.name,
                pet_type=pet.type,
                breed=pet.breed or "",
                avatar_path=pet.avatar_path or "",
                gender=pet.gender
            )
            container.add_widget(card)

    def filter_pets(self, filter_type):
        """筛选宠物"""
        from services import PetService
        pet_service = PetService()
        self.selected_filter = filter_type
        if filter_type == 'all':
            self.pets = pet_service.get_all_pets()
        else:
            self.pets = pet_service.filter_pets_by_type(filter_type)
        self.update_pet_cards()

    def search_pets(self, keyword):
        """搜索宠物"""
        if not keyword:
            self.load_pets()
            return
        from services import PetService
        pet_service = PetService()
        self.pets = pet_service.search_pets(keyword)
        self.update_pet_cards()


class PetDetailScreen(Screen):
    """宠物详情界面"""
    pet_id = StringProperty("")
    pet = ObjectProperty(None)

    def on_enter(self):
        """进入界面时加载宠物详情"""
        self.load_pet()

    def load_pet(self):
        """加载宠物信息"""
        if self.pet_id:
            from services import PetService
            pet_service = PetService()
            self.pet = pet_service.get_pet_by_id(int(self.pet_id))

    def go_to_edit(self):
        """跳转到编辑页面"""
        if self.pet_id:
            sm.get_screen('add_pet').pet_id = self.pet_id
            sm.get_screen('add_pet').is_editing = True
            sm.current = 'add_pet'

    def go_to_vaccines(self):
        """跳转到疫苗记录"""
        if self.pet_id:
            sm.get_screen('vaccine').pet_id = self.pet_id
            sm.current = 'vaccine'

    def go_to_weights(self):
        """跳转到体重记录"""
        if self.pet_id:
            sm.get_screen('weight').pet_id = self.pet_id
            sm.current = 'weight'

    def delete_pet(self):
        """删除宠物"""
        if self.pet_id:
            self.show_confirm_dialog("确认删除", "确定要删除这只宠物吗？所有相关数据将被删除。", self.confirm_delete)

    def confirm_delete(self):
        """确认删除"""
        from services import PetService
        pet_service = PetService()
        if pet_service.delete_pet(int(self.pet_id)):
            sm.current = 'pet_list'

    def show_confirm_dialog(self, title, message, callback):
        """显示确认对话框"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(PopupLabel(text=message, font_size='16sp', halign='center', valign='middle'))

        buttons = BoxLayout(size_hint_y=0.3, spacing=20)
        btn_cancel = Button(text='取消', on_press=lambda x: popup.dismiss())
        btn_confirm = Button(text='确定', on_press=lambda x: (callback(), popup.dismiss()))
        buttons.add_widget(btn_cancel)
        buttons.add_widget(btn_confirm)
        content.add_widget(buttons)

        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4), auto_dismiss=False)
        popup.open()
        return popup


class AddPetScreen(Screen):
    """添加/编辑宠物界面"""
    pet_id = StringProperty("")
    is_editing = BooleanProperty(False)
    selected_avatar = StringProperty("")
    selected_type = StringProperty("dog")
    selected_gender = StringProperty("unknown")

    def on_enter(self):
        """进入界面时如果是编辑模式则加载数据"""
        if self.pet_id:
            self.is_editing = True
            self.load_pet_data()
        else:
            self.reset_form()

    def on_leave(self):
        """离开界面时重置表单"""
        self.reset_form()

    def reset_form(self):
        """重置表单"""
        self.pet_id = ""
        self.is_editing = False
        self.selected_avatar = ""
        self.ids.name_input.text = ""
        self.ids.breed_input.text = ""
        self.ids.type_spinner.text = "狗狗"
        self.ids.gender_spinner.text = "未知"
        self.ids.birthday_input.text = ""

    def load_pet_data(self):
        """加载宠物数据用于编辑"""
        if self.pet_id:
            from services import PetService
            pet_service = PetService()
            pet = pet_service.get_pet_by_id(int(self.pet_id))
            if pet:
                self.ids.name_input.text = pet.name
                self.ids.type_spinner.text = "猫咪" if pet.type == "cat" else "狗狗"
                self.ids.breed_input.text = pet.breed or ""
                self.ids.gender_spinner.text = {"male": "公", "female": "母", "unknown": "未知"}.get(pet.gender, "未知")
                self.ids.birthday_input.text = pet.birthday.isoformat() if pet.birthday else ""
                self.selected_avatar = pet.avatar_path or ""
                self.selected_type = pet.type
                self.selected_gender = pet.gender

    def go_back(self):
        """返回上一页"""
        if self.is_editing and self.pet_id:
            sm.get_screen('pet_detail').pet_id = self.pet_id
            sm.current = 'pet_detail'
        else:
            sm.current = 'pet_list'

    def save_pet(self):
        """保存宠物"""
        name = self.ids.name_input.text.strip()
        if not name:
            self.show_error("请输入宠物名字")
            return

        pet_type = "cat" if self.ids.type_spinner.text == "猫咪" else "dog"
        breed = self.ids.breed_input.text.strip()
        birthday_str = self.ids.birthday_input.text.strip()

        gender_map = {"公": "male", "母": "female", "未知": "unknown"}
        gender = gender_map.get(self.ids.gender_spinner.text, "unknown")

        # 解析生日
        birthday = None
        if birthday_str:
            try:
                birthday = date.fromisoformat(birthday_str)
            except ValueError:
                self.show_error("生日日期格式不正确，请使用YYYY-MM-DD格式")
                return

        from services import PetService
        pet_service = PetService()

        if self.is_editing and self.pet_id:
            # 更新
            success = pet_service.update_pet(
                int(self.pet_id),
                name=name,
                pet_type=pet_type,
                breed=breed,
                birthday=birthday,
                gender=gender,
                avatar_path=self.selected_avatar
            )
            if success:
                self.show_success("宠物信息已更新")
                sm.get_screen('pet_detail').pet_id = self.pet_id
                sm.current = 'pet_detail'
        else:
            # 添加
            pet = pet_service.add_pet(
                name=name,
                pet_type=pet_type,
                breed=breed,
                birthday=birthday,
                gender=gender,
                avatar_path=self.selected_avatar
            )
            if pet:
                self.show_success("宠物添加成功")
                sm.get_screen('pet_detail').pet_id = str(pet.id)
                sm.current = 'pet_detail'

    def select_avatar(self, filepath):
        """选择头像"""
        if filepath:
            self.selected_avatar = filepath

    def show_error(self, message):
        """显示错误提示"""
        popup = Popup(
            title='错误',
            content=PopupLabel(text=message, font_size='14sp'),
            size_hint=(0.7, 0.3)
        )
        popup.open()

    def show_success(self, message):
        """显示成功提示"""
        popup = Popup(
            title='成功',
            content=PopupLabel(text=message, font_size='14sp', text_color=(0, 0.5, 0, 1)),
            size_hint=(0.7, 0.3)
        )
        popup.open()


class ReminderScreen(Screen):
    """提醒事项界面"""
    reminders = ListProperty([])
    today_reminders = ListProperty([])
    overdue_reminders = ListProperty([])
    upcoming_reminders = ListProperty([])
    pets = ListProperty([])
    show_add_form = BooleanProperty(False)
    today_count = NumericProperty(0)

    @property
    def today_str(self):
        """获取今天日期字符串"""
        return date.today().isoformat()

    def on_enter(self):
        """进入界面时加载数据"""
        self.load_reminders()
        self.load_pets()
        self.show_add_form = False

    def load_pets(self):
        """加载宠物列表"""
        from services import PetService
        pet_service = PetService()
        self.pets = pet_service.get_all_pets()

    def load_reminders(self):
        """加载提醒事项"""
        from services import ReminderService
        reminder_service = ReminderService()
        self.reminders = reminder_service.get_all_reminders()

        # 分类
        self.today_reminders = reminder_service.get_today_reminders()
        self.overdue_reminders = reminder_service.get_overdue_reminders()
        self.upcoming_reminders = reminder_service.get_upcoming_reminders(days=7)
        self.today_count = len(self.today_reminders) + len(self.overdue_reminders)

    def mark_done(self, reminder_id):
        """标记完成"""
        from services import ReminderService
        reminder_service = ReminderService()
        reminder_service.mark_completed(reminder_id)
        self.load_reminders()

    def delete_reminder(self, reminder_id):
        """删除提醒"""
        from services import ReminderService
        reminder_service = ReminderService()
        reminder_service.delete_reminder(reminder_id)
        self.load_reminders()

    def show_add_form(self):
        """显示添加表单"""
        self.show_add_form = True

    def hide_add_form(self):
        """隐藏添加表单"""
        self.show_add_form = False

    def add_reminder(self):
        """添加新提醒"""
        title = self.ids.reminder_title.text.strip() if hasattr(self.ids, 'reminder_title') else ""
        reminder_type = self.ids.reminder_type.text if hasattr(self.ids, 'reminder_type') else "other"
        pet_name = self.ids.reminder_pet.text if hasattr(self.ids, 'reminder_pet') else ""
        due_date_str = self.ids.reminder_due_date.text if hasattr(self.ids, 'reminder_due_date') else ""

        if not title:
            self.show_error("请输入提醒标题")
            return
        if not due_date_str:
            self.show_error("请输入到期日期")
            return

        try:
            due_date = date.fromisoformat(due_date_str)
        except ValueError:
            self.show_error("日期格式不正确")
            return

        # 查找宠物ID
        pet_id = 0
        if pet_name != '选择宠物':
            for pet in self.pets:
                if pet.name == pet_name:
                    pet_id = pet.id
                    break

        # 转换类型
        type_map = {"疫苗接种": "vaccine", "驱虫": "deworm", "洗澡": "bath", "其他": "other"}
        reminder_type = type_map.get(reminder_type, "other")

        from services import ReminderService
        reminder_service = ReminderService()
        reminder_service.add_reminder(pet_id=pet_id, title=title, due_date=due_date, reminder_type=reminder_type)

        self.hide_add_form()
        self.load_reminders()
        self.show_success("提醒添加成功")

    def show_error(self, message):
        """显示错误提示"""
        popup = Popup(
            title='错误',
            content=PopupLabel(text=message, font_size='14sp'),
            size_hint=(0.7, 0.3)
        )
        popup.open()

    def show_success(self, message):
        """显示成功提示"""
        popup = Popup(
            title='成功',
            content=PopupLabel(text=message, font_size='14sp', text_color=(0, 0.5, 0, 1)),
            size_hint=(0.7, 0.3)
        )
        popup.open()


class LoginScreen(Screen):
    """登录界面"""
    
    def login(self):
        """登录验证"""
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()
        
        if not username or not password:
            self.ids.error_label.text = '请输入用户名和密码'
            return
        
        from services import UserService
        user_service = UserService()
        success, message, user = user_service.login_user(username, password)
        
        if success:
            global current_user
            current_user = user
            sm.current = 'main'
            self.ids.error_label.text = ''
            self.ids.username_input.text = ''
            self.ids.password_input.text = ''
        else:
            self.ids.error_label.text = message
    
    def go_to_register(self):
        """跳转到注册界面"""
        self.ids.error_label.text = ''
        self.ids.username_input.text = ''
        self.ids.password_input.text = ''
        sm.current = 'register'


class RegisterScreen(Screen):
    """注册界面"""
    
    def register(self):
        """用户注册"""
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()
        confirm_password = self.ids.confirm_password_input.text.strip()
        email = self.ids.email_input.text.strip()
        
        if not username:
            self.ids.error_label.text = '请输入用户名'
            return
        if not password:
            self.ids.error_label.text = '请输入密码'
            return
        if password != confirm_password:
            self.ids.error_label.text = '两次输入的密码不一致'
            return
        
        from services import UserService
        user_service = UserService()
        success, message = user_service.register_user(username, password, email)
        
        if success:
            self.show_success(message)
            self.clear_form()
            sm.current = 'login'
        else:
            self.ids.error_label.text = message
    
    def go_to_login(self):
        """跳转到登录界面"""
        self.clear_form()
        sm.current = 'login'
    
    def clear_form(self):
        """清空表单"""
        self.ids.username_input.text = ''
        self.ids.password_input.text = ''
        self.ids.confirm_password_input.text = ''
        self.ids.email_input.text = ''
        self.ids.error_label.text = ''
    
    def show_success(self, message):
        """显示成功提示"""
        popup = Popup(
            title='成功',
            content=PopupLabel(text=message, font_size='14sp', color=(0, 0.5, 0, 1)),
            size_hint=(0.7, 0.3)
        )
        popup.open()


# 设置界面从screens模块导入
from screens.settings_screen import SettingsScreen


# 导入需要的组件
from kivy.uix.label import Label as PopupLabel
from kivy.uix.button import Button


# 导入健康记录界面
from screens.health_screens import VaccineScreen, DewormScreen, WeightScreen
from screens.statistics_screen import StatisticsScreen
from screens.daily_screen import DailyManagementScreen


# 全局变量
sm = None


class PetManagerApp(App):
    """宠物管理应用"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化数据库
        self.db_manager = get_db_manager()

    def build(self):
        """构建应用"""
        global sm
        
        # 加载KV文件
        Builder.load_file('kv/login.kv')
        Builder.load_file('kv/register.kv')
        Builder.load_file('kv/main.kv')
        Builder.load_file('kv/pet_list.kv')
        Builder.load_file('kv/pet_detail.kv')
        Builder.load_file('kv/custom_widgets.kv')
        Builder.load_file('kv/add_pet.kv')
        Builder.load_file('kv/vaccine.kv')
        Builder.load_file('kv/deworm.kv')
        Builder.load_file('kv/weight.kv')
        Builder.load_file('kv/reminder.kv')
        Builder.load_file('kv/statistics.kv')
        Builder.load_file('kv/daily.kv')
        Builder.load_file('kv/settings.kv')

        # 创建ScreenManager
        sm = ScreenManager(transition=NoTransition())

        # 注册所有屏幕
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(PetListScreen(name='pet_list'))
        sm.add_widget(PetDetailScreen(name='pet_detail'))
        sm.add_widget(AddPetScreen(name='add_pet'))
        sm.add_widget(VaccineScreen(name='vaccine'))
        sm.add_widget(DewormScreen(name='deworm'))
        sm.add_widget(WeightScreen(name='weight'))
        sm.add_widget(DailyManagementScreen(name='daily'))
        sm.add_widget(ReminderScreen(name='reminder'))
        sm.add_widget(StatisticsScreen(name='statistics'))
        sm.add_widget(SettingsScreen(name='settings'))
        
        # 默认显示登录界面
        sm.current = 'login'
        
        return sm

    def on_start(self):
        """应用启动时"""
        print("[PetManagerApp] 应用启动成功")

    def on_pause(self):
        """应用暂停时"""
        return True

    def on_resume(self):
        """应用恢复时"""
        pass

    def get_manager(self):
        """获取ScreenManager"""
        return sm


if __name__ == '__main__':
    from kivy.config import Config
    Config.set('graphics', 'width', '800')
    Config.set('graphics', 'height', '600')
    Config.set('graphics', 'resizable', 'True')
    Config.set('graphics', 'borderless', '0')
    
    from kivy.core.text import LabelBase
    LabelBase.register(name='SimHei', fn_regular='C:\\Windows\\Fonts\\simhei.ttf')
    LabelBase.register(name='SimSun', fn_regular='C:\\Windows\\Fonts\\simsun.ttc')
    
    PetManagerApp().run()
