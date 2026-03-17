# PC Build Advisor - 호환성 체크 엔진

> 📁 **전체 문서 목차**: [INDEX.md](./INDEX.md)

## 6. 호환성 체크 엔진 (상세 설계)

### 6.1 호환성 검증 규칙 목록

#### 1. CPU ↔ Motherboard (소켓)
```json
{
  "rule_id": "compat_01",
  "type": "socket_match",
  "description": "CPU와 MB 소켓 일치 확인",
  "check_fields": ["cpu.socket", "motherboard.socket"],
  "severity": "error",
  "validation_logic": {
    "socket_mappings": {
      "LGA1700": ["Z790", "B760", "H770"],
      "LGA1851": ["Z890", "B850"],
      "AM5": ["X870-E", "X870", "B850", "X670-E", "X670", "B650-E", "B650"],
      "AM4": ["X570", "B550", "B450", "X470"]
    }
  }
}
```

#### 2. RAM ↔ Motherboard (DDR 세대)
```json
{
  "rule_id": "compat_02",
  "type": "memory_type_match",
  "description": "RAM 타입(DDR4/DDR5) MB 지원 여부",
  "check_fields": ["ram.type", "motherboard.memory_type"],
  "severity": "error",
  "validation_logic": {
    "must_match": true
  }
}
```

#### 3. RAM ↔ Motherboard (용량 및 슬롯)
```json
{
  "rule_id": "compat_03",
  "type": "memory_capacity",
  "description": "RAM 최대 용량 및 슬롯 수 확인",
  "check_fields": ["ram.total_capacity_gb", "motherboard.max_memory_capacity_gb", "motherboard.memory_slots"],
  "severity": "error",
  "validation_logic": {
    "total_capacity_must_not_exceed_max": true,
    "required_slots": "ram.total_capacity_gb / (ram.capacity_per_stick_gb) <= motherboard.memory_slots"
  }
}
```

#### 4. RAM ↔ CPU (지원 속도)
```json
{
  "rule_id": "compat_04",
  "type": "memory_speed",
  "description": "CPU 메모리 컨트롤러가 지원하는 최대 속도 확인",
  "check_fields": ["ram.speed_mhz", "cpu.max_memory_speed_mhz"],
  "severity": "warning",
  "validation_logic": {
    "if": "ram.speed_mhz > cpu.max_memory_speed_mhz",
    "then": "RAM will run at CPU max speed, performance downgrade",
    "recommendation": "Choose slower RAM for perfect match"
  }
}
```

#### 5. GPU ↔ Case (길이)
```json
{
  "rule_id": "compat_05",
  "type": "physical_fit_gpu_length",
  "description": "GPU 길이가 케이스 최대 수용 길이 이하인지 확인",
  "check_fields": ["gpu.length_mm", "case.max_gpu_length_mm"],
  "severity": "error",
  "validation_logic": {
    "gpu_length_must_not_exceed": "case.max_gpu_length_mm"
  }
}
```

#### 6. GPU ↔ Case (너비/슬롯)
```json
{
  "rule_id": "compat_06",
  "type": "physical_fit_gpu_width",
  "description": "GPU 너비(슬롯 수)가 케이스 지원 슬롯 이하인지 확인",
  "check_fields": ["gpu.width_slots", "case.max_gpu_width_slots"],
  "severity": "error",
  "validation_logic": {
    "gpu_width_slots_must_not_exceed": "case.max_gpu_width_slots"
  }
}
```

#### 7. GPU ↔ PSU (전원 커넥터)
```json
{
  "rule_id": "compat_07",
  "type": "power_connectors",
  "description": "PSU가 GPU 필요 커넥터 제공하는지 확인",
  "check_fields": ["gpu.required_power_connectors", "psu.connectors"],
  "severity": "error",
  "validation_logic": {
    "8pin_required": "if gpu.required_power_connectors.8pin > 0 then psu.connector_8pin_pcie >= gpu.required_power_connectors.8pin",
    "6pin_required": "if gpu.required_power_connectors.6pin > 0 then psu.connector_6pin_pcie >= gpu.required_power_connectors.6pin",
    "12vhpwr_required": "if gpu.required_power_connectors.12vhpwr then psu.connector_12vhpwr == true"
  }
}
```

