import streamlit as st
from openai import OpenAI
import json

# 1. 정책 고정 데이터베이스 (설명의 풍부함과 UI 시각화 강화)
FIXED_DATABASE = {
    "오조오억": {
        "부정점수": 80, 
        "카테고리": "문화 이슈", 
        "의미": "상당히 많은 수를 의미하는 관용적 표현.",
        "배경": "본래 긍정적인 응원의 의미로 사용되었으나, 특정 온라인 커뮤니티에서 남성 비하적 맥락의 밈으로 변질되어 사용되면서 사회적 갈등을 유발하는 단어로 인식됨.",
        "근거": "젠더 갈등과 연관된 민감한 키워드로, 커뮤니티 내 불필요한 분쟁을 방지하기 위해 관리가 필요함."
    },
    "통매음": {
        "부정점수": 25, 
        "카테고리": "사회적 이슈", 
        "의미": "통신매체이용음란죄의 줄임말.",
        "배경": "자기 또는 다른 사람의 성적 욕망을 유발하거나 만족시킬 목적으로 통신매체를 이용해 성적 수치심을 주는 행위를 처벌하는 법률상의 죄명임.",
        "근거": "비속어 자체가 아닌 법적 용어이므로 낮은 리스크를 부여하되, 관련 분쟁의 맥락을 모니터링해야 함."
    }
}

st.set_page_config(page_title="Global Vibe Guard Pro", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    word_input = st.text_input("분석할 단어:", placeholder="").strip()

    if st.button("분석"):
        with st.spinner('분석 중입니다.'):
            # [Step 1] 고정 DB 확인 (AI급 UI 적용)
            if word_input in FIXED_DATABASE:
                data = FIXED_DATABASE[word_input]
                st.divider()
                st.success("분석 완료")
                col_score, col_cat = st.columns(2)
                with col_score: st.metric("리스크 점수", f"{data['부정점수']}점")
                with col_cat: st.subheader(f"🏷️ {data['카테고리']}")
                
                st.write(f"🌐 **감지된 언어:** 한국어(고정)")
                st.info(f"📖 **표면적 의미:** \n\n {data['의미']}")
                st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {data['배경']}")
                st.info(f"⚖️ **정책 판단 근거:** \n\n {data['근거']}")
            
            # [Step 2] 미등록 단어 분석 (다국어 및 맥락 격리 강화)
            else:
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": "너는 글로벌 정책관이야. 언어 감지(독일어 등)를 정확히 수행하고, 이전 맥락과 완전히 격리된 분석을 수행해. 욕설은 90-100점, 사회적 이슈는 70-80점대로 책정해."
                            },
                            {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("분석 완료")
                    col_score, col_cat = st.columns(2)
                    with col_score: st.metric("리스크 점수", f"{result['부정점수']}점")
                    with col_cat: st.subheader(f"🏷️ {result['카테고리']}")
                    st.write(f"🌐 **감지된 언어:** {result['언어']}")
                    st.info(f"📖 **의미:** {result['표면적의미']}")
                    st.warning(f"⚠️ **배경:** {result['논란의배경']}")
                    st.info(f"⚖️ **판단근거:** {result['판단근거']}")
                except:
                    st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
