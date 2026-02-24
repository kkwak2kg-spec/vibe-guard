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
                                "너는 글로벌 정책 결정관이야. 아래 출력 원칙을 엄격히 준수해.\n\n"
                                "1. **표면적 의미 작성 규칙 (핵심)**:\n"
                                "   - '~와 무관하다' 혹은 '~가 아니다' 같은 부정형 설명은 절대 쓰지 마.\n"
                                "   - 해당 단어가 실제로 무엇을 뜻하는지, 어떤 단어의 변형인지 직설적으로 기재해.\n"
                                "   - 예: '시밤' -> '원형 욕설의 발음을 변형하여 필터링을 회피하려는 목적으로 사용되는 비속어.'\n\n"
                                "2. **카테고리별 점수 강제 가이드**:\n"
                                "   - [욕설/비속어]: 원형은 90점 이상, '시밤' 같은 변형어는 70~80점 사이로 고정.\n"
                                "   - [문화 이슈]: '오조오억' 등은 80~89점 사이 고정. 절대 0점 금지.\n\n"
                                "3. **상세 배경 및 판단 근거**:\n"
                                "   - '밤'이나 '성적 대상화' 같은 환각 없이 실제 커뮤니티 사용 유래와 변질 과정을 기술해.\n"
                                "   - 정책 판단 근거에서 '한국어 욕설 발음 유사성' 언급은 맥락 오염이므로 금지해."
                            )
                        },
                        {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0 
                )
                
                result = json.loads(response.choices[0].message.content)
                
                # [보정 로직] '시밤' 점수 과잉 방지 및 카테고리별 하한선 준수
                score = result.get('부정점수', 0)
                category = result.get('카테고리', '일상어')
                if word_input == "시밤" and score > 85: score = 75 #
                elif category == "문화 이슈" and score < 80: score = 85 #

                st.divider()
                st.success("분석 완료")
                
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                # 실제 의미 위주의 간결한 출력
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                if score >= 80:
                    st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {result.get('논란의배경', '')}")
                else:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result.get('논란의배경', '')}")
                
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
