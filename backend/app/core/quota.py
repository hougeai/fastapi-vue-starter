from models.user import User, Role


class QuotaService:
    """用户配额服务"""

    async def get_user_role(self, user_id: str, ret_role=False):
        """获取用户角色"""
        user = await User.filter(user_id=user_id).first()
        if not user or not user.role_id:
            return False, '用户不存在'
        role = await Role.filter(id=user.role_id).first()
        if role.id == 1 and not ret_role:  # 管理员无限制
            return True, ''
        return role, ''


quota_service = QuotaService()
