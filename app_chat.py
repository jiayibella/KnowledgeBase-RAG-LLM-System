import streamlit as  st
from rag import RagService
import config_data as config
import time
from size_recommender import (
    extract_measurements,
    recommend_size,
    build_size_response,
)

# 标题
st.title("智能客服")
# 分隔符
st.divider()

# 避免性能压力，session_state 存入对象
if "message" not in st.session_state:
    st.session_state["message"]=[{"role":"assistant","content":"你好，有什么可以帮助你？"}]

if "rag" not in st.session_state:
    st.session_state["rag"]= RagService()
if "size_height_cm" not in st.session_state:
    st.session_state["size_height_cm"] = None

if "size_weight_kg" not in st.session_state:
    st.session_state["size_weight_kg"] = None


if "size_mode" not in st.session_state:
    st.session_state["size_mode"] = False
#循环 输出历史信息，原本只记录但页面不显示
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])
# 在页面最下方提供用户输入栏
prompt= st.chat_input()

if prompt :
    # 在页面输出用户的提问
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role":"user","content":prompt})

    # 从用户输入中提取身高和体重
    measurements = extract_measurements(prompt)

    # 判断用户是否发起了新的尺码咨询
    size_question_keywords = ["尺码", "码数", "穿多大"]
    is_new_size_question = any(
        keyword in prompt for keyword in size_question_keywords
    )

    if is_new_size_question:
        st.session_state["size_mode"] = True
        st.session_state["size_height_cm"] = None
        st.session_state["size_weight_kg"] = None

    # 尺码咨询期间，保存本轮提取到的信息
    if st.session_state["size_mode"]:
        if measurements["height_cm"] is not None:
            st.session_state["size_height_cm"] = measurements["height_cm"]

        if measurements["weight_kg"] is not None:
            st.session_state["size_weight_kg"] = measurements["weight_kg"]
    
    fit_preference = None #先初始化一个变量，用来存放用户对版型的偏好（合身 / 宽松），一开始默认是“没有收集到偏好”

    if "合身" in prompt:
        fit_preference = "合身"
    elif "宽松" in prompt:
        fit_preference = "宽松"
    if st.session_state["size_mode"]:
        height_cm = st.session_state["size_height_cm"]
        weight_kg = st.session_state["size_weight_kg"]

        if height_cm is None:
            ai_response = "为了准确推荐尺码，请告诉我您的身高。"

        elif weight_kg is None:
            ai_response = "为了准确推荐尺码，请告诉我您的体重。"

        else:
            size_result = recommend_size(height_cm, weight_kg)
            matched_sizes = size_result["matched_sizes"]

            if len(matched_sizes) > 1 and fit_preference == "合身":
                ai_response = (
                    f"根据您的身高和体重，符合的尺码有"
                    f"{'、'.join(matched_sizes)}。"
                    f"您喜欢合身，因此建议选择{matched_sizes[0]}码。"
                )
                st.session_state["size_mode"] = False

            elif len(matched_sizes) > 1 and fit_preference == "宽松":
                ai_response = (
                    f"根据您的身高和体重，符合的尺码有"
                    f"{'、'.join(matched_sizes)}。"
                    f"您喜欢宽松，因此建议选择{matched_sizes[-1]}码。"
                )
                st.session_state["size_mode"] = False

            else:
                ai_response = build_size_response(height_cm, weight_kg)

                if len(matched_sizes) <= 1:
                    st.session_state["size_mode"] = False

        st.chat_message("assistant").write(ai_response)
        st.session_state["message"].append(
            {"role": "assistant", "content": ai_response}
        )

    else:
        ai_res_list = []

        with st.spinner("AI 思考中......."):
            res_stream = st.session_state["rag"].chain.stream(
                {"input": prompt},
                config.session_config,
            )

            def capture(generator, cache_list):
                try:
                    for chunk in generator:
                     cache_list.append(chunk)
                    yield chunk

                except Exception as error:
                   error_message = (
                       "抱歉，服务暂时不可用或网络连接异常，"
                       "请检查网络后重新尝试。"
                    )
                   cache_list.append(error_message)
                   print(f"模型调用失败：{error}")
                   yield error_message

            st.chat_message("assistant").write_stream(
                capture(res_stream, ai_res_list)
            )
            st.session_state["message"].append(
                {
                    "role": "assistant",
                    "content": "".join(ai_res_list),
                }
            )
