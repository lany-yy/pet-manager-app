"""
宠物档案业务逻辑模块
"""
from typing import List, Optional, Dict, Any
from datetime import date

from database import DatabaseHelper, get_db_manager
from models.pet import Pet
from utils.image_helper import ImageHelper


class PetService:
    """宠物档案服务类"""

    def __init__(self):
        """初始化宠物服务"""
        db_manager = get_db_manager()
        self.db_helper = DatabaseHelper(db_manager)

    def add_pet(self, name: str, pet_type: str, breed: str = None,
                birthday: date = None, gender: str = 'unknown',
                avatar_path: str = None) -> Pet:
        """
        添加新宠物

        Args:
            name: 宠物名字
            pet_type: 类型 ('cat' 或 'dog')
            breed: 品种
            birthday: 出生日期
            gender: 性别
            avatar_path: 头像路径

        Returns:
            Pet: 新创建的宠物对象
        """
        # 保存头像
        saved_avatar = None
        if avatar_path:
            # 先插入获取ID
            pet_id = self.db_helper.insert_pet(
                name, pet_type, breed, birthday, gender, avatar_path
            )
        else:
            pet_id = self.db_helper.insert_pet(
                name, pet_type, breed, birthday, gender, avatar_path
            )

        # 如果有头像文件，复制到存储目录
        if avatar_path and pet_id:
            saved_avatar = ImageHelper.save_avatar(avatar_path, pet_id, pet_type)
            if saved_avatar != avatar_path:
                # 更新头像路径
                self.db_helper.update_pet(pet_id, avatar_path=saved_avatar)

        return self.get_pet_by_id(pet_id)

    def get_all_pets(self) -> List[Pet]:
        """
        获取所有宠物

        Returns:
            List[Pet]: 宠物列表
        """
        pets_data = self.db_helper.get_all_pets()
        return [Pet.from_dict(data) for data in pets_data]

    def get_pet_by_id(self, pet_id: int) -> Optional[Pet]:
        """
        根据ID获取宠物

        Args:
            pet_id: 宠物ID

        Returns:
            Optional[Pet]: 宠物对象，不存在返回None
        """
        pet_data = self.db_helper.get_pet_by_id(pet_id)
        return Pet.from_dict(pet_data) if pet_data else None

    def update_pet(self, pet_id: int, **kwargs) -> bool:
        """
        更新宠物信息

        Args:
            pet_id: 宠物ID
            **kwargs: 要更新的字段

        Returns:
            bool: 是否更新成功
        """
        # 处理头像更新
        if 'avatar_path' in kwargs and kwargs['avatar_path']:
            avatar_path = kwargs['avatar_path']
            pet = self.get_pet_by_id(pet_id)
            if pet:
                saved_avatar = ImageHelper.save_avatar(avatar_path, pet_id, pet.type)
                kwargs['avatar_path'] = saved_avatar

        return self.db_helper.update_pet(pet_id, **kwargs)

    def delete_pet(self, pet_id: int) -> bool:
        """
        删除宠物

        Args:
            pet_id: 宠物ID

        Returns:
            bool: 是否删除成功
        """
        # 先删除头像
        pet = self.get_pet_by_id(pet_id)
        if pet and pet.avatar_path:
            ImageHelper.delete_avatar(pet.avatar_path)

        return self.db_helper.delete_pet(pet_id)

    def get_pet_count(self) -> Dict[str, int]:
        """
        获取宠物数量统计

        Returns:
            Dict[str, int]: 数量统计
        """
        return self.db_helper.get_pet_count()

    def search_pets(self, keyword: str) -> List[Pet]:
        """
        搜索宠物

        Args:
            keyword: 搜索关键词

        Returns:
            List[Pet]: 匹配的宠物列表
        """
        all_pets = self.get_all_pets()
        keyword = keyword.lower()
        return [
            pet for pet in all_pets
            if keyword in pet.name.lower() or keyword in (pet.breed or "").lower()
        ]

    def filter_pets_by_type(self, pet_type: str) -> List[Pet]:
        """
        按类型筛选宠物

        Args:
            pet_type: 宠物类型 ('cat', 'dog', 或 'all')

        Returns:
            List[Pet]: 匹配的宠物列表
        """
        if pet_type == 'all':
            return self.get_all_pets()
        return [pet for pet in self.get_all_pets() if pet.type == pet_type]
