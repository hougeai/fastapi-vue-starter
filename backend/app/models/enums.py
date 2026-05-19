from enum import Enum


# 需要获取所有可用选项时（如下拉菜单）；进行数据验证时（检查值是否在允许范围内）；生成API文档时（展示所有可用选项）
class EnumBase(Enum):
    @classmethod
    # 获取所有枚举值
    def get_member_values(cls):
        return [item.value for item in cls._member_map_.values()]

    # 获取所有枚举名称
    @classmethod
    def get_member_names(cls):
        return [name for name in cls._member_names_]


class MethodType(str, Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'


class MenuType(str, Enum):
    CATALOG = 'catalog'  # 目录
    MENU = 'menu'  # 菜单


# 语种枚举
class LanguageType(str, Enum):
    ENGLISH = 'english'  # 英语
    CHINESE = 'chinese'  # 中文
    JAPANESE = 'japanese'  # 日语
    KOREAN = 'korean'  # 韩语
    GERMAN = 'german'  # 德语
    FRENCH = 'french'  # 法语
    SPANISH = 'spanish'  # 西班牙语
    ARABIC = 'arabic'  # 阿拉伯语


# 交付类型枚举
class DeliveryType(str, Enum):
    PHYSICAL = 'physical'  # 实物发货
    VIRTUAL = 'virtual'  # 虚拟发货
    NONE = 'none'  # 不发货


# 项目状态枚举
class ProjectStatus(int, Enum):
    DELETED = 0  # 已删除
    NORMAL = 1  # 正常


# 直播平台
class PlatformType(str, Enum):
    TikTok = 'tiktok'  # tiktok
    Douyin = 'douyin'  # 抖音


# 直播间状态枚举
class LiveRoomStatus(str, Enum):
    OFFLINE = 'offline'  # 离线
    ONLINE = 'online'  # 在线


# 直播间内容策略
class ContentStrategy(str, Enum):
    AUTO = 'auto'  # 自动
    HOT = 'hot'  # 预热引流
    PRODUCT = 'product'  # 产品讲解
    QA = 'qa'  # 答疑解惑
    INTERACTIVE = 'interactive'  # 互动活跃
    PROMOTION = 'promotion'  # 促销转化
    BRAND = 'brand'  # 品牌塑造


# 交易类型枚举
class TransactionType(int, Enum):
    INCOME = 1   # 收入
    EXPENSE = 2  # 支出


# 系统预设类别
# tx_type: 1=收入, 2=支出
SYSTEM_CATEGORIES = [
    # 支出类别
    {'name': '餐饮', 'tx_type': 2, 'icon': 'restaurant', 'order': 10},
    {'name': '交通', 'tx_type': 2, 'icon': 'car', 'order': 20},
    {'name': '购物', 'tx_type': 2, 'icon': 'shopping', 'order': 30},
    {'name': '娱乐', 'tx_type': 2, 'icon': 'game', 'order': 40},
    {'name': '房租', 'tx_type': 2, 'icon': 'home', 'order': 50},
    {'name': '医疗', 'tx_type': 2, 'icon': 'hospital', 'order': 60},
    {'name': '教育', 'tx_type': 2, 'icon': 'book', 'order': 70},
    {'name': '通讯', 'tx_type': 2, 'icon': 'phone', 'order': 80},
    {'name': '服装', 'tx_type': 2, 'icon': 'shirt', 'order': 90},
    {'name': '日用品', 'tx_type': 2, 'icon': 'basket', 'order': 100},
    {'name': '社交', 'tx_type': 2, 'icon': 'users', 'order': 110},
    {'name': '旅行', 'tx_type': 2, 'icon': 'plane', 'order': 120},
    {'name': '宠物', 'tx_type': 2, 'icon': 'paw', 'order': 130},
    {'name': '其他支出', 'tx_type': 2, 'icon': 'more', 'order': 999},
    # 模板专用类别（旅行）
    {'name': '机票', 'tx_type': 2, 'icon': 'plane', 'order': 140},
    {'name': '住宿', 'tx_type': 2, 'icon': 'bed', 'order': 150},
    {'name': '门票', 'tx_type': 2, 'icon': 'ticket', 'order': 160},
    # 模板专用类别（医疗）
    {'name': '门诊', 'tx_type': 2, 'icon': 'stethoscope', 'order': 170},
    {'name': '住院', 'tx_type': 2, 'icon': 'bed', 'order': 180},
    {'name': '药品', 'tx_type': 2, 'icon': 'pill', 'order': 190},
    {'name': '检查', 'tx_type': 2, 'icon': 'activity', 'order': 200},
    # 收入类别
    {'name': '工资', 'tx_type': 1, 'icon': 'wallet', 'order': 10},
    {'name': '奖金', 'tx_type': 1, 'icon': 'gift', 'order': 20},
    {'name': '投资收益', 'tx_type': 1, 'icon': 'trending-up', 'order': 30},
    {'name': '兼职', 'tx_type': 1, 'icon': 'briefcase', 'order': 40},
    {'name': '红包', 'tx_type': 1, 'icon': 'gift', 'order': 50},
    {'name': '退款', 'tx_type': 1, 'icon': 'rotate-ccw', 'order': 60},
    {'name': '其他收入', 'tx_type': 1, 'icon': 'more', 'order': 999},
]


# 账本模板
LEDGER_TEMPLATES = [
    {
        'name': '日常账本',
        'description': '适合日常生活收支记录',
        'icon': 'calendar',
        'categories': ['工资', '奖金', '餐饮', '交通', '购物', '娱乐', '其他支出'],
    },
    {
        'name': '旅行账本',
        'description': '适合旅行游玩开支记录',
        'icon': 'plane',
        'categories': ['机票', '住宿', '餐饮', '交通', '门票', '购物', '其他支出'],
    },
    {
        'name': '医疗账本',
        'description': '适合医疗健康开支记录',
        'icon': 'heart',
        'categories': ['门诊', '住院', '药品', '检查', '其他支出'],
    },
    {
        'name': '家庭账本',
        'description': '适合家庭共同开支记录',
        'icon': 'home',
        'categories': ['工资', '餐饮', '教育', '医疗', '房租', '其他支出'],
    },
]
