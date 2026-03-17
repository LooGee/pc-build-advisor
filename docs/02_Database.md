# PC Build Advisor - 데이터베이스 스키마

> 📁 **전체 문서 목차**: [INDEX.md](./INDEX.md)

## 5. 데이터베이스 스키마 (상세 설계)

### 5.1 Components 테이블 (기본 부품 정보)

```sql
CREATE TABLE components (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(50) NOT NULL,  -- cpu, gpu, ram, motherboard, storage, psu, case, cooler
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(200) NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    release_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(category, brand, model)
);

CREATE INDEX idx_components_category ON components(category);
CREATE INDEX idx_components_brand ON components(brand);
CREATE INDEX idx_components_active ON components(is_active);
```

### 5.2 CPUs 테이블

```sql
CREATE TABLE cpus (
    id UUID PRIMARY KEY REFERENCES components(id) ON DELETE CASCADE,
    socket VARCHAR(50) NOT NULL,  -- LGA1700, LGA1851, AM5, AM4
    cores INT NOT NULL,
    threads INT NOT NULL,
    base_clock_ghz DECIMAL(4,2) NOT NULL,  -- 3.00 GHz
    boost_clock_ghz DECIMAL(4,2) NOT NULL,
    tdp_w INT NOT NULL,  -- 65W, 125W, 253W
    integrated_graphics BOOLEAN DEFAULT FALSE,
    iGPU_model VARCHAR(100),
    cache_l3_mb INT,
    supported_memory_type VARCHAR(20),  -- DDR4, DDR5
    max_memory_speed_mhz INT,
    max_memory_capacity_gb INT,
    pcie_version VARCHAR(10),  -- 4.0, 5.0
    pcie_lanes INT,
    ecc_supported BOOLEAN DEFAULT FALSE,
    overclockable BOOLEAN DEFAULT FALSE,

    -- 성능 벤치마크 (Cinebench R23, Geekbench 등)
    cinebench_r23_multi_core INT,
    cinebench_r23_single_core INT,
    geekbench6_multi INT,
    geekbench6_single INT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cpus_socket ON cpus(socket);
CREATE INDEX idx_cpus_core_count ON cpus(cores, threads);
CREATE INDEX idx_cpus_benchmark ON cpus(cinebench_r23_multi_core);
```

### 5.3 GPUs 테이블

```sql
CREATE TABLE gpus (
    id UUID PRIMARY KEY REFERENCES components(id) ON DELETE CASCADE,
    chip_manufacturer VARCHAR(50) NOT NULL,  -- NVIDIA, AMD, Intel
    chip_model VARCHAR(100) NOT NULL,  -- RTX 4090, RX 7900 XTX
    architecture VARCHAR(100),  -- Ada, RDNA 3, Alchemist

    vram_size_gb INT NOT NULL,  -- 4, 6, 8, 12, 16, 24
    vram_type VARCHAR(20) NOT NULL,  -- GDDR6, GDDR6X, HBM2e
    vram_bandwidth_gbs INT,

    base_clock_mhz INT,
    boost_clock_mhz INT,
    tdp_w INT NOT NULL,

    -- 물리 크기 정보
    length_mm INT,
    width_slots INT,  -- 2.5, 3 등
    height_mm INT,

    -- 전원 연결
    required_power_connectors JSONB,  -- {"8pin": 2, "6pin": 1, "12vhpwr": true}
    recommended_psu_wattage INT,

    -- 출력 포트
    display_ports INT,
    hdmi_ports INT,
    usb_type_c INT,

    -- 기술 지원
    pcie_version VARCHAR(10),  -- 4.0, 5.0
    ray_tracing_supported BOOLEAN DEFAULT TRUE,
    dlss_supported BOOLEAN DEFAULT FALSE,
    dlss_version VARCHAR(10),  -- 3, 3.5
    fsr_supported BOOLEAN DEFAULT FALSE,
    fsr_version VARCHAR(10),  -- 2, 3

    -- 성능 벤치마크
    3dmark_timespy_score INT,
    3dmark_firestrike_score INT,
    geekbench6_gpu_score INT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_gpus_chip ON gpus(chip_manufacturer, chip_model);
CREATE INDEX idx_gpus_vram ON gpus(vram_size_gb);
CREATE INDEX idx_gpus_benchmark ON gpus(3dmark_timespy_score);
```

