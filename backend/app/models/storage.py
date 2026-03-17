import uuid
from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base
from app.models.base import TimestampMixin


class Storage(Base, TimestampMixin):
    __tablename__ = "storages"

    id = Column(UUID(as_uuid=True), ForeignKey("components.id", ondelete="CASCADE"), primary_key=True)
    type = Column(String(50), nullable=False, index=True)
    form_factor = Column(String(50), nullable=False)
    interface = Column(String(50), nullable=False, index=True)
    capacity_gb = Column(Integer, nullable=False, index=True)
    read_speed_mbs = Column(Integer)
    write_speed_mbs = Column(Integer)
    random_read_iops = Column(Integer)
    random_write_iops = Column(Integer)
    endurance_tbw = Column(Integer)
    mtbf_hours = Column(Integer)
    warranty_years = Column(Integer)
    has_dram_cache = Column(Boolean, default=True)
    cache_size_mb = Column(Integer)
    nand_type = Column(String(50))
    length_mm = Column(Integer)
    width_mm = Column(Integer)
    height_mm = Column(Integer)
    weight_grams = Column(Integer)