#### 8. GPU ↔ PSU (전력 용량)
```json
{
  "rule_id": "compat_08",
  "type": "total_power_capacity",
  "description": "PSU 용량이 시스템 총 소비 전력 + 20% 여유 이상인지 확인",
  "check_fields": ["gpu.tdp_w", "cpu.tdp_w", "psu.wattage"],
  "severity": "error",
  "validation_logic": {
    "total_system_power": "(cpu.tdp_w + gpu.tdp_w + 100) * 1.2 <= psu.wattage",
    "100W": "주변기기(MB, SSD, 쿨러 등) 예상치"
  }
}
```

#### 9. Cooler ↔ CPU (소켓)
```json
{
  "rule_id": "compat_09",
  "type": "cooler_socket",
  "description": "쿨러가 CPU 소켓 지원하는지 확인",
  "check_fields": ["cooler.supported_sockets", "cpu.socket"],
  "severity": "error",
  "validation_logic": {
    "cpu_socket_in_cooler_supported": "cpu.socket IN cooler.supported_sockets"
  }
}
```

#### 10. Cooler ↔ CPU (냉각 용량)
```json
{
  "rule_id": "compat_10",
  "type": "cooler_tdp_capacity",
  "description": "쿨러 냉각 용량이 CPU TDP 이상인지 확인",
  "check_fields": ["cooler.tdp_rating_w", "cpu.tdp_w"],
  "severity": "warning",
  "validation_logic": {
    "cooler_tdp_must_be_gte": "cooler.tdp_rating_w >= cpu.tdp_w",
    "if_less": "May cause thermal throttling under heavy load"
  }
}
```

#### 11. Cooler ↔ Case (높이 - 타워)
```json
{
  "rule_id": "compat_11",
  "type": "physical_fit_cooler_height",
  "description": "타워 쿨러 높이가 케이스 수용 높이 이하인지 확인",
  "check_fields": ["cooler.type", "cooler.height_mm", "case.max_cpu_cooler_height_mm"],
  "severity": "error",
  "validation_logic": {
    "if": "cooler.type == 'air'",
    "then": "cooler.height_mm <= case.max_cpu_cooler_height_mm"
  }
}
```

#### 12. Cooler ↔ Case (라디에이터 - 수냉)
```json
{
  "rule_id": "compat_12",
  "type": "physical_fit_radiator",
  "description": "수냉 라디에이터가 케이스 마운팅 공간에 맞는지 확인",
  "check_fields": ["cooler.type", "cooler.radiator_size", "case.max_front_radiator_size", "case.max_top_radiator_size"],
  "severity": "error",
  "validation_logic": {
    "if": "cooler.type.includes('liquid')",
    "then": "cooler.radiator_size IN [case.max_front_radiator_size, case.max_top_radiator_size, case.max_rear_radiator_size]"
  }
}
```

#### 13. RAM ↔ Cooler (높이 간섭)
```json
{
  "rule_id": "compat_13",
  "type": "ram_cooler_interference",
  "description": "대형 타워 쿨러와 키 큰 RAM 간섭 확인",
  "check_fields": ["ram.height_mm", "cooler.height_mm", "cooler.type"],
  "severity": "warning",
  "validation_logic": {
    "if": "cooler.type == 'air' AND cooler.height_mm > 150 AND ram.height_mm > 40",
    "then": "Potential interference, may need to install RAM first or choose shorter cooler"
  }
}
```

#### 14. Motherboard ↔ Case (폼팩터)
```json
{
  "rule_id": "compat_14",
  "type": "formfactor_fit",
  "description": "MB 폼팩터가 케이스 지원 폼팩터인지 확인",
  "check_fields": ["motherboard.form_factor", "case.supported_form_factors"],
  "severity": "error",
  "validation_logic": {
    "motherboard_form_factor_in_case_supported": "motherboard.form_factor IN case.supported_form_factors"
  }
}
```

#### 15. PSU ↔ Case (폼팩터)
```json
{
  "rule_id": "compat_15",
  "type": "psu_formfactor_fit",
  "description": "PSU 폼팩터가 케이스 지원 폼팩터인지 확인",
  "check_fields": ["psu.form_factor", "case.supported_psu_form_factors"],
  "severity": "error",
  "validation_logic": {
    "psu_form_factor_in_case_supported": "psu.form_factor IN case.supported_psu_form_factors"
  }
}
```

#### 16. PSU ↔ Case (길이)
```json
{
  "rule_id": "compat_16",
  "type": "psu_length_fit",
  "description": "PSU 길이가 케이스 최대 PSU 길이 이하인지 확인",
  "check_fields": ["psu.length_mm", "case.max_psu_length_mm"],
  "severity": "error",
  "validation_logic": {
    "psu_length_must_not_exceed": "psu.length_mm <= case.max_psu_length_mm"
  }
}
```