### 5.4 Motherboards 테이블

```sql
CREATE TABLE motherboards (
    id UUID PRIMARY KEY REFERENCES components(id) ON DELETE CASCADE,
    socket VARCHAR(50) NOT NULL,  -- LGA1700, AM5
    chipset VARCHAR(100) NOT NULL,  -- Z790, B760, X870
    form_factor VARCHAR(20) NOT NULL,  -- ATX, mATX, ITX, E-ATX

    -- 메모리
    memory_type VARCHAR(20) NOT NULL,  -- DDR4, DDR5
    memory_slots INT NOT NULL,  -- 2, 4
    max_memory_capacity_gb INT,  -- 192, 256
    max_memory_speed_mhz INT,  -- 6400
    supports_xmp BOOLEAN DEFAULT TRUE,
    supports_docp BOOLEAN DEFAULT TRUE,

    -- M.2 슬롯 (NVMe/SATA)
    m2_slots INT NOT NULL,  -- 슬롯 개수
    m2_slot_details JSONB,  -- [{"slot": 1, "interface": "PCIe 5.0", "supported": ["nvme"]}, ...]

    -- PCIe 슬롯
    pcie_x16_slots INT,  -- GPU 슬롯 개수
    pcie_x16_type JSONB,  -- [{"slot": 1, "gen": 5.0, "lanes": 16}, ...]
    pcie_x1_slots INT,
    pcie_x1_type VARCHAR(10),

    -- SATA
    sata_ports INT NOT NULL,

    -- USB 포트 (내부 헤더)
    usb_20_headers INT,
    usb_30_headers INT,
    usb_type_c_headers INT,
    usb_type_c_gen2_count INT,

    -- 기타 기능
    wifi BOOLEAN DEFAULT FALSE,
    wifi_standard VARCHAR(20),  -- WiFi 6E, WiFi 7
    bluetooth BOOLEAN DEFAULT FALSE,
    bluetooth_version VARCHAR(10),
    audio_codec VARCHAR(100),  -- ALC1220, ALC4082
    lan_ports INT DEFAULT 1,
    lan_speed VARCHAR(20),  -- 2.5G, 5G, 10G

    -- RGB 헤더
    rgb_headers INT DEFAULT 0,
    argb_headers INT DEFAULT 0,

    -- 물리 정보
    length_mm INT,
    width_mm INT,
    bios_chip VARCHAR(50),  -- SPI, LPC
    bios_capacity_mb INT,  -- 32, 64, 128

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_motherboards_socket ON motherboards(socket);
CREATE INDEX idx_motherboards_chipset ON motherboards(chipset);
CREATE INDEX idx_motherboards_form ON motherboards(form_factor);
```

### 5.5 RAMs 테이블

```sql
CREATE TABLE rams (
    id UUID PRIMARY KEY REFERENCES components(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,  -- DDR4, DDR5
    speed_mhz INT NOT NULL,  -- 3200, 6000
    capacity_per_stick_gb INT NOT NULL,  -- 8, 16, 32
    sticks_count INT NOT NULL,  -- 1, 2, 4
    total_capacity_gb INT NOT NULL,  -- 16, 32, 64, 128

    -- 타이밍 정보
    cas_latency INT NOT NULL,  -- 16, 18, 20
    trcd_ns INT,
    trp_ns INT,
    tras_ns INT,

    -- 전압
    voltage_v DECIMAL(4,2),  -- 1.35V, 1.50V

    -- 물리 정보
    height_mm INT,  -- 32, 40 (큰 히트싱크)
    width_mm INT,

    -- 특수 기능
    has_rgb BOOLEAN DEFAULT FALSE,
    rgb_type VARCHAR(50),  -- ARGB, RGB
    has_heatsink BOOLEAN DEFAULT TRUE,

    -- XMP/DOCP
    xmp_profiles JSONB,  -- [{"name": "XMP Profile 1", "speed": 6000, "cas": 30}, ...]
    docp_profiles JSONB,

    -- 호환성
    ecc_supported BOOLEAN DEFAULT FALSE,
    unbuffered BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_rams_type_speed ON rams(type, speed_mhz);
CREATE INDEX idx_rams_capacity ON rams(total_capacity_gb);
```

