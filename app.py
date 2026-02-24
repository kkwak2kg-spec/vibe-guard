import streamlit as st
from openai import OpenAI
import json

# 1. 페이지 설정
st.set_page_config(page_title="Global Vibe Guard Pro", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

# 2. API 키 로드
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key 설정", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    word_input = st.text_input("분석할 단어:", placeholder="").strip()

    if st.button("분석"):
        with st.spinner('분석 중입니다.'):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 게임 정책 결정관이자 한국 온라인 커뮤니티 전문가야.\n\n"
                                "1. **변형어/순화어 점수 규칙**:\n"
                                "   - '시밤', '시바' 등 원형 욕설(씨발)의 변형어나 순화어는 원형보다 리스크를 낮게 책정해.\n"
                                "   - [직설적 욕설]: 90-100점.\n"
                                "   - [변형/순화된 욕설]: 70-80점. (예: 시밤 등)\n\n"
                                "2. **오탐 방지 (선정성 배제)**:\n"
                                "   - '시밤' 분석 시 이를 성적인 의미('시'와 '밤'의 결합 등)와 연결하지 마.\n"
                                "   - 오직 '씨발'의 발음 변형 및 순화된 욕설 맥락으로만 분석해.\n\n"
                                "3. **카테고리 가이드라인**:\n"
                                "   - 변형어는 [욕설/비속어] 카테고리를 유지하되, 설명에서 순화된 표현임을 명시해.\n\n"
                                "4. **맥락 격리**: 이전 단어의 분석 내용(역사적 비극, 성적 비하 등)을 현재 분석에 절대 섞지 마."
                            )
                        },
                        {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0 
                )
                
                result = json.loads(response.choices[0].message.content)
                st.divider()
                st.success("분석 완료")
                
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{result['부정점수']}점")
                with c2: st.subheader(f"🏷️ {result['카테고리']}")
                
                st.write(f"🌐 **감지된 언어:** {result['언어']}")
                st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                
                # 점수대에 따른 UI 처리
                if result['부정점수'] >= 85:
                    st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                else:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                
                st.info(f"⚖️ **정책 판단 근거 및 운영 가이드:** \n\n {result['판단근거']}")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