#### 17. Storage ↔ Motherboard (M.2 슬롯)
```json
{
  "rule_id": "compat_17",
  "type": "m2_slot_availability",
  "description": "NVMe 스토리지용 M.2 슬롯 유효성 확인",
  "check_fields": ["storage.type", "storage.interface", "motherboard.m2_slots"],
  "severity": "error",
  "validation_logic": {
    "if": "storage.type == 'NVMe' AND motherboard.m2_slots > 0",
    "then": "M.2 슬롯 유형 확인 (PCIe Gen 호환성)"
  }
}
```

#### 18. Storage ↔ Motherboard (SATA 포트)
```json
{
  "rule_id": "compat_18",
  "type": "sata_port_availability",
  "description": "SATA 스토리지용 SATA 포트 유효성 확인",
  "check_fields": ["storage.type", "motherboard.sata_ports"],
  "severity": "error",
  "validation_logic": {
    "if": "storage.type IN ['SATA_SSD', 'HDD']",
    "then": "motherboard.sata_ports > 0"
  }
}
```

### 6.2 호환성 체크 엔진 (Python 구현 예시)

```python
# backend/app/services/compatibility.py

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import *
from app.schemas import CompatibilityIssue, QuoteRequest

class CompatibilityChecker:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_build_compatibility(
        self,
        cpu_id: str,
        motherboard_id: str,
        ram_id: str,
        gpu_id: str,
        psu_id: str,
        case_id: str,
        cooler_id: str,
        storages: List[str]
    ) -> tuple[bool, List[CompatibilityIssue]]:
        """전체 PC 빌드 호환성 검증"""

        issues: List[CompatibilityIssue] = []

        # 부품 정보 로드
        cpu = await self.db.get(CPU, cpu_id)
        mb = await self.db.get(Motherboard, motherboard_id)
        ram = await self.db.get(RAM, ram_id)
        gpu = await self.db.get(GPU, gpu_id)
        psu = await self.db.get(PSU, psu_id)
        case = await self.db.get(Case, case_id)
        cooler = await self.db.get(Cooler, cooler_id)

        # 각 호환성 규칙 검증
        issues.extend(await self._check_cpu_motherboard_socket(cpu, mb))
        issues.extend(await self._check_ram_motherboard_type(ram, mb))
        issues.extend(await self._check_ram_motherboard_capacity(ram, mb))
        issues.extend(await self._check_ram_cpu_speed(ram, cpu))
        issues.extend(await self._check_gpu_case_length(gpu, case))
        issues.extend(await self._check_gpu_case_width(gpu, case))
        issues.extend(await self._check_gpu_psu_power(gpu, psu))
        issues.extend(await self._check_total_power(cpu, gpu, psu))
        issues.extend(await self._check_cooler_cpu_socket(cooler, cpu))
        issues.extend(await self._check_cooler_cpu_tdp(cooler, cpu))
        issues.extend(await self._check_cooler_case_height(cooler, case))
        issues.extend(await self._check_cooler_case_radiator(cooler, case))
        issues.extend(await self._check_ram_cooler_interference(ram, cooler))
        issues.extend(await self._check_motherboard_case_formfactor(mb, case))
        issues.extend(await self._check_psu_case_formfactor(psu, case))
        issues.extend(await self._check_psu_case_length(psu, case))

        # 스토리지 호환성
        for storage_id in storages:
            storage = await self.db.get(Storage, storage_id)
            issues.extend(await self._check_storage_motherboard(storage, mb))

        # 심각도 판별
        is_compatible = not any(i.severity == "error" for i in issues)

        return is_compatible, issues

    # 각 호환성 검증 메서드들...
```

---

## 17. 호환 불가 시 상세 오류 메시지 시스템

### 17.1 오류 메시지 구조

```python
# backend/app/schemas/compatibility_result.py

from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class IssueSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUGGESTION = "suggestion"

class CompatibilityIssue(BaseModel):
    issue_id: str
    severity: IssueSeverity
    category_a: str
    category_b: str
    component_a_name: str
    component_b_name: str
    title_ko: str
    message_ko: str
    technical_detail_ko: str
    solution_ko: str
    alternative_components: list
    icon: str
    documentation_url: Optional[str]
```

### 17.2 전체 오류 메시지 카탈로그