### 5.6 Storages 테이블

```sql
CREATE TABLE storages (
    id UUID PRIMARY KEY REFERENCES components(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,  -- NVMe, SATA_SSD, HDD
    form_factor VARCHAR(50) NOT NULL,  -- M.2_2280, 2.5inch, 3.5inch
    interface VARCHAR(50) NOT NULL,  -- PCIe_Gen3, PCIe_Gen4, PCIe_Gen5, SATA

    -- 용량 및 성능
    capacity_gb INT NOT NULL,  -- 256, 512, 1000, 2000
    read_speed_mbs INT,  -- 순차 읽기 속도
    write_speed_mbs INT,
    random_read_iops INT,
    random_write_iops INT,

    -- 내구성
    endurance_tbw INT,  -- Total Bytes Written
    mtbf_hours INT,  -- Mean Time Between Failures
    warranty_years INT,

    -- 기술
    has_dram_cache BOOLEAN DEFAULT TRUE,
    cache_size_mb INT,
    nand_type VARCHAR(50),  -- TLC, QLC, SLC, PLC

    -- 물리 정보
    length_mm INT,
    width_mm INT,
    height_mm INT,
    weight_grams INT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_storages_type ON storages(type);
CREATE INDEX idx_storages_interface ON storages(interface);
CREATE INDEX idx_storages_capacity ON storages(capacity_gb);
```

### 5.7 PSUs 테이블

```sql
CREATE TABLE psus (
    id UUID PRIMARY KEY REFERENCES components(id) ON DELETE CASCADE,
    wattage W INT NOT NULL,  -- 550, 650, 750, 850, 1000, 1200
    efficiency_rating VARCHAR(50) NOT NULL,  -- 80+ Bronze, Silver, Gold, Platinum, Titanium

    -- 형태
    modular_type VARCHAR(50) NOT NULL,  -- full, semi, non
    form_factor VARCHAR(50) NOT NULL,  -- ATX, SFX, SFX-L

    -- 물리 정보
    length_mm INT,
    width_mm INT,
    height_mm INT,
    weight_kg DECIMAL(5,2),

    -- 냉각
    fan_size_mm INT,  -- 80, 120, 135
    fan_type VARCHAR(50),  -- FDB, Ball Bearing
    has_zero_rpm_mode BOOLEAN DEFAULT FALSE,

    -- 커넥터 (수량)
    connector_24pin INT DEFAULT 1,
    connector_8pin_cpu INT,  -- 4pin+4pin
    connector_6pin_pcie INT,
    connector_8pin_pcie INT,  -- 6pin+2pin
    connector_12vhpwr BOOLEAN DEFAULT FALSE,  -- 12V-2x6 or 12V-2x8
    connector_sata INT,
    connector_perif INT,

    -- 기술
    ocp_protection BOOLEAN DEFAULT TRUE,  -- Over Current Protection
    scp_protection BOOLEAN DEFAULT TRUE,  -- Short Circuit Protection
    opp_protection BOOLEAN DEFAULT TRUE,  -- Over Power Protection

    -- 인증
    pfc_active BOOLEAN DEFAULT FALSE,  -- Active Power Factor Correction

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_psus_wattage ON psus(wattage);
CREATE INDEX idx_psus_efficiency ON psus(efficiency_rating);
```

### 5.8 Cases 테이블

