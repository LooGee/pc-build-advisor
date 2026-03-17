import uuid
from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.database import Base
from app.models.base import TimestampMixin


class GPU(Base, TimestampMixin):
    __tablename__ = "gpus"

    id = Column(UUID(as_uuid=True), ForeignKey("components.id", ondelete="CASCADE"), primary_key=True)
    chip_manufacturer = Column(String(50), nullable=False, index=True)
    chip_model = Column(String(100), nullable=False)
    architecture = Column(String(100))
    vram_size_gb = Column(Integer, nullable=False, index=True)
    vram_type = Column(String(20), nullable=False)
    vram_bandwidth_gbs = Column(Integer)
    base_clock_mhz = Column(Integer)
    boost_clock_mhz = Column(Integer)
    tdp_w = Column(Integer, nullable=False)
    length_mm = Column(Integer)
    width_slots = Column(Integer)
    height_mm = Column(Integer)
    required_power_connectors = Column(JSONB)
    recommended_psu_wattage = Column(Integer)
    display_ports = Column(Integer)
    hdmi_ports = Column(Integer)
    usb_type_c = Column(Integer)
    pcie_version = Column(String(10))
    ray_tracing_supported = Column(Boolean, default=True)
    dlss_supported = Column(Boolean, default=False)
    dlss_version = Column(String(10))
    fsr_supported = Column(Boolean, default=False)
    fsr_version = Column(String(10))
    tdmark_timespy_score = Column(Integer, index=True)
    tdmark_firestrike_score = Column(Integer)
    geekbench6_gpu_score = Column(Integer)
