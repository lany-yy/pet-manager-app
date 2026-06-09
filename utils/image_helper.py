"""
图片处理模块
提供图片相关的辅助函数
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Tuple


class ImageHelper:
    """图片处理辅助工具类"""

    # 支持的图片格式
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp']

    # 默认头像占位符
    CAT_PLACEHOLDER = "cat_placeholder.png"
    DOG_PLACEHOLDER = "dog_placeholder.png"

    @staticmethod
    def get_asset_path(filename: str) -> str:
        """
        获取资源文件的完整路径

        Args:
            filename: 文件名

        Returns:
            str: 完整路径
        """
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(current_dir, 'assets', 'images', filename)

    @staticmethod
    def get_avatar_path() -> str:
        """
        获取头像存储目录

        Returns:
            str: 头像目录路径
        """
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        avatar_dir = os.path.join(current_dir, 'avatars')
        if not os.path.exists(avatar_dir):
            os.makedirs(avatar_dir)
        return avatar_dir

    @staticmethod
    def save_avatar(source_path: str, pet_id: int, pet_type: str) -> str:
        """
        保存宠物头像

        Args:
            source_path: 源图片路径
            pet_id: 宠物ID
            pet_type: 宠物类型

        Returns:
            str: 保存后的路径
        """
        if not os.path.exists(source_path):
            return ""

        ext = os.path.splitext(source_path)[1].lower()
        if ext not in ImageHelper.SUPPORTED_FORMATS:
            ext = '.jpg'

        filename = f"{pet_type}_{pet_id}{ext}"
        dest_path = os.path.join(ImageHelper.get_avatar_path(), filename)

        # 复制文件
        shutil.copy2(source_path, dest_path)
        return dest_path

    @staticmethod
    def delete_avatar(avatar_path: str) -> bool:
        """
        删除头像

        Args:
            avatar_path: 头像路径

        Returns:
            bool: 是否删除成功
        """
        if avatar_path and os.path.exists(avatar_path):
            try:
                os.remove(avatar_path)
                return True
            except OSError:
                return False
        return False

    @staticmethod
    def get_placeholder_path(pet_type: str) -> str:
        """
        获取占位头像路径

        Args:
            pet_type: 宠物类型 ('cat' 或 'dog')

        Returns:
            str: 占位图路径
        """
        if pet_type == 'cat':
            return ImageHelper.get_asset_path(ImageHelper.CAT_PLACEHOLDER)
        else:
            return ImageHelper.get_asset_path(ImageHelper.DOG_PLACEHOLDER)

    @staticmethod
    def file_exists(path: str) -> bool:
        """检查文件是否存在"""
        return path and os.path.exists(path)

    @staticmethod
    def get_file_extension(path: str) -> str:
        """获取文件扩展名"""
        return os.path.splitext(path)[1].lower()
