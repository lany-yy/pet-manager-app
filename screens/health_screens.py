from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from datetime import date


class VaccineScreen(Screen):
    """疫苗记录界面"""
    pet_id = StringProperty("")
    pet_name = StringProperty("")
    vaccines = ListProperty([])
    
    vaccine_name_input = StringProperty("")
    vaccine_date_input = StringProperty("")
    next_due_input = StringProperty("")
    notes_input = StringProperty("")
    show_add_form = BooleanProperty(False)

    def on_enter(self):
        """进入界面时加载数据"""
        if self.pet_id:
            self.load_pet_info()
            self.load_vaccines()
        self.show_add_form = False
        self.reset_form()

    def load_pet_info(self):
        """加载宠物信息"""
        if self.pet_id:
            from services import PetService
            pet_service = PetService()
            pet = pet_service.get_pet_by_id(int(self.pet_id))
            if pet:
                self.pet_name = pet.name

    def load_vaccines(self):
        """加载疫苗记录"""
        if self.pet_id:
            from services import VaccineService
            vaccine_service = VaccineService()
            self.vaccines = vaccine_service.get_vaccines_by_pet(int(self.pet_id))

    def go_back(self):
        """返回"""
        self.manager.get_screen('pet_detail').pet_id = self.pet_id
        self.manager.current = 'pet_detail'

    def toggle_add_form(self):
        """显示/隐藏添加表单"""
        self.show_add_form = not self.show_add_form
        if not self.show_add_form:
            self.reset_form()

    def reset_form(self):
        """重置表单"""
        self.vaccine_name_input = ""
        self.vaccine_date_input = date.today().isoformat()
        self.next_due_input = ""
        self.notes_input = ""

    def add_vaccine(self):
        """添加疫苗记录"""
        if not self.pet_id or not self.vaccine_name_input:
            self.show_error("请填写疫苗名称")
            return
        
        try:
            vaccine_date = date.fromisoformat(self.vaccine_date_input)
        except ValueError:
            self.show_error("日期格式不正确")
            return

        next_due = None
        if self.next_due_input:
            try:
                next_due = date.fromisoformat(self.next_due_input)
            except ValueError:
                self.show_error("下次到期日期格式不正确")
                return

        from services import VaccineService
        vaccine_service = VaccineService()
        vaccine_service.add_vaccine(
            pet_id=int(self.pet_id),
            vaccine_name=self.vaccine_name_input,
            vaccine_date=vaccine_date,
            next_due=next_due,
            notes=self.notes_input
        )

        self.load_vaccines()
        self.toggle_add_form()
        self.show_success("疫苗记录添加成功")

    def delete_vaccine(self, vaccine_id):
        """删除疫苗记录"""
        from services import VaccineService
        vaccine_service = VaccineService()
        vaccine_service.delete_vaccine(vaccine_id)
        self.load_vaccines()
        self.show_success("疫苗记录已删除")

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


class DewormScreen(Screen):
    """驱虫记录界面"""
    pet_id = StringProperty("")
    pet_name = StringProperty("")
    deworm_records = ListProperty([])
    
    deworm_type_input = StringProperty("体内")
    deworm_date_input = StringProperty("")
    next_due_input = StringProperty("")
    notes_input = StringProperty("")
    show_add_form = BooleanProperty(False)

    def on_enter(self):
        """进入界面时加载数据"""
        if self.pet_id:
            self.load_pet_info()
            self.load_deworm_records()
        self.show_add_form = False
        self.reset_form()

    def load_pet_info(self):
        """加载宠物信息"""
        if self.pet_id:
            from services import PetService
            pet_service = PetService()
            pet = pet_service.get_pet_by_id(int(self.pet_id))
            if pet:
                self.pet_name = pet.name

    def load_deworm_records(self):
        """加载驱虫记录"""
        if self.pet_id:
            from services import DewormService
            deworm_service = DewormService()
            self.deworm_records = deworm_service.get_deworm_records_by_pet(int(self.pet_id))

    def go_back(self):
        """返回"""
        self.manager.get_screen('pet_detail').pet_id = self.pet_id
        self.manager.current = 'pet_detail'

    def toggle_add_form(self):
        """显示/隐藏添加表单"""
        self.show_add_form = not self.show_add_form
        if not self.show_add_form:
            self.reset_form()

    def reset_form(self):
        """重置表单"""
        self.deworm_type_input = "体内"
        self.deworm_date_input = date.today().isoformat()
        self.next_due_input = ""
        self.notes_input = ""

    def add_deworm(self):
        """添加驱虫记录"""
        if not self.pet_id:
            return

        try:
            deworm_date = date.fromisoformat(self.deworm_date_input)
        except ValueError:
            self.show_error("日期格式不正确")
            return

        next_due = None
        if self.next_due_input:
            try:
                next_due = date.fromisoformat(self.next_due_input)
            except ValueError:
                self.show_error("下次日期格式不正确")
                return

        from services import DewormService
        deworm_service = DewormService()
        deworm_service.add_deworm_record(
            pet_id=int(self.pet_id),
            deworm_type=self.deworm_type_input,
            deworm_date=deworm_date,
            next_due=next_due,
            notes=self.notes_input
        )

        self.load_deworm_records()
        self.toggle_add_form()
        self.show_success("驱虫记录添加成功")

    def delete_deworm(self, record_id):
        """删除驱虫记录"""
        from services import DewormService
        deworm_service = DewormService()
        deworm_service.delete_deworm_record(record_id)
        self.load_deworm_records()
        self.show_success("驱虫记录已删除")

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


class WeightScreen(Screen):
    """体重记录界面"""
    pet_id = StringProperty("")
    pet_name = StringProperty("")
    weights = ListProperty([])
    latest_weight = NumericProperty(0)
    
    weight_input = StringProperty("")

    def on_enter(self):
        """进入界面时加载数据"""
        if self.pet_id:
            self.load_pet_info()
            self.load_weights()
        self.weight_input = ""

    def load_pet_info(self):
        """加载宠物信息"""
        if self.pet_id:
            from services import PetService
            pet_service = PetService()
            pet = pet_service.get_pet_by_id(int(self.pet_id))
            if pet:
                self.pet_name = pet.name

    def load_weights(self):
        """加载体重记录"""
        if self.pet_id:
            from services import WeightService
            weight_service = WeightService()
            self.weights = weight_service.get_weights_by_pet(int(self.pet_id))
            self.latest_weight = weight_service.get_latest_weight(int(self.pet_id)) or 0

    def add_weight(self):
        """添加体重记录"""
        if not self.pet_id or not self.weight_input:
            return
        
        try:
            weight = float(self.weight_input)
            if weight <= 0 or weight > 200:
                self.show_error("请输入有效的体重值")
                return
        except ValueError:
            self.show_error("请输入有效的数字")
            return

        from services import WeightService
        weight_service = WeightService()
        weight_service.add_weight(int(self.pet_id), weight)

        self.load_weights()
        self.weight_input = ""
        self.show_success("体重记录添加成功")

    def delete_weight(self, weight_id):
        """删除体重记录"""
        from services import WeightService
        weight_service = WeightService()
        weight_service.delete_weight(weight_id)
        self.load_weights()
        self.show_success("体重记录已删除")

    def go_back(self):
        """返回"""
        self.manager.get_screen('pet_detail').pet_id = self.pet_id
        self.manager.current = 'pet_detail'

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

    def get_weight_trend_data(self):
        """获取体重趋势数据"""
        if self.pet_id:
            from services import WeightService
            weight_service = WeightService()
            return weight_service.get_weight_trend(int(self.pet_id))
        return []