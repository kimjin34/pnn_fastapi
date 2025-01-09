from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("postgresql+asyncpg://root:0304@svc.sel4.cloudtype.app:30346/root", echo=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def provide_session():
    async with async_session() as session:
        yield session
