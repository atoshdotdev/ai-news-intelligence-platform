import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ainews.core.db.base import Base

if TYPE_CHECKING:
    from ainews.core.db.models import Source


class SourceBlacklist(Base):
    __tablename__ = "source_blacklist"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("sources.id"), nullable=False, index=True
    )
    url_fragment: Mapped[str] = mapped_column(String(255), nullable=False)

    source: Mapped["Source"] = relationship(back_populates="blacklist_entries")

    __table_args__ = (
        UniqueConstraint("source_id", "url_fragment", name="uq_source_blacklist"),
    )
