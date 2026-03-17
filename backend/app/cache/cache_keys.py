def component_key(component_id: str) -> str:
    return f"component:{component_id}"

def price_key(component_id: str) -> str:
    return f"prices:{component_id}"

def quote_key(quote_id: str) -> str:
    return f"quote:{quote_id}"

def llm_analysis_key(text_hash: int) -> str:
    return f"llm_analysis:{text_hash}"

def compatibility_key(*component_ids: str) -> str:
    sorted_ids = sorted(component_ids)
    return f"compat:{'_'.join(sorted_ids)}"
