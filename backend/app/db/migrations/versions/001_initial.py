"""Initial migration: create all tables

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # 1. components  (no foreign-key dependencies)                        #
    # ------------------------------------------------------------------ #
    op.create_table(
        'components',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column('category',     sa.String(50),  nullable=False),
        sa.Column('brand',        sa.String(100), nullable=False),
        sa.Column('model',        sa.String(200), nullable=False),
        sa.Column('description',  sa.Text(),      nullable=True),
        sa.Column('image_url',    sa.String(500), nullable=True),
        sa.Column('release_date', sa.Date(),      nullable=True),
        sa.Column(
            'is_active',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )
    op.create_index('idx_components_category', 'components', ['category'])
    op.create_index('idx_components_brand',    'components', ['brand'])
    op.create_index('idx_components_is_active','components', ['is_active'])

    # ------------------------------------------------------------------ #
    # 2. cpus                                                             #
    # ------------------------------------------------------------------ #
    op.create_table(
        'cpus',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('components.id', ondelete='CASCADE'),
            primary_key=True,
            nullable=False,
        ),
        sa.Column('socket',                  sa.String(50),  nullable=False),
        sa.Column('cores',                   sa.Integer(),   nullable=False),
        sa.Column('threads',                 sa.Integer(),   nullable=False),
        sa.Column('base_clock_ghz',          sa.Numeric(4, 2), nullable=False),
        sa.Column('boost_clock_ghz',         sa.Numeric(4, 2), nullable=False),
        sa.Column('tdp_w',                   sa.Integer(),   nullable=False),
        sa.Column(
            'integrated_graphics',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('igpu_model',              sa.String(100), nullable=True),
        sa.Column('cache_l3_mb',             sa.Integer(),   nullable=True),
        sa.Column('supported_memory_type',   sa.String(20),  nullable=True),
        sa.Column('max_memory_speed_mhz',    sa.Integer(),   nullable=True),
        sa.Column('max_memory_capacity_gb',  sa.Integer(),   nullable=True),
        sa.Column('pcie_version',            sa.String(10),  nullable=True),
        sa.Column('pcie_lanes',              sa.Integer(),   nullable=True),
        sa.Column(
            'ecc_supported',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column(
            'overclockable',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('cinebench_r23_multi_core', sa.Integer(), nullable=True),
        sa.Column('cinebench_r23_single_core',sa.Integer(), nullable=True),
        sa.Column('geekbench6_multi',          sa.Integer(), nullable=True),
        sa.Column('geekbench6_single',         sa.Integer(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )
    op.create_index('idx_cpus_socket',    'cpus', ['socket'])
    op.create_index('idx_cpus_benchmark', 'cpus', ['cinebench_r23_multi_core'])

    # ------------------------------------------------------------------ #
    # 3. gpus                                                             #
    # ------------------------------------------------------------------ #
    op.create_table(
        'gpus',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('components.id', ondelete='CASCADE'),
            primary_key=True,
            nullable=False,
        ),
        sa.Column('chip_manufacturer',       sa.String(50),  nullable=False),
        sa.Column('chip_model',              sa.String(100), nullable=False),
        sa.Column('architecture',            sa.String(100), nullable=True),
        sa.Column('vram_size_gb',            sa.Integer(),   nullable=False),
        sa.Column('vram_type',               sa.String(20),  nullable=False),
        sa.Column('vram_bandwidth_gbs',      sa.Integer(),   nullable=True),
        sa.Column('base_clock_mhz',          sa.Integer(),   nullable=True),
        sa.Column('boost_clock_mhz',         sa.Integer(),   nullable=True),
        sa.Column('tdp_w',                   sa.Integer(),   nullable=False),
        sa.Column('length_mm',               sa.Integer(),   nullable=True),
        sa.Column('width_slots',             sa.Integer(),   nullable=True),
        sa.Column('height_mm',               sa.Integer(),   nullable=True),
        sa.Column(
            'required_power_connectors',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column('recommended_psu_wattage', sa.Integer(),  nullable=True),
        sa.Column('display_ports',           sa.Integer(),  nullable=True),
        sa.Column('hdmi_ports',              sa.Integer(),  nullable=True),
        sa.Column('usb_type_c',              sa.Integer(),  nullable=True),
        sa.Column('pcie_version',            sa.String(10), nullable=True),
        sa.Column(
            'ray_tracing_supported',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'dlss_supported',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('dlss_version', sa.String(10), nullable=True),
        sa.Column(
            'fsr_supported',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('fsr_version',              sa.String(10), nullable=True),
        sa.Column('tdmark_timespy_score',     sa.Integer(),  nullable=True),
        sa.Column('tdmark_firestrike_score',  sa.Integer(),  nullable=True),
        sa.Column('geekbench6_gpu_score',     sa.Integer(),  nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )
    op.create_index('idx_gpus_chip_manufacturer', 'gpus', ['chip_manufacturer'])
    op.create_index('idx_gpus_vram_size_gb',      'gpus', ['vram_size_gb'])
    op.create_index('idx_gpus_timespy',           'gpus', ['tdmark_timespy_score'])

    # ------------------------------------------------------------------ #
    # 4. motherboards                                                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        'motherboards',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('components.id', ondelete='CASCADE'),
            primary_key=True,
            nullable=False,
        ),
        sa.Column('socket',                 sa.String(50),  nullable=False),
        sa.Column('chipset',                sa.String(100), nullable=False),
        sa.Column('form_factor',            sa.String(20),  nullable=False),
        sa.Column('memory_type',            sa.String(20),  nullable=False),
        sa.Column('memory_slots',           sa.Integer(),   nullable=False),
        sa.Column('max_memory_capacity_gb', sa.Integer(),   nullable=True),
        sa.Column('max_memory_speed_mhz',   sa.Integer(),   nullable=True),
        sa.Column(
            'supports_xmp',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'supports_docp',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column('m2_slots',    sa.Integer(), nullable=False),
        sa.Column(
            'm2_slot_details',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column('pcie_x16_slots', sa.Integer(), nullable=True),
        sa.Column(
            'pcie_x16_type',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column('pcie_x1_slots',      sa.Integer(),  nullable=True),
        sa.Column('sata_ports',         sa.Integer(),  nullable=False),
        sa.Column('usb_20_headers',     sa.Integer(),  nullable=True),
        sa.Column('usb_30_headers',     sa.Integer(),  nullable=True),
        sa.Column('usb_type_c_headers', sa.Integer(),  nullable=True),
        sa.Column(
            'wifi',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('wifi_standard', sa.String(20), nullable=True),
        sa.Column(
            'bluetooth',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('bluetooth_version', sa.String(10),  nullable=True),
        sa.Column('audio_codec',        sa.String(100), nullable=True),
        sa.Column(
            'lan_ports',
            sa.Integer(),
            nullable=False,
            server_default=sa.text('1'),
        ),
        sa.Column('lan_speed',    sa.String(20), nullable=True),
        sa.Column(
            'rgb_headers',
            sa.Integer(),
            nullable=False,
            server_default=sa.text('0'),
        ),
        sa.Column(
            'argb_headers',
            sa.Integer(),
            nullable=False,
            server_default=sa.text('0'),
        ),
        sa.Column('length_mm', sa.Integer(), nullable=True),
        sa.Column('width_mm',  sa.Integer(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )
    op.create_index('idx_motherboards_socket',      'motherboards', ['socket'])
    op.create_index('idx_motherboards_chipset',     'motherboards', ['chipset'])
    op.create_index('idx_motherboards_form_factor', 'motherboards', ['form_factor'])

    # ------------------------------------------------------------------ #
    # 5. rams                                                             #
    # ------------------------------------------------------------------ #
    op.create_table(
        'rams',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('components.id', ondelete='CASCADE'),
            primary_key=True,
            nullable=False,
        ),
        sa.Column('type',                  sa.String(20),    nullable=False),
        sa.Column('speed_mhz',             sa.Integer(),     nullable=False),
        sa.Column('capacity_per_stick_gb', sa.Integer(),     nullable=False),
        sa.Column('sticks_count',          sa.Integer(),     nullable=False),
        sa.Column('total_capacity_gb',     sa.Integer(),     nullable=False),
        sa.Column('cas_latency',           sa.Integer(),     nullable=False),
        sa.Column('trcd_ns',               sa.Integer(),     nullable=True),
        sa.Column('trp_ns',                sa.Integer(),     nullable=True),
        sa.Column('tras_ns',               sa.Integer(),     nullable=True),
        sa.Column('voltage_v',             sa.Numeric(4, 2), nullable=True),
        sa.Column('height_mm',             sa.Integer(),     nullable=True),
        sa.Column('width_mm',              sa.Integer(),     nullable=True),
        sa.Column(
            'has_rgb',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('rgb_type', sa.String(50), nullable=True),
        sa.Column(
            'has_heatsink',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'xmp_profiles',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            'docp_profiles',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            'ecc_supported',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column(
            'unbuffered',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )
    op.create_index('idx_rams_type',             'rams', ['type'])
    op.create_index('idx_rams_total_capacity_gb','rams', ['total_capacity_gb'])

    # ------------------------------------------------------------------ #
    # 6. storages                                                         #
    # ------------------------------------------------------------------ #
    op.create_table(
        'storages',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('components.id', ondelete='CASCADE'),
            primary_key=True,
            nullable=False,
        ),
        sa.Column('type',               sa.String(50), nullable=False),
        sa.Column('form_factor',        sa.String(50), nullable=False),
        sa.Column('interface',          sa.String(50), nullable=False),
        sa.Column('capacity_gb',        sa.Integer(),  nullable=False),
        sa.Column('read_speed_mbs',     sa.Integer(),  nullable=True),
        sa.Column('write_speed_mbs',    sa.Integer(),  nullable=True),
        sa.Column('random_read_iops',   sa.Integer(),  nullable=True),
        sa.Column('random_write_iops',  sa.Integer(),  nullable=True),
        sa.Column('endurance_tbw',      sa.Integer(),  nullable=True),
        sa.Column('mtbf_hours',         sa.Integer(),  nullable=True),
        sa.Column('warranty_years',     sa.Integer(),  nullable=True),
        sa.Column(
            'has_dram_cache',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column('cache_size_mb', sa.Integer(),  nullable=True),
        sa.Column('nand_type',     sa.String(50), nullable=True),
        sa.Column('length_mm',     sa.Integer(),  nullable=True),
        sa.Column('width_mm',      sa.Integer(),  nullable=True),
        sa.Column('height_mm',     sa.Integer(),  nullable=True),
        sa.Column('weight_grams',  sa.Integer(),  nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )
    op.create_index('idx_storages_type',        'storages', ['type'])
    op.create_index('idx_storages_interface',   'storages', ['interface'])
    op.create_index('idx_storages_capacity_gb', 'storages', ['capacity_gb'])

    # ------------------------------------------------------------------ #
    # 7. psus                                                             #
    # ------------------------------------------------------------------ #
    op.create_table(
        'psus',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('components.id', ondelete='CASCADE'),
            primary_key=True,
            nullable=False,
        ),
        sa.Column('wattage',           sa.Integer(),     nullable=False),
        sa.Column('efficiency_rating', sa.String(50),    nullable=False),
        sa.Column('modular_type',      sa.String(50),    nullable=False),
        sa.Column('form_factor',       sa.String(50),    nullable=False),
        sa.Column('length_mm',         sa.Integer(),     nullable=True),
        sa.Column('width_mm',          sa.Integer(),     nullable=True),
        sa.Column('height_mm',         sa.Integer(),     nullable=True),
        sa.Column('weight_kg',         sa.Numeric(5, 2), nullable=True),
        sa.Column('fan_size_mm',       sa.Integer(),     nullable=True),
        sa.Column('fan_type',          sa.String(50),    nullable=True),
        sa.Column(
            'has_zero_rpm_mode',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column(
            'connector_24pin',
            sa.Integer(),
            nullable=False,
            server_default=sa.text('1'),
        ),
        sa.Column('connector_8pin_cpu',  sa.Integer(), nullable=True),
        sa.Column('connector_6pin_pcie', sa.Integer(), nullable=True),
        sa.Column('connector_8pin_pcie', sa.Integer(), nullable=True),
        sa.Column(
            'connector_12vhpwr',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('connector_sata',  sa.Integer(), nullable=True),
        sa.Column('connector_perif', sa.Integer(), nullable=True),
        sa.Column(
            'ocp_protection',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'scp_protection',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'opp_protection',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'pfc_active',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )
    op.create_index('idx_psus_wattage',           'psus', ['wattage'])
    op.create_index('idx_psus_efficiency_rating', 'psus', ['efficiency_rating'])

    # ------------------------------------------------------------------ #
    # 8. cases                                                            #
    # ------------------------------------------------------------------ #
    op.create_table(
        'cases',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('components.id', ondelete='CASCADE'),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            'supported_form_factors',
            postgresql.ARRAY(sa.String()),
            nullable=True,
        ),
        sa.Column('max_gpu_length_mm',        sa.Integer(), nullable=True),
        sa.Column('max_gpu_width_slots',       sa.Integer(), nullable=True),
        sa.Column('max_cpu_cooler_height_mm',  sa.Integer(), nullable=True),
        sa.Column('max_front_radiator_size',   sa.String(50), nullable=True),
        sa.Column('max_top_radiator_size',     sa.String(50), nullable=True),
        sa.Column('max_rear_radiator_size',    sa.String(50), nullable=True),
        sa.Column('max_psu_length_mm',         sa.Integer(), nullable=True),
        sa.Column(
            'supported_psu_form_factors',
            postgresql.ARRAY(sa.String()),
            nullable=True,
        ),
        sa.Column('drive_bays_35',   sa.Integer(), nullable=True),
        sa.Column('drive_bays_25',   sa.Integer(), nullable=True),
        sa.Column('m2_slots',        sa.Integer(), nullable=True),
        sa.Column('front_fan_slots', sa.Integer(), nullable=True),
        sa.Column('top_fan_slots',   sa.Integer(), nullable=True),
        sa.Column('rear_fan_slots',  sa.Integer(), nullable=True),
        sa.Column('bottom_fan_slots',sa.Integer(), nullable=True),
        sa.Column('max_fan_size_mm', sa.Integer(), nullable=True),
        sa.Column(
            'has_tempered_glass',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column(
            'has_front_panel_rgb',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column(
            'front_usb_20_ports',
            sa.Integer(),
            nullable=False,
            server_default=sa.text('0'),
        ),
        sa.Column(
            'front_usb_30_ports',
            sa.Integer(),
            nullable=False,
            server_default=sa.text('0'),
        ),
        sa.Column(
            'front_usb_type_c',
            sa.Integer(),
            nullable=False,
            server_default=sa.text('0'),
        ),
        sa.Column(
            'front_audio_jack',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column('form_factor_case', sa.String(50),    nullable=True),
        sa.Column('length_mm',         sa.Integer(),     nullable=True),
        sa.Column('width_mm',          sa.Integer(),     nullable=True),
        sa.Column('height_mm',         sa.Integer(),     nullable=True),
        sa.Column('weight_kg',         sa.Numeric(5, 2), nullable=True),
        sa.Column('material',          sa.String(100),   nullable=True),
        sa.Column('color',             sa.String(100),   nullable=True),
        sa.Column('airflow_design',    sa.String(100),   nullable=True),
        sa.Column(
            'dust_filters',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )

    # ------------------------------------------------------------------ #
    # 9. coolers                                                          #
    # ------------------------------------------------------------------ #
    op.create_table(
        'coolers',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('components.id', ondelete='CASCADE'),
            primary_key=True,
            nullable=False,
        ),
        sa.Column('type',              sa.String(50),    nullable=False),
        sa.Column(
            'supported_sockets',
            postgresql.ARRAY(sa.String()),
            nullable=True,
        ),
        sa.Column(
            'is_air_cooler',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('height_mm',      sa.Integer(),   nullable=True),
        sa.Column('mounting_type',  sa.String(100), nullable=True),
        sa.Column(
            'is_liquid_cooler',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('radiator_size',          sa.String(50),    nullable=True),
        sa.Column('fan_count',              sa.Integer(),     nullable=True),
        sa.Column('fan_size_mm',            sa.Integer(),     nullable=True),
        sa.Column('radiator_thickness_mm',  sa.Integer(),     nullable=True),
        sa.Column('block_material',         sa.String(100),   nullable=True),
        sa.Column(
            'has_rgb',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('rgb_type',     sa.String(50),    nullable=True),
        sa.Column('tdp_rating_w', sa.Integer(),     nullable=False),
        sa.Column('noise_level_dba', sa.Integer(),  nullable=True),
        sa.Column('max_rpm',         sa.Integer(),  nullable=True),
        sa.Column('weight_kg',       sa.Numeric(5, 2), nullable=True),
        sa.Column(
            'mounting_bracket_included',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'requires_thermal_paste',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'thermal_paste_included',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )
    op.create_index('idx_coolers_type',        'coolers', ['type'])
    op.create_index('idx_coolers_tdp_rating_w','coolers', ['tdp_rating_w'])

    # ------------------------------------------------------------------ #
    # 10. prices                                                          #
    # ------------------------------------------------------------------ #
    op.create_table(
        'prices',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column(
            'component_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('components.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('source',      sa.String(100), nullable=False),
        sa.Column('price_krw',   sa.Integer(),   nullable=False),
        sa.Column('price_usd',   sa.Numeric(10, 2), nullable=True),
        sa.Column(
            'shipping_cost_krw',
            sa.Integer(),
            nullable=False,
            server_default=sa.text('0'),
        ),
        sa.Column(
            'in_stock',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column('stock_quantity',       sa.Integer(),     nullable=True),
        sa.Column('product_url',          sa.String(1000),  nullable=True),
        sa.Column('product_name',         sa.String(500),   nullable=True),
        sa.Column('seller_name',          sa.String(200),   nullable=True),
        sa.Column(
            'has_discount',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('discount_rate_percent', sa.Integer(), nullable=True),
        sa.Column('original_price_krw',    sa.Integer(), nullable=True),
        sa.Column(
            'free_shipping',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column(
            'rocket_delivery',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('last_checked',    sa.DateTime(timezone=True), nullable=True),
        sa.Column('price_trend',     sa.String(20), nullable=True),
        sa.Column('days_since_change',sa.Integer(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )
    op.create_index('idx_prices_component_id', 'prices', ['component_id'])
    op.create_index('idx_prices_source',       'prices', ['source'])
    op.create_index('idx_prices_in_stock',     'prices', ['in_stock'])

    # ------------------------------------------------------------------ #
    # 11. price_history                                                   #
    # ------------------------------------------------------------------ #
    op.create_table(
        'price_history',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column(
            'component_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('components.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('source',      sa.String(100),             nullable=False),
        sa.Column('price_krw',   sa.Integer(),               nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        'idx_price_history_component_source',
        'price_history',
        ['component_id', 'source'],
    )
    op.create_index(
        'idx_price_history_recorded_at',
        'price_history',
        ['recorded_at'],
    )

    # ------------------------------------------------------------------ #
    # 12. compatibility_rules  (no FK dependencies)                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        'compatibility_rules',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column('rule_name',  sa.String(200), nullable=False),
        sa.Column('rule_type',  sa.String(100), nullable=False),
        sa.Column('category_a', sa.String(50),  nullable=True),
        sa.Column('category_b', sa.String(50),  nullable=True),
        sa.Column(
            'validation_logic',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column('error_message_ko',   sa.Text(),     nullable=True),
        sa.Column('warning_message_ko', sa.Text(),     nullable=True),
        sa.Column('severity',           sa.String(20), nullable=True),
        sa.Column(
            'is_active',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )

    # ------------------------------------------------------------------ #
    # 13. quotes  (FK to cpus, gpus, motherboards, rams, psus,           #
    #              cases, coolers)                                        #
    # ------------------------------------------------------------------ #
    op.create_table(
        'quotes',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column('user_id',        sa.String(500), nullable=True),
        sa.Column('user_input_text',sa.Text(),      nullable=False),
        sa.Column(
            'analyzed_requirements',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column('tier',       sa.String(20),  nullable=True),
        sa.Column('build_name', sa.String(200), nullable=True),
        sa.Column(
            'cpu_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('cpus.id'),
            nullable=True,
        ),
        sa.Column(
            'gpu_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('gpus.id'),
            nullable=True,
        ),
        sa.Column(
            'motherboard_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('motherboards.id'),
            nullable=True,
        ),
        sa.Column(
            'ram_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('rams.id'),
            nullable=True,
        ),
        sa.Column(
            'storage_ids',
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=True,
        ),
        sa.Column(
            'psu_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('psus.id'),
            nullable=True,
        ),
        sa.Column(
            'case_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('cases.id'),
            nullable=True,
        ),
        sa.Column(
            'cooler_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('coolers.id'),
            nullable=True,
        ),
        sa.Column('total_price_krw',       sa.Integer(), nullable=True),
        sa.Column('components_price_krw',  sa.Integer(), nullable=True),
        sa.Column('shipping_cost_krw',     sa.Integer(), nullable=True),
        sa.Column(
            'is_compatible',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'compatibility_issues',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column('estimated_cpu_benchmark',      sa.Integer(), nullable=True),
        sa.Column('estimated_gpu_benchmark',      sa.Integer(), nullable=True),
        sa.Column('estimated_gaming_fps_1080p',   sa.Integer(), nullable=True),
        sa.Column('estimated_gaming_fps_1440p',   sa.Integer(), nullable=True),
        sa.Column('estimated_power_consumption_w',sa.Integer(), nullable=True),
        sa.Column('llm_model',           sa.String(100), nullable=True),
        sa.Column('llm_version',         sa.String(50),  nullable=True),
        sa.Column('generation_time_ms',  sa.Integer(),   nullable=True),
        sa.Column('expires_at',          sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )
    op.create_index('idx_quotes_user_id',   'quotes', ['user_id'])
    op.create_index('idx_quotes_tier',      'quotes', ['tier'])
    op.create_index('idx_quotes_created_at','quotes', ['created_at'])

    # ------------------------------------------------------------------ #
    # 14. quote_components  (FK to quotes and components)                 #
    # ------------------------------------------------------------------ #
    op.create_table(
        'quote_components',
        sa.Column(
            'quote_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('quotes.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'component_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('components.id'),
            nullable=False,
        ),
        sa.Column('category',      sa.String(50),   nullable=False),
        sa.Column('unit_price_krw',sa.Integer(),    nullable=False),
        sa.Column(
            'quantity',
            sa.Integer(),
            nullable=False,
            server_default=sa.text('1'),
        ),
        sa.Column('price_source',         sa.String(100),  nullable=True),
        sa.Column('product_url',          sa.String(1000), nullable=True),
        sa.Column('compatibility_status', sa.String(20),   nullable=True),
        sa.Column('compatibility_notes',  sa.Text(),       nullable=True),
        sa.PrimaryKeyConstraint('quote_id', 'component_id'),
    )

    # ------------------------------------------------------------------ #
    # 15. game_requirements  (no FK dependencies)                         #
    # ------------------------------------------------------------------ #
    op.create_table(
        'game_requirements',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column('game_name', sa.String(200), nullable=False, unique=True),
        sa.Column('aliases',   sa.String(500), nullable=True),
        sa.Column('genre',     sa.String(100), nullable=True),
        # Minimum requirements
        sa.Column('min_cpu_benchmark_single', sa.Integer(), nullable=True),
        sa.Column('min_cpu_benchmark_multi',  sa.Integer(), nullable=True),
        sa.Column('min_gpu_benchmark',        sa.Integer(), nullable=True),
        sa.Column('min_ram_gb',               sa.Integer(), nullable=True),
        sa.Column('min_storage_gb',           sa.Integer(), nullable=True),
        sa.Column('min_resolution',           sa.String(20), nullable=True),
        sa.Column('min_fps',                  sa.Integer(), nullable=True),
        # Recommended requirements
        sa.Column('rec_cpu_benchmark_single', sa.Integer(), nullable=True),
        sa.Column('rec_cpu_benchmark_multi',  sa.Integer(), nullable=True),
        sa.Column('rec_gpu_benchmark',        sa.Integer(), nullable=True),
        sa.Column('rec_ram_gb',               sa.Integer(), nullable=True),
        sa.Column('rec_storage_gb',           sa.Integer(), nullable=True),
        sa.Column('rec_resolution',           sa.String(20), nullable=True),
        sa.Column('rec_fps',                  sa.Integer(), nullable=True),
        # Ultra / high requirements
        sa.Column('ultra_cpu_benchmark_single', sa.Integer(), nullable=True),
        sa.Column('ultra_cpu_benchmark_multi',  sa.Integer(), nullable=True),
        sa.Column('ultra_gpu_benchmark',        sa.Integer(), nullable=True),
        sa.Column('ultra_ram_gb',               sa.Integer(), nullable=True),
        sa.Column('ultra_storage_gb',           sa.Integer(), nullable=True),
        sa.Column('ultra_resolution',           sa.String(20), nullable=True),
        sa.Column('ultra_fps',                  sa.Integer(), nullable=True),
        # Feature flags
        sa.Column(
            'supports_ray_tracing',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column(
            'supports_dlss',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column(
            'supports_fsr',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('release_year', sa.Integer(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )
    op.create_index('idx_game_requirements_game_name', 'game_requirements', ['game_name'])

    # ------------------------------------------------------------------ #
    # 16. software_requirements  (no FK dependencies)                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        'software_requirements',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column('software_name', sa.String(200), nullable=False),
        sa.Column('category',      sa.String(100), nullable=False),
        sa.Column('vendor',        sa.String(100), nullable=True),
        # Minimum requirements
        sa.Column('min_cpu_benchmark_single', sa.Integer(), nullable=True),
        sa.Column('min_cpu_benchmark_multi',  sa.Integer(), nullable=True),
        sa.Column('min_gpu_benchmark',        sa.Integer(), nullable=True),
        sa.Column('min_ram_gb',               sa.Integer(), nullable=True),
        sa.Column('min_storage_gb',           sa.Integer(), nullable=True),
        # Recommended requirements
        sa.Column('rec_cpu_benchmark_single', sa.Integer(), nullable=True),
        sa.Column('rec_cpu_benchmark_multi',  sa.Integer(), nullable=True),
        sa.Column('rec_gpu_benchmark',        sa.Integer(), nullable=True),
        sa.Column('rec_ram_gb',               sa.Integer(), nullable=True),
        sa.Column('rec_storage_gb',           sa.Integer(), nullable=True),
        # Professional requirements
        sa.Column('professional_cpu_benchmark_single', sa.Integer(), nullable=True),
        sa.Column('professional_cpu_benchmark_multi',  sa.Integer(), nullable=True),
        sa.Column('professional_gpu_benchmark',        sa.Integer(), nullable=True),
        sa.Column('professional_ram_gb',               sa.Integer(), nullable=True),
        sa.Column('professional_storage_gb',           sa.Integer(), nullable=True),
        # GPU acceleration
        sa.Column(
            'needs_gpu_acceleration',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('preferred_gpu_vendor', sa.String(50), nullable=True),
        sa.Column(
            'cuda_supported',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column(
            'opencl_supported',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column(
            'hip_supported',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
        sa.Column('release_year', sa.Integer(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )
    op.create_index(
        'idx_software_requirements_category',
        'software_requirements',
        ['category'],
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_index('idx_software_requirements_category', table_name='software_requirements')
    op.drop_table('software_requirements')

    op.drop_index('idx_game_requirements_game_name', table_name='game_requirements')
    op.drop_table('game_requirements')

    op.drop_table('quote_components')

    op.drop_index('idx_quotes_created_at', table_name='quotes')
    op.drop_index('idx_quotes_tier',       table_name='quotes')
    op.drop_index('idx_quotes_user_id',    table_name='quotes')
    op.drop_table('quotes')

    op.drop_table('compatibility_rules')

    op.drop_index('idx_price_history_recorded_at',        table_name='price_history')
    op.drop_index('idx_price_history_component_source',   table_name='price_history')
    op.drop_table('price_history')

    op.drop_index('idx_prices_in_stock',     table_name='prices')
    op.drop_index('idx_prices_source',       table_name='prices')
    op.drop_index('idx_prices_component_id', table_name='prices')
    op.drop_table('prices')

    op.drop_index('idx_coolers_tdp_rating_w', table_name='coolers')
    op.drop_index('idx_coolers_type',          table_name='coolers')
    op.drop_table('coolers')

    op.drop_table('cases')

    op.drop_index('idx_psus_efficiency_rating', table_name='psus')
    op.drop_index('idx_psus_wattage',           table_name='psus')
    op.drop_table('psus')

    op.drop_index('idx_storages_capacity_gb', table_name='storages')
    op.drop_index('idx_storages_interface',   table_name='storages')
    op.drop_index('idx_storages_type',        table_name='storages')
    op.drop_table('storages')

    op.drop_index('idx_rams_total_capacity_gb', table_name='rams')
    op.drop_index('idx_rams_type',              table_name='rams')
    op.drop_table('rams')

    op.drop_index('idx_motherboards_form_factor', table_name='motherboards')
    op.drop_index('idx_motherboards_chipset',     table_name='motherboards')
    op.drop_index('idx_motherboards_socket',      table_name='motherboards')
    op.drop_table('motherboards')

    op.drop_index('idx_gpus_timespy',           table_name='gpus')
    op.drop_index('idx_gpus_vram_size_gb',      table_name='gpus')
    op.drop_index('idx_gpus_chip_manufacturer', table_name='gpus')
    op.drop_table('gpus')

    op.drop_index('idx_cpus_benchmark', table_name='cpus')
    op.drop_index('idx_cpus_socket',    table_name='cpus')
    op.drop_table('cpus')

    op.drop_index('idx_components_is_active', table_name='components')
    op.drop_index('idx_components_brand',     table_name='components')
    op.drop_index('idx_components_category',  table_name='components')
    op.drop_table('components')
