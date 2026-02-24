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
                                "너는 글로벌 정책 결정관이야. 아래 '환각 방지 규칙'을 반드시 준수해.\n\n"
                                "1. **발음 변형어 처리 (시밤 등)**:\n"
                                "   - '시밤'은 시간대인 '밤'과 무관하며, 성적인 의미와도 직접적 연관이 없음.\n"
                                "   - 오직 원형 욕설인 '씨발'의 발음을 약화시키거나 필터링을 피하기 위한 '변형 비속어'로만 분석해.\n"
                                "   - 점수는 원형보다 낮은 70~80점 사이로 고정해.\n\n"
                                "2. **카테고리별 점수 강제 보정**:\n"
                                "   - [욕설/비속어]: 90~100점 (원형), 70~85점 (변형/순화).\n"
                                "   - [문화 이슈]: 80~89점. '오조오억' 등이 0점으로 나오는 오류를 절대 범하지 마.\n\n"
                                "3. **상세 배경 작성 가이드**:\n"
                                "   - '밤'이나 '음식' 같은 표면적 글자에 집착하지 말고, 해당 단어가 '커뮤니티에서 어떤 의도로 생성되었는지' 그 유래를 심층 분석해.\n"
                                "   - 정책 판단 근거에서 '한국어 욕설 발음 유사성' 언급은 맥락 오염이므로 절대 금지해."
                            )
                        },
                        {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0 
                )
                
                result = json.loads(response.choices[0].message.content)
                
                # [보정 로직] 시스템 레벨에서 점수 하한선 및 카테고리 오류 수정
                score = result.get('부정점수', 0)
                category = result.get('카테고리', '일상어')
                
                # '시밤' 같은 변형어에 95점이 나오는 과잉 대응 방지
                if word_input == "시밤" and score > 85: score = 80 
                
                st.divider()
                st.success("분석 완료")
                
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                # 배경 설명 (심각도에 따라 UI 차별화)
                if score >= 85:
                    st.error(f"⚠️ **상세 맥락 및 배경 (커뮤니티 심층 분석):** \n\n {result.get('논란의배경', '')}")
                else:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result.get('논란의배경', '')}")
                
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
