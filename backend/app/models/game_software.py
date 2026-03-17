import uuid
from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base
from app.models.base import TimestampMixin


class GameRequirement(Base, TimestampMixin):
    __tablename__ = "game_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_name = Column(String(200), nullable=False, unique=True, index=True)
    aliases = Column(String(500))  # comma-separated
    genre = Column(String(100))
    min_cpu_benchmark_single = Column(Integer)
    min_cpu_benchmark_multi = Column(Integer)
    min_gpu_benchmark = Column(Integer)
    min_ram_gb = Column(Integer)
    min_storage_gb = Column(Integer)
    min_resolution = Column(String(20))
    min_fps = Column(Integer)
    rec_cpu_benchmark_single = Column(Integer)
    rec_cpu_benchmark_multi = Column(Integer)
    rec_gpu_benchmark = Column(Integer)
    rec_ram_gb = Column(Integer)
    rec_storage_gb = Column(Integer)
    rec_resolution = Column(String(20))
    rec_fps = Column(Integer)
    ultra_cpu_benchmark_single = Column(Integer)
    ultra_cpu_benchmark_multi = Column(Integer)
    ultra_gpu_benchmark = Column(Integer)
    ultra_ram_gb = Column(Integer)
    ultra_storage_gb = Column(Integer)
    ultra_resolution = Column(String(20))
    ultra_fps = Column(Integer)
    supports_ray_tracing = Column(Boolean, default=False)
    supports_dlss = Column(Boolean, default=False)
    supports_fsr = Column(Boolean, default=False)
    release_year = Column(Integer)


class SoftwareRequirement(Base, TimestampMixin):
    __tablename__ = "software_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    software_name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    vendor = Column(String(100))
    min_cpu_benchmark_single = Column(Integer)
    min_cpu_benchmark_multi = Column(Integer)
    min_gpu_benchmark = Column(Integer)
    min_ram_gb = Column(Integer)
    min_storage_gb = Column(Integer)
    rec_cpu_benchmark_single = Column(Integer)
    rec_cpu_benchmark_multi = Column(Integer)
    rec_gpu_benchmark = Column(Integer)
    rec_ram_gb = Column(Integer)
    rec_storage_gb = Column(Integer)
    professional_cpu_benchmark_multi = Column(Integer)
    professional_gpu_benchmark = Column(Integer)
    professional_ram_gb = Column(Integer)
    professional_storage_gb = Column(Integer)
    needs_gpu_acceleration = Column(Boolean, default=False)
    preferred_gpu_vendor = Column(String(50))
    cuda_supported = Column(Boolean, default=False)
    opencl_supported = Column(Boolean, default=False)
    hip_supported = Column(Boolean, default=False)
    release_year = Column(Integer)