```python
COMPATIBILITY_MESSAGES = {
    "SOCKET_MISMATCH": {
        "severity": "error",
        "icon": "🔴",
        "title_ko": "CPU 소켓 불일치",
        "message_ko": "'{cpu_name}'은(는) {cpu_socket} 소켓을 사용하지만, "
                      "'{mb_name}' 메인보드는 {mb_socket} 소켓입니다. "
                      "물리적으로 장착이 불가능합니다.",
        "technical_detail_ko": "CPU 소켓과 메인보드 소켓은 반드시 동일해야 합니다. "
                               "{cpu_socket} CPU는 {compatible_chipsets} 칩셋 메인보드에만 장착 가능합니다.",
        "solution_ko": "다음 중 하나를 선택해주세요:\n"
                       "1. CPU를 {mb_socket} 소켓 제품으로 변경\n"
                       "2. 메인보드를 {cpu_socket} 소켓 제품으로 변경",
    },

    "DDR_MISMATCH": {
        "severity": "error",
        "icon": "🔴",
        "title_ko": "RAM 규격 불일치",
        "message_ko": "'{ram_name}'은(는) {ram_type}이지만, "
                      "'{mb_name}' 메인보드는 {mb_memory_type}만 지원합니다. "
                      "물리적으로 장착이 불가능합니다.",
        "technical_detail_ko": "DDR4와 DDR5는 핀 배열이 다르므로 호환되지 않습니다. "
                               "메인보드의 메모리 슬롯 유형에 맞는 RAM을 선택해야 합니다.",
        "solution_ko": "'{mb_name}'에 맞는 {mb_memory_type} RAM으로 변경해주세요.",
    },

    "GPU_TOO_LONG": {
        "severity": "error",
        "icon": "🔴",
        "title_ko": "GPU가 케이스에 들어가지 않음",
        "message_ko": "'{gpu_name}'의 길이는 {gpu_length}mm이지만, "
                      "'{case_name}' 케이스의 최대 GPU 수용 길이는 {case_max_gpu}mm입니다. "
                      "GPU가 {overflow}mm 초과하여 물리적으로 장착이 불가능합니다.",
        "technical_detail_ko": "대형 GPU(특히 RTX 4090급)는 길이가 300mm를 넘을 수 있어 "
                               "소형 케이스에 장착이 어렵습니다.",
        "solution_ko": "1. 더 큰 케이스(최소 {required_min_length}mm 이상)를 선택\n"
                       "2. 더 짧은 GPU(ITX 모델 등)를 선택",
    },

    "COOLER_TOO_TALL": {
        "severity": "error",
        "icon": "🔴",
        "title_ko": "CPU 쿨러가 케이스에 들어가지 않음",
        "message_ko": "'{cooler_name}'의 높이는 {cooler_height}mm이지만, "
                      "'{case_name}' 케이스의 최대 CPU 쿨러 높이는 {case_max_cooler}mm입니다.",
        "technical_detail_ko": "타워형 공랭 쿨러는 높이가 케이스 내부 공간을 초과하면 "
                               "사이드 패널이 닫히지 않거나 쿨러를 장착할 수 없습니다.",
        "solution_ko": "1. 더 낮은 쿨러(로우프로파일)로 변경\n"
                       "2. 수냉 쿨러(AIO)로 변경\n"
                       "3. 더 넓은 케이스로 변경",
    },

    "MB_CASE_FORMFACTOR": {
        "severity": "error",
        "icon": "🔴",
        "title_ko": "메인보드 폼팩터 불일치",
        "message_ko": "'{mb_name}'은(는) {mb_form_factor} 크기이지만, "
                      "'{case_name}' 케이스는 {case_supported_forms}만 지원합니다.",
        "technical_detail_ko": "E-ATX 메인보드는 풀타워 케이스에만, ATX는 미드타워 이상에 장착 가능합니다. "
                               "작은 케이스에 큰 메인보드를 넣을 수 없습니다.",
        "solution_ko": "{mb_form_factor}를 지원하는 케이스로 변경해주세요.",
    },

    "PSU_INSUFFICIENT_POWER": {
        "severity": "error",
        "icon": "🔴",
        "title_ko": "파워서플라이 용량 부족",
        "message_ko": "시스템 예상 소비전력은 약 {estimated_power}W이지만, "
                      "'{psu_name}'의 용량은 {psu_wattage}W입니다. "
                      "안정적 운영을 위해 최소 {recommended_psu}W 이상의 파워가 필요합니다.",
        "technical_detail_ko": "CPU({cpu_tdp}W) + GPU({gpu_tdp}W) + 기타 부품(~100W) = 약 {total_tdp}W. "
                               "안정성을 위해 20% 이상 여유가 필요합니다. "
                               "파워 부족 시 시스템이 갑자기 꺼지거나 부품이 손상될 수 있습니다.",
        "solution_ko": "{recommended_psu}W 이상의 파워서플라이로 변경해주세요.",
    },

    "PSU_NO_GPU_CONNECTOR": {
        "severity": "error",
        "icon": "🔴",
        "title_ko": "GPU 전원 커넥터 부족",
        "message_ko": "'{gpu_name}'은(는) {required_connectors}이(가) 필요하지만, "
                      "'{psu_name}'에는 해당 커넥터가 없습니다.",
        "technical_detail_ko": "최신 고급 GPU(RTX 4070 SUPER 이상)는 12VHPWR(12V-2x6) 커넥터가 필요합니다. "
                               "구형 파워에는 이 커넥터가 없을 수 있습니다.",
        "solution_ko": "12VHPWR 커넥터를 지원하는 최신 파워서플라이로 변경하거나, "
                       "변환 어댑터 사용을 고려해주세요(권장하지 않음).",
    },

    "COOLER_SOCKET_INCOMPATIBLE": {
        "severity": "error",
        "icon": "🔴",
        "title_ko": "쿨러 소켓 미지원",
        "message_ko": "'{cooler_name}'은(는) {cooler_sockets} 소켓을 지원하지만, "
                      "'{cpu_name}'은(는) {cpu_socket} 소켓입니다. 장착 브라켓이 호환되지 않습니다.",
        "solution_ko": "{cpu_socket} 소켓을 지원하는 쿨러로 변경해주세요. "
                       "일부 쿨러는 별도 마운팅 킷 구매로 해결 가능합니다.",
    },

    "RADIATOR_NO_FIT": {
        "severity": "error",
        "icon": "🔴",
        "title_ko": "라디에이터 장착 불가",
        "message_ko": "'{cooler_name}'의 {radiator_size} 라디에이터를 "
                      "'{case_name}' 케이스에 장착할 공간이 없습니다. "
                      "케이스 지원: 전면 최대 {case_front_rad}, 상단 최대 {case_top_rad}.",
        "solution_ko": "1. 더 작은 라디에이터의 수냉 쿨러로 변경\n"
                       "2. 라디에이터를 수용할 수 있는 더 큰 케이스로 변경",
    },

    "M2_SLOT_EXCEEDED": {
        "severity": "error",
        "icon": "🔴",
        "title_ko": "M.2 슬롯 부족",
        "message_ko": "선택한 NVMe SSD 수({nvme_count}개)가 "
                      "'{mb_name}' 메인보드의 M.2 슬롯 수({mb_m2_slots}개)를 초과합니다.",
        "solution_ko": "NVMe SSD 수를 줄이거나, M.2 슬롯이 더 많은 메인보드를 선택해주세요.",
    },

    "PSU_CASE_FORMFACTOR": {
        "severity": "error",
        "icon": "🔴",
        "title_ko": "파워 폼팩터 불일치",
        "message_ko": "'{psu_name}'은(는) {psu_form}이지만, "
                      "'{case_name}' 케이스는 {case_psu_forms}만 지원합니다.",
        "solution_ko": "{case_psu_forms} 규격의 파워서플라이로 변경해주세요.",
    },

    "RAM_SPEED_DOWNGRADE": {
        "severity": "warning",
        "icon": "🟡",
        "title_ko": "RAM 속도 다운클록",
        "message_ko": "'{ram_name}'은(는) {ram_speed}MHz이지만, "
                      "'{cpu_name}'의 메모리 컨트롤러는 최대 {cpu_max_speed}MHz를 지원합니다. "
                      "RAM이 {cpu_max_speed}MHz로 다운클록되어 작동합니다.",
        "technical_detail_ko": "더 비싼 고속 RAM을 구매해도 CPU가 지원하지 않는 속도는 활용되지 않습니다.",
        "solution_ko": "{cpu_max_speed}MHz 이하의 RAM으로 변경하면 비용을 절약할 수 있습니다.",
    },

    "COOLER_TDP_INSUFFICIENT": {
        "severity": "warning",
        "icon": "🟡",
        "title_ko": "쿨러 냉각 용량 부족 우려",
        "message_ko": "'{cooler_name}'의 냉각 용량({cooler_tdp}W)이 "
                      "'{cpu_name}'의 TDP({cpu_tdp}W)보다 낮습니다. "
                      "고부하 작업 시 CPU 쓰로틀링이 발생할 수 있습니다.",
        "solution_ko": "{cpu_tdp}W 이상을 지원하는 쿨러로 업그레이드를 권장합니다.",
    },

    "RAM_COOLER_CLEARANCE": {
        "severity": "warning",
        "icon": "🟡",
        "title_ko": "RAM과 CPU 쿨러 간섭 가능성",
        "message_ko": "'{cooler_name}'은(는) 대형 타워쿨러(높이 {cooler_height}mm)이고, "
                      "'{ram_name}'은(는) 높은 히트싱크({ram_height}mm)를 가지고 있어 "
                      "첫 번째 RAM 슬롯에서 간섭이 발생할 수 있습니다.",
        "solution_ko": "1. 로우프로파일 RAM(높이 32mm 이하)으로 변경\n"
                       "2. RAM을 2번째/4번째 슬롯에만 장착\n"
                       "3. 쿨러를 수냉으로 변경",
    },

    "OVERKILL_PSU": {
        "severity": "info",
        "icon": "🔵",
        "title_ko": "파워서플라이 과잉 스펙",
        "message_ko": "시스템 예상 소비전력 {estimated_power}W 대비 "
                      "'{psu_name}'({psu_wattage}W)은(는) 필요 이상으로 높습니다. "
                      "비용 절감을 위해 {recommended_psu}W급으로 충분합니다.",
        "solution_ko": "{recommended_psu}W 파워로 다운그레이드하면 ₩{savings:,} 절약 가능합니다.",
    },

    "BETTER_VALUE_EXISTS": {
        "severity": "suggestion",
        "icon": "💡",
        "title_ko": "더 나은 가성비 대안",
        "message_ko": "'{component_name}' 대신 '{alternative_name}'을(를) 선택하면 "
                      "비슷한 성능에 ₩{price_diff:,} 절약할 수 있습니다.",
    },

    "NEWER_MODEL_AVAILABLE": {
        "severity": "suggestion",
        "icon": "💡",
        "title_ko": "최신 모델 출시됨",
        "message_ko": "'{component_name}'의 후속 모델 '{newer_name}'이(가) "
                      "비슷한 가격대에 출시되었습니다. 성능이 약 {perf_diff}% 향상됩니다.",
    },
}
```

