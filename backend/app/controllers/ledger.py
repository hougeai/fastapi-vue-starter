from typing import Optional
from tortoise.expressions import Q
from models.ledger import Ledger, Category, LedgerTemplate
from models.enums import TransactionType
from schemas.ledger import LedgerCreate, LedgerUpdate, CategoryCreate, CategoryUpdate, LedgerTemplateCreate, LedgerTemplateUpdate
from .crud import CRUDBase


# ============ LedgerTemplate Controller ============
class LedgerTemplateController(CRUDBase[LedgerTemplate, LedgerTemplateCreate, LedgerTemplateUpdate]):
    def __init__(self):
        super().__init__(model=LedgerTemplate)

    async def get_by_name(self, name: str) -> Optional[LedgerTemplate]:
        return await self.model.filter(name=name).first()


ledger_template_controller = LedgerTemplateController()


# ============ Ledger Controller ============
class LedgerController(CRUDBase[Ledger, LedgerCreate, LedgerUpdate]):
    def __init__(self):
        super().__init__(model=Ledger)

    async def get_by_user(self, user_id: str) -> list[Ledger]:
        return await self.model.filter(user_id=user_id).order_by('-is_default', '-id').all()

    async def create_for_user(self, user_id: str, obj_in: LedgerCreate) -> Ledger:
        # 如果是第一个账本，设为默认
        if not await self.model.filter(user_id=user_id).exists():
            obj_in.is_default = True
        # 创建时直接设置 user_id
        data = obj_in.model_dump()
        data['user_id'] = user_id
        obj = await self.model.create(**data)
        return obj

    async def create_from_template(self, user_id: str, template_id: int, name: str, description: str = None) -> tuple[Ledger, list[Category]]:
        """从模板创建账本及预设类别"""
        template = await ledger_template_controller.get(id=template_id)
        if not template:
            raise ValueError('Template not found')

        # 创建账本
        ledger_data = LedgerCreate(
            name=name,
            description=description or template.description,
            icon=template.icon,
            template_id=template_id,
        )
        ledger = await self.create_for_user(user_id, ledger_data)

        # 模板类别全部来自系统预设，无需为用户创建自定义类别
        # 直接返回模板对应的系统预设类别
        created_categories = []
        for cat_name in template.categories:
            sys_cat = await Category.filter(name=cat_name, is_system=True, user_id__isnull=True).first()
            if sys_cat:
                created_categories.append(sys_cat)

        return ledger, created_categories

    async def set_default(self, ledger_id: int, user_id: str) -> Ledger:
        """设置默认账本"""
        await self.model.filter(user_id=user_id).update(is_default=False)
        ledger = await self.get(id=ledger_id)
        ledger.is_default = True
        await ledger.save()
        return ledger


ledger_controller = LedgerController()


# ============ Category Controller ============
class CategoryController(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def __init__(self):
        super().__init__(model=Category)

    async def get_by_user(self, user_id: str, tx_type: Optional[TransactionType] = None) -> list[Category]:
        """获取用户的类别列表（包含系统预设+用户自定义）"""
        query = self.model.filter(
            Q(user_id__isnull=True) | Q(user_id=user_id)  # 系统预设 OR 当前用户
        )
        if tx_type:
            query = query.filter(tx_type=tx_type.value)
        return await query.order_by('order', '-is_system', '-id').all()

    async def create_for_user(self, user_id: str, obj_in: CategoryCreate, is_system: bool = False) -> Category:
        """为用户创建类别"""
        data = obj_in.model_dump()
        data['user_id'] = None if is_system else user_id
        data['is_system'] = is_system
        obj = await self.model.create(**data)
        return obj

    async def get_system_categories(self, tx_type: Optional[TransactionType] = None) -> list[Category]:
        """获取系统预设类别"""
        query = self.model.filter(user_id__isnull=True, is_system=True)
        if tx_type:
            query = query.filter(tx_type=tx_type.value)
        return await query.order_by('order').all()

    async def exists_by_name(self, user_id: str, name: str, exclude_id: Optional[int] = None) -> bool:
        """检查用户是否已存在同名类别"""
        query = self.model.filter(
            Q(user_id__isnull=True) | Q(user_id=user_id),
            name=name,
        )
        if exclude_id:
            query = query.exclude(id=exclude_id)
        return await query.exists()


category_controller = CategoryController()
