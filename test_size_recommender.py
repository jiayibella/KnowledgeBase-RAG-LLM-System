from size_recommender import recommend_size, extract_measurements


# 测试1：只有一个匹配尺码
result = recommend_size(170, 60)
assert result["weight_jin"] == 120
assert result["matched_sizes"] == ["L"]


# 测试2：同时匹配两个尺码
result = recommend_size(170, 65)
assert result["matched_sizes"] == ["L", "XL"]


# 测试3：没有匹配的尺码
result = recommend_size(170, 80)
assert result["matched_sizes"] == []


# 测试4：从完整句子中提取身高和体重
result = extract_measurements("我身高170厘米，体重60公斤")
assert result == {
    "height_cm": 170.0,
    "weight_kg": 60.0,
}


# 测试5：只提取体重
result = extract_measurements("60公斤")
assert result == {
    "height_cm": None,
    "weight_kg": 60.0,
}


print("所有尺码测试均已通过")