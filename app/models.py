from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有 ORM 模型的基础类。"""


class Task(Base):
    """任务数据库模型。"""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="PENDING",
    )
    priority: Mapped[int] = mapped_column(
        nullable=False,
        server_default="1",
    )
