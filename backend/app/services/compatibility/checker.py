from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.compatibility import CompatibilityIssue, IssueSeverity
from app.models.cpu import CPU
from app.models.gpu import GPU
from app.models.motherboard import Motherboard
from app.models.ram import RAM
from app.models.psu import PSU
from app.models.case import Case
from app.models.cooler import Cooler
from app.models.storage import Storage
from app.models.component import Component


class CompatibilityChecker:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_build_compatibility(
        self,
        cpu_id: Optional[str] = None,
        motherboard_id: Optional[str] = None,
        ram_id: Optional[str] = None,
        gpu_id: Optional[str] = None,
        psu_id: Optional[str] = None,
        case_id: Optional[str] = None,
        cooler_id: Optional[str] = None,
        storages: List[str] = None,
    ) -> Tuple[bool, List[CompatibilityIssue]]:
        issues: List[CompatibilityIssue] = []

        # Load components
        cpu = await self._load(CPU, cpu_id) if cpu_id else None
        mb = await self._load(Motherboard, motherboard_id) if motherboard_id else None
        ram = await self._load(RAM, ram_id) if ram_id else None
        gpu = await self._load(GPU, gpu_id) if gpu_id else None
        psu = await self._load(PSU, psu_id) if psu_id else None
        case = await self._load(Case, case_id) if case_id else None
        cooler = await self._load(Cooler, cooler_id) if cooler_id else None

        # Load component names
        cpu_comp = await self._load(Component, cpu_id) if cpu_id else None
        mb_comp = await self._load(Component, motherboard_id) if motherboard_id else None
        ram_comp = await self._load(Component, ram_id) if ram_id else None
        gpu_comp = await self._load(Component, gpu_id) if gpu_id else None
        psu_comp = await self._load(Component, psu_id) if psu_id else None
        case_comp = await self._load(Component, case_id) if case_id else None
        cooler_comp = await self._load(Component, cooler_id) if cooler_id else None

        def name(comp):
            return f"{comp.brand} {comp.model}" if comp else "Unknown"

        # Rule 1: CPU <-> Motherboard socket
        if cpu and mb:
            if cpu.socket != mb.socket:
                issues.append(CompatibilityIssue(
                    issue_id="compat_01",
                    severity=IssueSeverity.ERROR,
                    category_a="cpu", category_b="motherboard",
                    component_a_name=name(cpu_comp),
                    component_b_name=name(mb_comp),
                    title_ko="CPU 소켓 불일치",
                    message_ko=f"'{name(cpu_comp)}'은(는) {cpu.socket} 소켓이지만, '{name(mb_comp)}'은(는) {mb.socket} 소켓입니다.",
                    solution_ko="CPU 또는 메인보드의 소켓을 맞춰주세요.",
                    icon="🔴",
                ))

        # Rule 2: RAM <-> Motherboard DDR type
        if ram and mb:
            if ram.type != mb.memory_type:
                issues.append(CompatibilityIssue(
                    issue_id="compat_02",
                    severity=IssueSeverity.ERROR,
                    category_a="ram", category_b="motherboard",
                    component_a_name=name(ram_comp),
                    component_b_name=name(mb_comp),
                    title_ko="RAM 규격 불일치",
                    message_ko=f"'{name(ram_comp)}'은(는) {ram.type}이지만, '{name(mb_comp)}'은(는) {mb.memory_type}만 지원합니다.",
                    solution_ko=f"{mb.memory_type} RAM으로 변경해주세요.",
                    icon="🔴",
                ))

        # Rule 3: RAM capacity > MB max
        if ram and mb and mb.max_memory_capacity_gb:
            if ram.total_capacity_gb > mb.max_memory_capacity_gb:
                issues.append(CompatibilityIssue(
                    issue_id="compat_03",
                    severity=IssueSeverity.ERROR,
                    category_a="ram", category_b="motherboard",
                    component_a_name=name(ram_comp),
                    component_b_name=name(mb_comp),
                    title_ko="RAM 최대 용량 초과",
                    message_ko=f"RAM 총 용량({ram.total_capacity_gb}GB)이 메인보드 최대 지원 용량({mb.max_memory_capacity_gb}GB)을 초과합니다.",
                    solution_ko="RAM 용량을 줄이거나 더 높은 용량을 지원하는 메인보드를 선택하세요.",
                    icon="🔴",
                ))

        # Rule 4: RAM speed > CPU max (warning)
        if ram and cpu and cpu.max_memory_speed_mhz:
            if ram.speed_mhz > cpu.max_memory_speed_mhz:
                issues.append(CompatibilityIssue(
                    issue_id="compat_04",
                    severity=IssueSeverity.WARNING,
                    category_a="ram", category_b="cpu",
                    component_a_name=name(ram_comp),
                    component_b_name=name(cpu_comp),
                    title_ko="RAM 속도 다운클록",
                    message_ko=f"RAM({ram.speed_mhz}MHz)이 CPU 최대 지원 속도({cpu.max_memory_speed_mhz}MHz)보다 빠릅니다. 다운클록됩니다.",
                    solution_ko=f"{cpu.max_memory_speed_mhz}MHz 이하 RAM으로 변경하면 비용을 절약할 수 있습니다.",
                    icon="🟡",
                ))

        # Rule 5: GPU length > Case max
        if gpu and case and gpu.length_mm and case.max_gpu_length_mm:
            if gpu.length_mm > case.max_gpu_length_mm:
                overflow = gpu.length_mm - case.max_gpu_length_mm
                issues.append(CompatibilityIssue(
                    issue_id="compat_05",
                    severity=IssueSeverity.ERROR,
                    category_a="gpu", category_b="case",
                    component_a_name=name(gpu_comp),
                    component_b_name=name(case_comp),
                    title_ko="GPU가 케이스에 들어가지 않음",
                    message_ko=f"GPU 길이({gpu.length_mm}mm)가 케이스 최대 수용 길이({case.max_gpu_length_mm}mm)를 {overflow}mm 초과합니다.",
                    solution_ko="더 큰 케이스 또는 더 짧은 GPU를 선택하세요.",
                    icon="🔴",
                ))

        # Rule 8: Total power capacity
        if cpu and gpu and psu:
            required = int((cpu.tdp_w + gpu.tdp_w + 100) * 1.2)
            if psu.wattage < required:
                issues.append(CompatibilityIssue(
                    issue_id="compat_08",
                    severity=IssueSeverity.ERROR,
                    category_a="psu", category_b="system",
                    component_a_name=name(psu_comp),
                    component_b_name="시스템 전체",
                    title_ko="파워서플라이 용량 부족",
                    message_ko=f"시스템 예상 소비전력(약 {required}W)이 PSU 용량({psu.wattage}W)을 초과합니다.",
                    solution_ko=f"{required}W 이상의 PSU로 변경해주세요.",
                    icon="🔴",
                ))

        # Rule 9: Cooler <-> CPU socket
        if cooler and cpu and cooler.supported_sockets:
            if cpu.socket not in cooler.supported_sockets:
                issues.append(CompatibilityIssue(
                    issue_id="compat_09",
                    severity=IssueSeverity.ERROR,
                    category_a="cooler", category_b="cpu",
                    component_a_name=name(cooler_comp),
                    component_b_name=name(cpu_comp),
                    title_ko="쿨러 소켓 미지원",
                    message_ko=f"'{name(cooler_comp)}'은(는) {cpu.socket} 소켓을 지원하지 않습니다.",
                    solution_ko=f"{cpu.socket}을 지원하는 쿨러로 변경해주세요.",
                    icon="🔴",
                ))

        # Rule 11: Cooler height > Case max (air cooler)
        if cooler and case and cooler.is_air_cooler and cooler.height_mm and case.max_cpu_cooler_height_mm:
            if cooler.height_mm > case.max_cpu_cooler_height_mm:
                issues.append(CompatibilityIssue(
                    issue_id="compat_11",
                    severity=IssueSeverity.ERROR,
                    category_a="cooler", category_b="case",
                    component_a_name=name(cooler_comp),
                    component_b_name=name(case_comp),
                    title_ko="CPU 쿨러가 케이스에 들어가지 않음",
                    message_ko=f"쿨러 높이({cooler.height_mm}mm)가 케이스 최대 수용 높이({case.max_cpu_cooler_height_mm}mm)를 초과합니다.",
                    solution_ko="더 낮은 쿨러 또는 더 넓은 케이스를 선택하세요.",
                    icon="🔴",
                ))

        # Rule 14: Motherboard <-> Case form factor
        if mb and case and case.supported_form_factors:
            if mb.form_factor not in case.supported_form_factors:
                issues.append(CompatibilityIssue(
                    issue_id="compat_14",
                    severity=IssueSeverity.ERROR,
                    category_a="motherboard", category_b="case",
                    component_a_name=name(mb_comp),
                    component_b_name=name(case_comp),
                    title_ko="메인보드 폼팩터 불일치",
                    message_ko=f"'{name(mb_comp)}'({mb.form_factor})은(는) '{name(case_comp)}'가 지원하는 폼팩터({', '.join(case.supported_form_factors)})와 맞지 않습니다.",
                    solution_ko=f"{mb.form_factor}를 지원하는 케이스로 변경해주세요.",
                    icon="🔴",
                ))

        is_compatible = not any(i.severity == IssueSeverity.ERROR for i in issues)
        return is_compatible, issues

    async def _load(self, model_class, id_str: str):
        if not id_str:
            return None
        import uuid
        try:
            obj_id = uuid.UUID(str(id_str))
            result = await self.db.get(model_class, obj_id)
            return result
        except Exception:
            return None
