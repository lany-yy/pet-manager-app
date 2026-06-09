"""
宠物卡片组件
用于在列表中显示宠物信息
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.lang import Builder

Builder.load_string("""
<PetCard>:
    size_hint_y: None
    height: 160
    orientation: 'vertical'
    padding: 10
    spacing: 5

    canvas:
        Color:
            rgba: 0.95, 0.95, 0.95, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12, 12, 12, 12]

    AsyncImage:
        source: root.avatar_path if root.avatar_path and root.avatar_path.exists() else (root.cat_placeholder if root.pet_type == 'cat' else root.dog_placeholder)
        size_hint_y: 0.65
        allow_stretch: True
        keep_ratio: True
        mipmap: True

    Label:
        text: root.name
        font_size: '16sp'
        bold: True
        halign: 'center'
        valign: 'middle'
        text_size: self.size

    Label:
        text: root.breed or ''
        font_size: '12sp'
        color: 0.5, 0.5, 0.5, 1
        halign: 'center'
        valign: 'top'
        text_size: self.size
""")


class PetCard(BoxLayout):
    """宠物卡片组件"""

    pet_id = NumericProperty(0)
    name = StringProperty("")
    pet_type = StringProperty("dog")
    breed = StringProperty("")
    avatar_path = StringProperty("")
    gender = StringProperty("unknown")

    # 占位图路径
    cat_placeholder = StringProperty("assets/images/cat_placeholder.png")
    dog_placeholder = StringProperty("assets/images/dog_placeholder.png")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_touch_down=self.on_card_tap)

    def on_card_tap(self, instance, touch):
        """处理卡片点击"""
        if self.collide_point(*touch.pos):
            self.navigate_to_detail()
            return True
        return False

    def navigate_to_detail(self):
        """跳转到详情页"""
        # 延迟导入避免循环引用
        import main
        detail_screen = main.sm.get_screen('pet_detail')
        detail_screen.pet_id = str(self.pet_id)
        main.sm.current = 'pet_detail'
