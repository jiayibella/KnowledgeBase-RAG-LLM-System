# 尺码规则，与 assets/尺码推荐.txt 保持一致
import re
SIZE_RULES = [
    {
        "size": "S",
        "height_min": 155,
        "height_max": 165,
        "weight_min": 75,
        "weight_max": 95,
    },
    {
        "size": "M",
        "height_min": 160,
        "height_max": 170,
        "weight_min": 90,
        "weight_max": 115,
    },
    {
        "size": "L",
        "height_min": 165,
        "height_max": 175,
        "weight_min": 115,
        "weight_max": 135,
    },
    {
        "size": "XL",
        "height_min": 170,
        "height_max": 178,
        "weight_min": 130,
        "weight_max": 150,
    },
    {
        "size": "2XL",
        "height_min": 175,
        "height_max": 182,
        "weight_min": 145,
        "weight_max": 165,
    },
    {
        "size": "3XL",
        "height_min": 178,
        "height_max": 185,
        "weight_min": 160,
        "weight_max": 180,
    },
    {
        "size": "4XL",
        "height_min": 180,
        "height_max": 190,
        "weight_min": 180,
        "weight_max": 210,
    },
    {
        "size": "5XL",
        "height_min": 190,
        "height_max": float("inf"),
        "weight_min": 210,
        "weight_max": float("inf"),
    },
]


def recommend_size(height_cm, weight_kg):
    """根据身高和公斤体重，返回严格匹配的尺码。"""

    weight_jin = weight_kg * 2
    matched_sizes = []

    for rule in SIZE_RULES:
        height_matches = (
            rule["height_min"] <= height_cm <= rule["height_max"]
        )
        weight_matches = (
            rule["weight_min"] <= weight_jin <= rule["weight_max"]
        )

        if height_matches and weight_matches:
            matched_sizes.append(rule["size"])

    return {
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "weight_jin": weight_jin,
        "matched_sizes": matched_sizes,
    }

def extract_measurements(text):
    """从文字中提取身高和体重，统一为厘米和公斤。"""

    height_cm = None
    weight_kg = None

    height_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(厘米|公分|cm)",
        text,
        flags=re.IGNORECASE,
    )

    weight_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(公斤|千克|kg|斤)",
        text,
        flags=re.IGNORECASE,
    )

    if height_match:
        height_cm = float(height_match.group(1))

    if weight_match:
        weight_kg = float(weight_match.group(1))
        unit = weight_match.group(2)

        if unit == "斤":
            weight_kg = weight_kg / 2

    return {
        "height_cm": height_cm,
        "weight_kg": weight_kg,
    }
def build_size_response(height_cm, weight_kg):
    """使用Python计算结果生成尺码回答。"""

    result = recommend_size(height_cm, weight_kg)
    weight_jin = result["weight_jin"]
    matched_sizes = result["matched_sizes"]

    if len(matched_sizes) == 0:
        return (
            f"您的身高是{height_cm}厘米，"
            f"体重是{weight_kg}公斤（{weight_jin}斤）。"
            "目前没有同时符合身高和体重条件的尺码。"
        )

    if len(matched_sizes) == 1:
        return (
            f"您的体重{weight_kg}公斤换算后是{weight_jin}斤。"
            f"结合身高{height_cm}厘米，"
            f"身高和体重同时符合{matched_sizes[0]}码，"
            f"因此建议选择{matched_sizes[0]}码。"
        )

    sizes_text = "、".join(matched_sizes)

    return (
        f"您的体重{weight_kg}公斤换算后是{weight_jin}斤。"
        f"结合身高{height_cm}厘米，"
        f"同时符合的候选尺码有{sizes_text}。"
        "请告诉我您喜欢合身还是宽松，我再进一步建议。"
    )



