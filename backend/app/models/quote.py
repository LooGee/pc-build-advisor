import uuid
from sqlalchemy import Column, Integer, Boolean, String, Text, ForeignKey, DateTime, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.database import Base
from app.models.base import TimestampMixin


class Quote(Base, TimestampMixin):
    __tablename__ = "quotes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(500), index=True)
    user_input_text = Column(Text, nullable=False)
    analyzed_requirements = Column(JSONB)
    tier = Column(String(20), index=True)
    build_name = Column(String(200))
    cpu_id = Column(UUID(as_uuid=True), ForeignKey("cpus.id"))
    gpu_id = Column(UUID(as_uuid=True), ForeignKey("gpus.id"))
    motherboard_id = Column(UUID(as_uuid=True), ForeignKey("motherboards.id"))
    ram_id = Column(UUID(as_uuid=True), ForeignKey("rams.id"))
    storage_ids = Column(ARRAY(UUID(as_uuid=True)))
    psu_id = Column(UUID(as_uuid=True), ForeignKey("psus.id"))
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"))
    cooler_id = Column(UUID(as_uuid=True), ForeignKey("coolers.id"))
    total_price_krw = Column(Integer)
    components_price_krw = Column(Integer)
    shipping_cost_krw = Column(Integer)
    is_compatible = Column(Boolean, default=True)
    compatibility_issues = Column(JSONB)
    estimated_cpu_benchmark = Column(Integer)
    estimated_gpu_benchmark = Column(Integer)
    estimated_gaming_fps_1080p = Column(Integer)
    estimated_gaming_fps_1440p = Column(Integer)
    estimated_power_consumption_w = Column(Integer)
    llm_model = Column(String(100))
    llm_version = Column(String(50))
    generation_time_ms = Column(Integer)
    expires_at = Column(DateTime(timezone=True))

    components = relationship("QuoteComponent", back_populates="quote", lazy="select")


class QuoteComponent(Base):
    __tablename__ = "quote_components"

    quote_id = Column(UUID(as_uuid=True), ForeignKey("quotes.id", ondelete="CASCADE"), primary_key=True)
    component_id = Column(UUID(as_uuid=True), ForeignKey("components.id"), primary_key=True)
    category = Column(String(50), nullable=False)
    unit_price_krw = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)
    price_source = Column(String(100))
    product_url = Column(String(1000))
    compatibility_status = Column(String(20))
    compatibility_notes = Column(Text)

    quote = relationship("Quote", back_populates="components")
