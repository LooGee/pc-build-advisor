import uuid
from sqlalchemy import Column, String, Text, Boolean, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.base import TimestampMixin


class Component(Base, TimestampMixin):
    __tablename__ = "components"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(50), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    model = Column(String(200), nullable=False)
    description = Column(Text)
    image_url = Column(String(500))
    release_date = Column(Date)
    is_active = Column(Boolean, default=True, index=True)

    # Relationships
    prices = relationship("Price", back_populates="component", lazy="select")
    price_history = relationship("PriceHistory", back_populates="component", lazy="select")