```sql
CREATE TABLE cases (
    id UUID PRIMARY KEY REFERENCES components(id) ON DELETE CASCADE,

    -- 폼팩터 지원
    supported_form_factors VARCHAR[],  -- ['ATX', 'mATX', 'ITX']

    -- GPU 호환성
    max_gpu_length_mm INT,
    max_gpu_width_slots INT,

    -- 쿨러 호환성
    max_cpu_cooler_height_mm INT,  -- 타워 쿨러
    max_front_radiator_size VARCHAR,  -- 120mm, 240mm, 360mm
    max_top_radiator_size VARCHAR,
    max_rear_radiator_size VARCHAR,

    -- PSU 호환성
    max_psu_length_mm INT,
    supported_psu_form_factors VARCHAR[],  -- ['ATX', 'SFX', 'SFX-L']

    -- 스토리지 베이
    drive_bays_35 INT,  -- 3.5인치 베이
    drive_bays_25 INT,  -- 2.5인치 베이
    m2_slots INT,  -- M.2 고정점

    -- 팬 지원
    front_fan_slots INT,
    top_fan_slots INT,
    rear_fan_slots INT,
    bottom_fan_slots INT,
    max_fan_size_mm INT,  -- 최대 지원 팬 크기

    -- RGB/조명
    has_tempered_glass BOOLEAN DEFAULT FALSE,
    has_front_panel_rgb BOOLEAN DEFAULT FALSE,
    led_controller_included BOOLEAN DEFAULT FALSE,

    -- 포트 (전면)
    front_usb_20_ports INT DEFAULT 0,
    front_usb_30_ports INT DEFAULT 0,
    front_usb_type_c INT DEFAULT 0,
    front_audio_jack BOOLEAN DEFAULT TRUE,

    -- 물리 정보
    form_factor_case VARCHAR(50),  -- Full Tower, Mid Tower, Mini Tower, SFF
    length_mm INT,
    width_mm INT,
    height_mm INT,
    weight_kg DECIMAL(5,2),

    -- 자재 및 색상
    material VARCHAR(100),  -- Steel, Aluminum
    color VARCHAR(100),  -- Black, White, Custom

    -- 에어플로우
    airflow_design VARCHAR(100),  -- Front-to-Rear, Top-to-Bottom
    dust_filters BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cases_formfactor ON cases(supported_form_factors);
CREATE INDEX idx_cases_gpu_length ON cases(max_gpu_length_mm);
```

### 5.9 Coolers 테이블

```sql
CREATE TABLE coolers (
    id UUID PRIMARY KEY REFERENCES components(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,  -- air, aio_liquid_120, aio_liquid_240, aio_liquid_280, aio_liquid_360, custom_loop

    -- 소켓 호환성
    supported_sockets VARCHAR[],  -- ['LGA1700', 'AM5', 'LGA1851']

    -- Air Cooler 사양
    is_air_cooler BOOLEAN DEFAULT FALSE,
    height_mm INT,  -- 타워 높이
    mounting_type VARCHAR(100),

    -- Liquid Cooler 사양
    is_liquid_cooler BOOLEAN DEFAULT FALSE,
    radiator_size VARCHAR(50),  -- 120mm, 240mm, 280mm, 360mm
    fan_count INT,  -- 라디에이터에 달린 팬 수
    fan_size_mm INT,  -- 일반적으로 120mm
    radiator_thickness_mm INT,  -- 16, 27, 30 (두꺼운 라디에이터)
    block_material VARCHAR(100),  -- Copper, Nickel, Aluminum
    has_rgb BOOLEAN DEFAULT FALSE,
    rgb_type VARCHAR(50),  -- ARGB, RGB

    -- 성능
    tdp_rating_w INT NOT NULL,  -- 보냉 용량
    noise_level_dba INT,  -- 데시벨
    max_rpm INT,

    -- 물리 정보
    weight_kg DECIMAL(5,2),
    mounting_bracket_included BOOLEAN DEFAULT TRUE,

    -- 호환성
    requires_thermal_paste BOOLEAN DEFAULT TRUE,
    thermal_paste_included BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_coolers_type ON coolers(type);
CREATE INDEX idx_coolers_tdp ON coolers(tdp_rating_w);
```

