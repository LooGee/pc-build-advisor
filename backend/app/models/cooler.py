import uuid
from sqlalchemy import Column, Integer, Boolean, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.db.database import Base
from app.models.base import TimestampMixin


class Cooler(Base, TimestampMixin):
    __tablename__ = "coolers"

    id = Column(UUID(as_uuid=True), ForeignKey("components.id", ondelete="CASCADE"), primary_key=True)
    type = Column(String(50), nullable=False, index=True)
    supported_sockets = Column(ARRAY(String))
    is_air_cooler = Column(Boolean, default=False)
    height_mm = Column(Integer)
    mounting_type = Column(String(100))
    is_liquid_cooler = Column(Boolean, default=False)
    radiator_size = Column(String(50))
    fan_count = Column(Integer)
    fan_size_mm = Column(Integer)
    radiator_thickness_mm = Column(Integer)
    block_material = Column(String(100))
    has_rgb = Column(Boolean, default=False)
    rgb_type = Column(String(50))
    tdp_rating_w = Column(Integer, nullable=False, index=True)
    noise_level_dba = Column(Integer)
    max_rpm = Column(Integer)
    weight_kg = Column(Numeric(5, 2))
    mounting_bracket_included = Column(Boolean, default=True)
    requires_thermal_paste = Column(Boolean, default=True)
    thermal_paste_included = Column(Boolean, default=False)
