import streamlit as st
import requests
import json

# إعدادات الصفحة
st.set_page_config(page_title="LIA - Algerian AI", page_icon="🤖")

st.title("🤖 LIA - المساعدة الذكية الجزائرية")
st.markdown("---")

# التأكد من وجود Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"

# تعريف شخصية LIA (System Prompt)
SYSTEM_PROMPT = "أنتِ LIA، مساعدة ذكية جزائرية مرحة وفايقة. تحدثي بالدارجة الجزائرية."

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات القديمة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# خانة الدردشة
if prompt := st.chat_input("واش حاب تقولي لـ ليا؟"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # طلب الرد من Ollama
    with st.chat_message("assistant"):
        with st.spinner("ليا راهي تخمم..."):
            try:
                payload = {
                    "model": "qwen3:1.7b",
                    "prompt": f"{SYSTEM_PROMPT}\nالمستخدم: {prompt}\nLIA:",
                    "stream": False
                }
                response = requests.post(OLLAMA_URL, json=payload)
                full_response = response.json()['response']
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except:
                st.error("خطأ: تأكد من تشغيل Ollama في جهازك!")