### 5.10 Game Requirements 테이블

```sql
CREATE TABLE game_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_name VARCHAR(200) NOT NULL UNIQUE,
    genre VARCHAR(100),

    -- Minimum (Low Settings, 1080p, 30fps)
    min_cpu_benchmark_single INT,
    min_cpu_benchmark_multi INT,
    min_gpu_benchmark INT,
    min_ram_gb INT,
    min_storage_gb INT,
    min_resolution VARCHAR(20),  -- 720p, 1080p
    min_fps INT,

    -- Recommended (High Settings, 1080p, 60fps)
    rec_cpu_benchmark_single INT,
    rec_cpu_benchmark_multi INT,
    rec_gpu_benchmark INT,
    rec_ram_gb INT,
    rec_storage_gb INT,
    rec_resolution VARCHAR(20),  -- 1080p, 1440p
    rec_fps INT,

    -- Ultra/High Settings (1440p-4K, 144fps+)
    ultra_cpu_benchmark_single INT,
    ultra_cpu_benchmark_multi INT,
    ultra_gpu_benchmark INT,
    ultra_ram_gb INT,
    ultra_storage_gb INT,
    ultra_resolution VARCHAR(20),  -- 1440p, 4K
    ultra_fps INT,

    -- 특수 기술
    supports_ray_tracing BOOLEAN DEFAULT FALSE,
    supports_dlss BOOLEAN DEFAULT FALSE,
    supports_fsr BOOLEAN DEFAULT FALSE,
    requires_gpu_acceleration BOOLEAN DEFAULT TRUE,

    release_year INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_game_requirements_name ON game_requirements(game_name);
```

### 5.11 Software Requirements 테이블

```sql
CREATE TABLE software_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    software_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,  -- video_editing, 3d_rendering, data_science, programming, design
    vendor VARCHAR(100),

    -- Minimum
    min_cpu_benchmark_single INT,
    min_cpu_benchmark_multi INT,
    min_gpu_benchmark INT,
    min_ram_gb INT,
    min_storage_gb INT,

    -- Recommended
    rec_cpu_benchmark_single INT,
    rec_cpu_benchmark_multi INT,
    rec_gpu_benchmark INT,
    rec_ram_gb INT,
    rec_storage_gb INT,

    -- Professional/Workstation
    professional_cpu_benchmark_multi INT,
    professional_gpu_benchmark INT,
    professional_ram_gb INT,
    professional_storage_gb INT,

    -- GPU 가속
    needs_gpu_acceleration BOOLEAN DEFAULT FALSE,
    preferred_gpu_vendor VARCHAR(50),  -- NVIDIA, AMD, Intel, Any
    cuda_supported BOOLEAN DEFAULT FALSE,
    opencl_supported BOOLEAN DEFAULT FALSE,
    hip_supported BOOLEAN DEFAULT FALSE,

    release_year INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_software_requirements_category ON software_requirements(category);
```

### 5.12 Prices 테이블

```sql
CREATE TABLE prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_id UUID NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    source VARCHAR(100) NOT NULL,  -- danawa, compuzone, coupang, pcpartpicker
    price_krw INT NOT NULL,
    price_usd DECIMAL(10,2),

    -- 배송료 및 상태
    shipping_cost_krw INT DEFAULT 0,
    total_price_krw INT GENERATED ALWAYS AS (price_krw + shipping_cost_krw) STORED,
    in_stock BOOLEAN DEFAULT TRUE,
    stock_quantity INT,

    -- 링크 및 메타정보
    product_url VARCHAR(1000),
    product_name VARCHAR(500),
    seller_name VARCHAR(200),

    -- 할인 정보
    has_discount BOOLEAN DEFAULT FALSE,
    discount_rate_percent INT,
    original_price_krw INT,

    -- 배송 정보
    free_shipping BOOLEAN DEFAULT FALSE,
    rocket_delivery BOOLEAN DEFAULT FALSE,  -- Coupang Rocket Delivery

    -- 가격 이력 참조
    last_checked TIMESTAMP DEFAULT NOW(),
    price_trend VARCHAR(20),  -- up, down, stable
    days_since_change INT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_prices_component ON prices(component_id);
CREATE INDEX idx_prices_source ON prices(source);
CREATE INDEX idx_prices_total ON prices(total_price_krw);
CREATE INDEX idx_prices_stock ON prices(in_stock);
CREATE UNIQUE INDEX idx_prices_unique ON prices(component_id, source);
```

