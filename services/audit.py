from sqlalchemy.ext.asyncio import AsyncSession
from models import AuditLog

async def log_action(session: AsyncSession, user_id: int, action: str, details: str = None):
    """Xavfsizlik va o'zgarishlarni kuzatib boruvchi log funksiyasi"""
    log = AuditLog(
        user_id=user_id,
        action=action,
        details=details
    )
    session.add(log)
    await session.commit()