### 17.3 조합 불가 시 전체 견적 거부 응답

```json
{
    "success": false,
    "error_code": "INCOMPATIBLE_BUILD",
    "message_ko": "선택하신 부품 조합으로는 PC를 구성할 수 없습니다.",
    "critical_issues": [
        {
            "issue_id": "SOCKET_MISMATCH",
            "severity": "error",
            "title_ko": "CPU 소켓 불일치",
            "message_ko": "'Intel Core i9-14900K'은(는) LGA1700 소켓이지만, 'ASUS ROG STRIX B650-A'는 AM5 소켓입니다.",
            "solution_ko": "CPU를 AM5 소켓 제품(AMD Ryzen)으로 변경하거나, 메인보드를 LGA1700 소켓 제품으로 변경해주세요.",
            "alternative_components": [
                {"category": "cpu", "id": "cpu_r7_7800x3d", "name": "AMD Ryzen 7 7800X3D", "price_krw": 380000},
                {"category": "motherboard", "id": "mb_z790", "name": "ASUS TUF GAMING Z790-PLUS", "price_krw": 280000}
            ]
        }
    ],
    "auto_fix_available": true,
    "auto_fix_suggestions": [
        {
            "fix_id": "fix_change_cpu",
            "description_ko": "CPU를 AMD Ryzen 7 7800X3D로 변경 (다른 부품 유지)",
            "price_change_krw": -50000,
            "changes": [{"category": "cpu", "from": "cpu_i9_14900k", "to": "cpu_r7_7800x3d"}]
        },
        {
            "fix_id": "fix_change_mb",
            "description_ko": "메인보드를 ASUS TUF GAMING Z790-PLUS로 변경 (다른 부품 유지)",
            "price_change_krw": +20000,
            "changes": [{"category": "motherboard", "from": "mb_b650a", "to": "mb_z790_plus"}]
        }
    ]
}
```

---
