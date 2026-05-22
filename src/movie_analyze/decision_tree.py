def analyze_story_success(resultDICT):
    has_event = bool(resultDICT.get("Event"))
    has_threat = bool(resultDICT.get("Threat"))
    has_motivation = bool(resultDICT.get("Motivation"))
    has_hero_must_do = bool(resultDICT.get("Hero_must_do"))
    has_character = bool(resultDICT.get("character"))

    if not has_event:
        return {"level": "低成功率", "rate": 0.10}
    if not has_threat:
        return {"level": "中低成功率", "rate": 0.28}

    if not has_motivation:
        return {"level": "中等成功率", "rate": 0.42}
    if not has_hero_must_do:
        return {"level": "中高成功率", "rate": 0.62}
    if not has_character:
        return {"level": "高成功率", "rate": 0.72}

    return {"level": "高成功率", "rate": 0.88}

