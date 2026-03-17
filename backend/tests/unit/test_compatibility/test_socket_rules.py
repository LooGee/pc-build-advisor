import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.compatibility.checker import CompatibilityChecker
from app.schemas.compatibility import IssueSeverity


@pytest.mark.asyncio
async def test_socket_mismatch_raises_error():
    mock_db = AsyncMock()

    cpu = MagicMock()
    cpu.socket = "LGA1700"

    mb = MagicMock()
    mb.socket = "AM5"
    mb.memory_type = "DDR5"
    mb.max_memory_capacity_gb = 128
    mb.supported_form_factors = ["ATX", "mATX"]

    ram = MagicMock()
    ram.type = "DDR5"
    ram.speed_mhz = 5600
    ram.total_capacity_gb = 32

    cpu_comp = MagicMock()
    cpu_comp.brand = "Intel"
    cpu_comp.model = "i9-14900K"

    mb_comp = MagicMock()
    mb_comp.brand = "ASUS"
    mb_comp.model = "ROG STRIX B650"

    async def mock_get(model_class, id_val):
        from app.models.cpu import CPU
        from app.models.motherboard import Motherboard
        from app.models.component import Component
        if model_class == CPU:
            return cpu
        elif model_class == Motherboard:
            return mb
        elif model_class == Component:
            if str(id_val) == "cpu-id":
                return cpu_comp
            return mb_comp
        return None

    mock_db.get = mock_get

    checker = CompatibilityChecker(mock_db)
    is_compat, issues = await checker.check_build_compatibility(
        cpu_id="cpu-id",
        motherboard_id="mb-id",
    )

    assert not is_compat
    assert any(i.issue_id == "compat_01" for i in issues)
    assert any(i.severity == IssueSeverity.ERROR for i in issues)
