# 服务模块初始化
from .pet_service import PetService
from .vaccine_service import VaccineService
from .weight_service import WeightService
from .reminder_service import ReminderService
from .deworm_service import DewormService
from .stats_service import StatsService
from .feeding_service import FeedingService
from .user_service import UserService

__all__ = ['PetService', 'VaccineService', 'WeightService', 'ReminderService', 'DewormService', 'StatsService', 'FeedingService', 'UserService']