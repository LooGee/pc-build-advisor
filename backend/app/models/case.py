import uuid
from sqlalchemy import Column, Integer, Boolean, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.db.database import Base
from app.models.base import TimestampMixin


class Case(Base, TimestampMixin):
    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), ForeignKey("components.id", ondelete="CASCADE"), primary_key=True)
    supported_form_factors = Column(ARRAY(String))
    max_gpu_length_mm = Column(Integer)
    max_gpu_width_slots = Column(Integer)
    max_cpu_cooler_height_mm = Column(Integer)
    max_front_radiator_size = Column(String)
    max_top_radiator_size = Column(String)
    max_rear_radiator_size = Column(String)
    max_psu_length_mm = Column(Integer)
    supported_psu_form_factors = Column(ARRAY(String))
    drive_bays_35 = Column(Integer)
    drive_bays_25 = Column(Integer)
    m2_slots = Column(Integer)
    front_fan_slots = Column(Integer)
    top_fan_slots = Column(Integer)
    rear_fan_slots = Column(Integer)
    bottom_fan_slots = Column(Integer)
    max_fan_size_mm = Column(Integer)
    has_tempered_glass = Column(Boolean, default=False)
    has_front_panel_rgb = Column(Boolean, default=False)
    front_usb_20_ports = Column(Integer, default=0)
    front_usb_30_ports = Column(Integer, default=0)
    front_usb_type_c = Column(Integer, default=0)
    front_audio_jack = Column(Boolean, default=True)
    form_factor_case = Column(String(50))
    length_mm = Column(Integer)
    width_mm = Column(Integer)
    height_mm = Column(Integer)
    weight_kg = Column(Numeric(5, 2))
    material = Column(String(100))
    color = Column(String(100))
    airflow_design = Column(String(100))
    dust_filters = Column(Boolean, default=True)
