"""
图表组件模块
提供体重曲线等图表显示功能
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Line, Rectangle
from kivy.properties import ListProperty, NumericProperty
from datetime import datetime


class WeightChart(BoxLayout):
    """体重趋势图表组件"""

    data_points = ListProperty([])
    max_weight = NumericProperty(0)
    min_weight = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(data_points=self.update_chart)
        self.bind(size=self.update_chart)

    def update_chart(self, *args):
        """更新图表"""
        self.canvas.after.clear()
        
        if not self.data_points:
            return

        # 提取数据并按日期排序
        sorted_data = sorted(self.data_points, key=lambda x: x['date'])
        
        if len(sorted_data) < 2:
            return

        # 计算体重范围
        weights = [p['weight'] for p in sorted_data]
        self.min_weight = min(weights) * 0.95
        self.max_weight = max(weights) * 1.05
        
        if self.max_weight == self.min_weight:
            self.max_weight = self.min_weight + 1
            self.min_weight = max(0, self.min_weight - 1)

        weight_range = self.max_weight - self.min_weight
        
        # 计算坐标
        padding = 40
        chart_width = self.width - padding * 2
        chart_height = self.height - padding * 2
        
        points = []
        step_x = chart_width / (len(sorted_data) - 1)
        
        for i, point in enumerate(sorted_data):
            x = padding + i * step_x
            y = padding + chart_height - ((point['weight'] - self.min_weight) / weight_range) * chart_height
            points.append((x, y))

        # 绘制网格
        with self.canvas.after:
            # 水平网格线
            Color(0.9, 0.9, 0.9, 1)
            for i in range(5):
                y = padding + (chart_height / 4) * i
                Line(points=[(padding, y), (self.width - padding, y)], width=1)

            # 垂直网格线
            for i in range(len(sorted_data)):
                x = padding + step_x * i
                Line(points=[(x, padding), (x, self.height - padding)], width=1)

            # 绘制曲线
            Color(0.2, 0.6, 0.8, 1)
            Line(points=points, width=2, smooth=True)

            # 绘制数据点
            Color(0.8, 0.3, 0.3, 1)
            for x, y in points:
                Line(circle=(x, y, 4), width=2)

            # Y轴标签
            Color(0.5, 0.5, 0.5, 1)
            for i in range(5):
                y = padding + (chart_height / 4) * (4 - i)
                weight_val = self.min_weight + (weight_range / 4) * i
                label_text = f"{weight_val:.1f}kg"

    def set_data(self, data):
        """设置图表数据"""
        self.data_points = data


class StatCard(BoxLayout):
    """统计卡片组件"""

    title = ListProperty([])
    value = ListProperty([])
    color = ListProperty([0.2, 0.6, 0.8, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

    def update_display(self):
        """更新显示"""
        pass
