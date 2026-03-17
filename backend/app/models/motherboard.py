import uuid
from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from app.db.database import Base
from app.models.base import TimestampMixin


class Motherboard(Base, TimestampMixin):
    __tablename__ = "motherboards"

    id = Column(UUID(as_uuid=True), ForeignKey("components.id", ondelete="CASCADE"), primary_key=True)
    socket = Column(String(50), nullable=False, index=True)
    chipset = Column(String(100), nullable=False, index=True)
    form_factor = Column(String(20), nullable=False, index=True)
    memory_type = Column(String(20), nullable=False)
    memory_slots = Column(Integer, nullable=False)
    max_memory_capacity_gb = Column(Integer)
    max_memory_speed_mhz = Column(Integer)
    supports_xmp = Column(Boolean, default=True)
    supports_docp = Column(Boolean, default=True)
    m2_slots = Column(Integer, nullable=False)
    m2_slot_details = Column(JSONB)
    pcie_x16_slots = Column(Integer)
    pcie_x16_type = Column(JSONB)
    pcie_x1_slots = Column(Integer)
    sata_ports = Column(Integer, nullable=False)
    usb_20_headers = Column(Integer)
    usb_30_headers = Column(Integer)
    usb_type_c_headers = Column(Integer)
    wifi = Column(Boolean, default=False)
    wifi_standard = Column(String(20))
    bluetooth = Column(Boolean, default=False)
    bluetooth_version = Column(String(10))
    audio_codec = Column(String(100))
    lan_ports = Column(Integer, default=1)
    lan_speed = Column(String(20))
    rgb_headers = Column(Integer, default=0)
    argb_headers = Column(Integer, default=0)
    length_mm = Column(Integer)
    width_mm = Column(Integer)
