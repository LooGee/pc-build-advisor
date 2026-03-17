import uuid
from sqlalchemy import Column, Integer, Boolean, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.database import Base
from app.models.base import TimestampMixin


class RAM(Base, TimestampMixin):
    __tablename__ = "rams"

    id = Column(UUID(as_uuid=True), ForeignKey("components.id", ondelete="CASCADE"), primary_key=True)
    type = Column(String(20), nullable=False, index=True)
    speed_mhz = Column(Integer, nullable=False)
    capacity_per_stick_gb = Column(Integer, nullable=False)
    sticks_count = Column(Integer, nullable=False)
    total_capacity_gb = Column(Integer, nullable=False, index=True)
    cas_latency = Column(Integer, nullable=False)
    trcd_ns = Column(Integer)
    trp_ns = Column(Integer)
    tras_ns = Column(Integer)
    voltage_v = Column(Numeric(4, 2))
    height_mm = Column(Integer)
    width_mm = Column(Integer)
    has_rgb = Column(Boolean, default=False)
    rgb_type = Column(String(50))
    has_heatsink = Column(Boolean, default=True)
    xmp_profiles = Column(JSONB)
    docp_profiles = Column(JSONB)
    ecc_supported = Column(Boolean, default=False)
    unbuffered = Column(Boolean, default=True)
