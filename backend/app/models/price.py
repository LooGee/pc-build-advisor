import uuid
from sqlalchemy import Column, Integer, Boolean, String, Numeric, ForeignKey, DateTime, Computed
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base
from app.models.base import TimestampMixin


class Price(Base, TimestampMixin):
    __tablename__ = "prices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    component_id = Column(UUID(as_uuid=True), ForeignKey("components.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(100), nullable=False, index=True)
    price_krw = Column(Integer, nullable=False)
    price_usd = Column(Numeric(10, 2))
    shipping_cost_krw = Column(Integer, default=0)
    in_stock = Column(Boolean, default=True, index=True)
    stock_quantity = Column(Integer)
    product_url = Column(String(1000))
    product_name = Column(String(500))
    seller_name = Column(String(200))
    has_discount = Column(Boolean, default=False)
    discount_rate_percent = Column(Integer)
    original_price_krw = Column(Integer)
    free_shipping = Column(Boolean, default=False)
    rocket_delivery = Column(Boolean, default=False)
    last_checked = Column(DateTime(timezone=True))
    price_trend = Column(String(20))
    days_since_change = Column(Integer)

    component = relationship("Component", back_populates="prices")

    @property
    def total_price_krw(self):
        return self.price_krw + (self.shipping_cost_krw or 0)


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    component_id = Column(UUID(as_uuid=True), ForeignKey("components.id", ondelete="CASCADE"), nullable=False)
    source = Column(String(100), nullable=False)
    price_krw = Column(Integer, nullable=False)
    recorded_at = Column(DateTime(timezone=True))

    component = relationship("Component", back_populates="price_history")