### 5.13 Price History 테이블

```sql
CREATE TABLE price_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_id UUID NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    source VARCHAR(100) NOT NULL,
    price_krw INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_price_history_component ON price_history(component_id, source);
CREATE INDEX idx_price_history_recorded ON price_history(recorded_at);
```

### 5.14 Compatibility Rules 테이블

```sql
CREATE TABLE compatibility_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(200) NOT NULL,
    rule_type VARCHAR(100) NOT NULL,  -- socket, memory_type, power, physical_fit
    category_a VARCHAR(50),  -- cpu, gpu, motherboard 등
    category_b VARCHAR(50),

    -- 검증 로직 (JSON)
    validation_logic JSONB NOT NULL,  -- 규칙 상세 정의
    error_message_ko TEXT,
    warning_message_ko TEXT,
    severity VARCHAR(20),  -- error, warning

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 예시 validation_logic:
-- {"type": "socket_match", "field_a": "socket", "field_b": "socket", "mapping": {"LGA1700": "LGA1700", "AM5": "AM5"}}
```

### 5.15 Quotes 테이블

```sql
CREATE TABLE quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(500),  -- 익명 세션 ID

    -- 요구사항
    user_input_text TEXT NOT NULL,
    analyzed_requirements JSONB,  -- {primary_use, specific_software, performance_tier, budget, preferences, priority}

    -- 3가지 견적
    tier VARCHAR(20),  -- minimum, balanced, maximum
    build_name VARCHAR(200),

    -- 부품 구성 (부품 ID 배열)
    cpu_id UUID REFERENCES cpus(id),
    gpu_id UUID REFERENCES gpus(id),
    motherboard_id UUID REFERENCES motherboards(id),
    ram_id UUID REFERENCES rams(id),
    storage_ids UUID[],
    psu_id UUID REFERENCES psus(id),
    case_id UUID REFERENCES cases(id),
    cooler_id UUID REFERENCES coolers(id),

    -- 가격 정보
    total_price_krw INT,
    components_price_krw INT,
    shipping_cost_krw INT,

    -- 호환성 결과
    is_compatible BOOLEAN DEFAULT TRUE,
    compatibility_issues JSONB,  -- [{issue_type, severity, message}]

    -- 성능 예측
    estimated_cpu_benchmark INT,
    estimated_gpu_benchmark INT,
    estimated_gaming_fps_1080p INT,
    estimated_gaming_fps_1440p INT,
    estimated_power_consumption_w INT,

    -- 메타정보
    llm_model VARCHAR(100),  -- claude-3-5-sonnet, gpt-4o
    llm_version VARCHAR(50),
    generation_time_ms INT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP  -- 견적 유효기간
);

CREATE INDEX idx_quotes_user ON quotes(user_id);
CREATE INDEX idx_quotes_tier ON quotes(tier);
CREATE INDEX idx_quotes_created ON quotes(created_at);
```

### 5.16 Quote Components 테이블 (정규화)

```sql
CREATE TABLE quote_components (
    quote_id UUID NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
    component_id UUID NOT NULL REFERENCES components(id),
    category VARCHAR(50) NOT NULL,
    unit_price_krw INT NOT NULL,
    quantity INT DEFAULT 1,
    price_source VARCHAR(100),  -- 어느 사이트에서 가져온 가격인지
    product_url VARCHAR(1000),
    compatibility_status VARCHAR(20),  -- ok, warning, error
    compatibility_notes TEXT,

    PRIMARY KEY (quote_id, component_id)
);
```

---
