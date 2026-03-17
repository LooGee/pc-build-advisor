GAME_NAME_MAPPING = {
    "PUBG": "PlayerUnknown's Battlegrounds",
    "배그": "PlayerUnknown's Battlegrounds",
    "배틀그라운드": "PlayerUnknown's Battlegrounds",
    "로스트아크": "Lost Ark",
    "WoW": "World of Warcraft",
    "와우": "World of Warcraft",
    "월드오브워크래프트": "World of Warcraft",
    "OW2": "Overwatch 2",
    "오버워치": "Overwatch 2",
    "오버워치2": "Overwatch 2",
    "사이버펑크": "Cyberpunk 2077",
    "사이버펑크2077": "Cyberpunk 2077",
    "발더스게이트3": "Baldur's Gate 3",
    "BG3": "Baldur's Gate 3",
    "리그오브레전드": "League of Legends",
    "롤": "League of Legends",
    "LOL": "League of Legends",
    "스타크래프트2": "StarCraft II",
    "스타2": "StarCraft II",
    "엘든링": "Elden Ring",
    "GTA5": "Grand Theft Auto V",
    "GTA6": "Grand Theft Auto VI",
    "발로란트": "Valorant",
    "마인크래프트": "Minecraft",
    "모더워페어": "Call of Duty: Modern Warfare",
    "에이펙스레전드": "Apex Legends",
    "에픽": "Fortnite",
    "포트나이트": "Fortnite",
}


def normalize_game_name(game: str) -> str:
    return GAME_NAME_MAPPING.get(game.strip(), game.strip())


def normalize_game_list(games: list) -> list:
    return [normalize_game_name(g) for g in games]
