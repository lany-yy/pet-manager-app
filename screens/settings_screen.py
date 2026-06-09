"""
设置界面
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import os
import json


class SettingsScreen(Screen):
    """设置界面"""

    def go_back(self):
        """返回"""
        self.manager.current = 'main'

    def backup_data(self):
        """备份数据"""
        backup_path = self.create_backup()
        if backup_path:
            self.show_success(f"数据已备份到:\n{backup_path}")
        else:
            self.show_error("备份失败")

    def restore_data(self):
        """恢复数据"""
        result = self.restore_backup()
        if result:
            self.show_success("数据恢复成功")
        else:
            self.show_error("恢复失败")

    def clear_data(self):
        """清除所有数据"""
        self.show_confirm_dialog("确认清除", "确定要清除所有数据吗？此操作无法撤销！", self.confirm_clear)

    def confirm_clear(self):
        """确认清除"""
        from database import get_db_manager
        db_manager = get_db_manager()
        db_manager.reset_database()
        self.show_success("数据已清除")

    def create_backup(self) -> str:
        """创建数据备份"""
        from database import get_db_manager
        db_manager = get_db_manager()
        
        # 获取数据库路径
        db_path = db_manager.db_path
        if not os.path.exists(db_path):
            return ""

        # 创建备份文件名
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"pet_manager_backup_{timestamp}.db"
        
        # 备份到桌面
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        backup_path = os.path.join(desktop_path, backup_name)

        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            return backup_path
        except Exception:
            return ""

    def restore_backup(self) -> bool:
        """从备份恢复数据"""
        from database import get_db_manager
        db_manager = get_db_manager()

        # 在桌面查找最新的备份文件
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        backup_files = [f for f in os.listdir(desktop_path) if f.startswith('pet_manager_backup_') and f.endswith('.db')]
        
        if not backup_files:
            self.show_error("未找到备份文件")
            return False

        # 按修改时间排序，取最新的
        backup_files.sort(key=lambda f: os.path.getmtime(os.path.join(desktop_path, f)), reverse=True)
        latest_backup = os.path.join(desktop_path, backup_files[0])

        db_path = db_manager.db_path
        
        try:
            import shutil
            shutil.copy2(latest_backup, db_path)
            # 重新初始化连接
            db_manager.close()
            db_manager.conn = None
            db_manager.init_tables()
            return True
        except Exception as e:
            print(f"Restore error: {e}")
            return False

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

    def show_confirm_dialog(self, title, message, callback):
        """显示确认对话框"""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button

        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(text=message, font_size='14sp'))

        buttons = BoxLayout(size_hint_y=0.3, spacing=20)
        btn_cancel = Button(text='取消', on_press=lambda x: popup.dismiss())
        btn_confirm = Button(text='确定', on_press=lambda x: (callback(), popup.dismiss()))
        buttons.add_widget(btn_cancel)
        buttons.add_widget(btn_confirm)
        content.add_widget(buttons)

        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4), auto_dismiss=False)
        popup.open()
