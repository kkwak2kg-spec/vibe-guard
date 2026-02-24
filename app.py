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
                                "너는 글로벌 게임 정책 결정관이자 다국어 분석 전문가야. "
                                "특히 한국어 욕설과 무관한 외국어 조합을 욕설로 오판하는 '오탐(False Positive)'을 방지하는 것이 최우선 과제야.\n\n"
                                "### [오탐 방지 및 분석 프로토콜]\n"
                                "1. **언어적 원천 의미 확인 (필수)**: 단어가 외국어(베트남어, 독일어 등)를 포함할 경우, 그 언어의 본래 의미를 먼저 해석해. "
                                "의미가 건전하다면(예: '나야', '관리자' 등) 한국어 욕설과 발음이 우연히 비슷하더라도 리스크 점수를 낮게 책정해.\n"
                                "2. **음성학적 유사성 검증**: 'Admin'과 '씨발'처럼 시각적/발음상 공통점이 거의 없는 경우, 억지로 변형어로 판정하지 마.\n"
                                "3. **카테고리 및 점수 가이드**:\n"
                                "   - [확실한 욕설]: 90-100점.\n"
                                "   - [의도적 변형어]: 75-85점. (단, 발음 유사성이 명확해야 함)\n"
                                "   - [건전한 외국어/닉네임]: 0-20점. 설령 금칙어와 철자가 일부 겹쳐도 의미가 우선임.\n"
                                "4. **설명 격리**: 이전 대화의 역사적 비극이나 성적 비하 맥락을 현재 분석에 절대 섞지 마."
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
                
                # 점수대별 UI 색상 최적화
                if result['부정점수'] >= 80:
                    st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                elif result['부정점수'] >= 40:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                else:
                    st.info(f"💡 **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
