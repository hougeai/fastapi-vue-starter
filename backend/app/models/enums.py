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
