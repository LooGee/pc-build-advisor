import uuid
from sqlalchemy import Column, Boolean, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.database import Base
from app.models.base import TimestampMixin


class CompatibilityRule(Base, TimestampMixin):
    __tablename__ = "compatibility_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_name = Column(String(200), nullable=False)
    rule_type = Column(String(100), nullable=False)
    category_a = Column(String(50))
    category_b = Column(String(50))
    validation_logic = Column(JSONB, nullable=False)
    error_message_ko = Column(Text)
    warning_message_ko = Column(Text)
    severity = Column(String(20))
    is_active = Column(Boolean, default=True)
