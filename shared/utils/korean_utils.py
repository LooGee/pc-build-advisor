import re

def normalize_korean_budget(text: str) -> int | None:
    """한국어 예산 표현을 숫자로 변환"""
    text = text.replace(",", "").replace(" ", "")

    # "150만원", "150만" → 1500000
    match = re.search(r"(\d+(?:\.\d+)?)만원?", text)
    if match:
        return int(float(match.group(1)) * 10000)

    # "1억5천" → 150000000
    match = re.search(r"(\d+)억", text)
    if match:
        return int(match.group(1)) * 100000000

    # Plain number
    match = re.search(r"(\d+)", text)
    if match:
        val = int(match.group(1))
        if val < 10000:  # Probably in 만원 units
            return val * 10000
        return val

    return None


def normalize_game_name(text: str) -> str:
    """게임명 한국어 별칭 정규화"""
    aliases = {
        "배그": "PUBG",
        "배틀그라운드": "PUBG",
        "로스트아크": "Lost Ark",
        "오버워치": "Overwatch 2",
        "오버워치2": "Overwatch 2",
        "와우": "World of Warcraft",
        "사이버펑크": "Cyberpunk 2077",
        "롤": "League of Legends",
        "리그오브레전드": "League of Legends",
        "발로란트": "Valorant",
        "마크": "Minecraft",
        "마인크래프트": "Minecraft",
        "포트나이트": "Fortnite",
        "에픽": "Fortnite",
        "스타2": "StarCraft II",
        "스타크래프트2": "StarCraft II",
        "엘든링": "Elden Ring",
    }
    return aliases.get(text.strip(), text.strip())
