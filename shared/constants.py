# Global constants shared across services

# Component categories
COMPONENT_CATEGORIES = ["cpu", "gpu", "motherboard", "ram", "storage", "psu", "case", "cooler"]

# Price sources
PRICE_SOURCES = ["danawa", "compuzone", "coupang", "pcpartpicker"]

# Quote tiers
QUOTE_TIERS = ["minimum", "balanced", "maximum"]

# Cache TTLs (seconds)
CACHE_TTL_COMPONENT = 86400   # 24h
CACHE_TTL_PRICE = 21600       # 6h
CACHE_TTL_LLM = 3600          # 1h

# Performance benchmarks (rough reference values)
GPU_BENCHMARK_TIERS = {
    "entry": 5000,
    "mid_low": 8000,
    "mid": 11000,
    "high": 15000,
    "ultra": 20000,
}

CPU_BENCHMARK_TIERS = {
    "entry": 6000,
    "mid_low": 10000,
    "mid": 15000,
    "high": 22000,
    "ultra": 35000,
}
