"""
确认对话框组件
"""
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty, ObjectProperty


class ConfirmDialog(ModalView):
    """确认对话框组件"""

    title = StringProperty("")
    message = StringProperty("")
    on_confirm_callback = ObjectProperty(None)

    def __init__(self, title="确认", message="", on_confirm=None, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.message = message
        self.on_confirm_callback = on_confirm
        self.auto_dismiss = False
        self.build_ui()

    def build_ui(self):
        """构建对话框UI"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # 标题
        title_label = Label(
            text=self.title,
            font_size='18sp',
            bold=True,
            size_hint_y=0.2
        )
        layout.add_widget(title_label)

        # 消息
        message_label = Label(
            text=self.message,
            font_size='14sp',
            size_hint_y=0.5,
            text_size=(self.width - 40, None),
            halign='center',
            valign='middle'
        )
        layout.add_widget(message_label)

        # 按钮
        btn_layout = BoxLayout(size_hint_y=0.3, spacing=20)

        btn_cancel = Button(
            text='取消',
            on_press=lambda x: self.dismiss()
        )
        btn_confirm = Button(
            text='确定',
            on_press=lambda x: self.confirm()
        )

        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_confirm)
        layout.add_widget(btn_layout)

        self.add_widget(layout)

    def confirm(self):
        """确认回调"""
        if self.on_confirm_callback:
            self.on_confirm_callback()
        self.dismiss()
