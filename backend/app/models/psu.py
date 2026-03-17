import uuid
from sqlalchemy import Column, Integer, Boolean, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base
from app.models.base import TimestampMixin


class PSU(Base, TimestampMixin):
    __tablename__ = "psus"

    id = Column(UUID(as_uuid=True), ForeignKey("components.id", ondelete="CASCADE"), primary_key=True)
    wattage = Column(Integer, nullable=False, index=True)
    efficiency_rating = Column(String(50), nullable=False, index=True)
    modular_type = Column(String(50), nullable=False)
    form_factor = Column(String(50), nullable=False)
    length_mm = Column(Integer)
    width_mm = Column(Integer)
    height_mm = Column(Integer)
    weight_kg = Column(Numeric(5, 2))
    fan_size_mm = Column(Integer)
    fan_type = Column(String(50))
    has_zero_rpm_mode = Column(Boolean, default=False)
    connector_24pin = Column(Integer, default=1)
    connector_8pin_cpu = Column(Integer)
    connector_6pin_pcie = Column(Integer)
    connector_8pin_pcie = Column(Integer)
    connector_12vhpwr = Column(Boolean, default=False)
    connector_sata = Column(Integer)
    connector_perif = Column(Integer)
    ocp_protection = Column(Boolean, default=True)
    scp_protection = Column(Boolean, default=True)
    opp_protection = Column(Boolean, default=True)
    pfc_active = Column(Boolean, default=False)
