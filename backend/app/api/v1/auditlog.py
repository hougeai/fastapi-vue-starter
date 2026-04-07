from fastapi import APIRouter, Query
from tortoise.expressions import Q
from models.user import AuditLog
from schemas import SuccessExtra

router = APIRouter()


@router.get('/list', summary='查看操作日志')
async def get_audit_log_list(
    page: int = Query(1, description='页码'),
    page_size: int = Query(10, description='每页数量'),
    user_id: str = Query('', description='操作人ID'),
    module: str = Query('', description='功能模块'),
    method: str = Query('', description='请求方法'),
    summary: str = Query('', description='接口描述'),
    status: int = Query(None, description='状态码'),
    start_time: str = Query('', description='开始时间'),
    end_time: str = Query('', description='结束时间'),
):
    q = Q()
    if user_id:
        q &= Q(user_id=user_id)
    if module:
        q &= Q(module__icontains=module)
    if method:
        q &= Q(method__icontains=method)
    if summary:
        q &= Q(summary__icontains=summary)
    if status:
        q &= Q(status=status)
    if start_time and end_time:
        q &= Q(create_at__range=[start_time, end_time])
    elif start_time:
        q &= Q(create_at__gte=start_time)
    elif end_time:
        q &= Q(create_at__lte=end_time)

    audit_log_objs = await AuditLog.filter(q).offset((page - 1) * page_size).limit(page_size).order_by('-create_at')
    total = await AuditLog.filter(q).count()
    data = [await audit_log.to_dict() for audit_log in audit_log_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)
