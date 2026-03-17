import uuid
from sqlalchemy import Column, Integer, Boolean, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base
from app.models.base import TimestampMixin


class CPU(Base, TimestampMixin):
    __tablename__ = "cpus"

    id = Column(UUID(as_uuid=True), ForeignKey("components.id", ondelete="CASCADE"), primary_key=True)
    socket = Column(String(50), nullable=False, index=True)
    cores = Column(Integer, nullable=False)
    threads = Column(Integer, nullable=False)
    base_clock_ghz = Column(Numeric(4, 2), nullable=False)
    boost_clock_ghz = Column(Numeric(4, 2), nullable=False)
    tdp_w = Column(Integer, nullable=False)
    integrated_graphics = Column(Boolean, default=False)
    igpu_model = Column(String(100))
    cache_l3_mb = Column(Integer)
    supported_memory_type = Column(String(20))
    max_memory_speed_mhz = Column(Integer)
    max_memory_capacity_gb = Column(Integer)
    pcie_version = Column(String(10))
    pcie_lanes = Column(Integer)
    ecc_supported = Column(Boolean, default=False)
    overclockable = Column(Boolean, default=False)
    cinebench_r23_multi_core = Column(Integer, index=True)
    cinebench_r23_single_core = Column(Integer)
    geekbench6_multi = Column(Integer)
    geekbench6_single = Column(Integer)
