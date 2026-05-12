from typing import Optional
from tortoise.expressions import Q
from models.ledger import Ledger, Category
from models.enums import TransactionType
from schemas.ledger import LedgerCreate, LedgerUpdate, CategoryCreate, CategoryUpdate
from .crud import CRUDBase


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
