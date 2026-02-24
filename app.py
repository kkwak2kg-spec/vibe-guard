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
        with st.spinner('커뮤니티 심층 맥락 및 정책을 정밀 분석 중입니다.'):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 정책 결정관이자 한국 온라인 커뮤니티 전문가야. 아래 지침을 엄격히 준수해.\n\n"
                                "1. **심층 분석 보고서 작성 규칙**:\n"
                                "   - [표면적 의미]: 단어의 사전적 의미나 원형을 부정형(~와 무관하다 등) 없이 실제 의미만 기재해.\n"
                                "   - [상세 맥락 및 배경]: 어느 커뮤니티에서 유래했는지, 왜 조롱이나 비하의 맥락으로 변질됐는지, 사회적 논란의 핵심이 무엇인지 아주 구체적이고 풍부하게 서술해.\n"
                                "   - [판단 근거]: 운영 정책상 리스크 점수 부여 이유를 논리적으로 설명해.\n\n"
                                "2. **카테고리별 점수 강제 가이드 (0점 방지 필수)**:\n"
                                "   - [욕설/비속어]: 90-100점 (원형), 70-85점 (변형/순화).\n"
                                "   - [문화 이슈/비하 밈]: 80-89점. '오조오억', '운지' 등 포함.\n"
                                "   - [정치 이슈]: 60-70점. '김영삼' 등 단순 실명은 0점.\n\n"
                                "3. **금지 사항**: 분석 근거에 한국어 욕설 발음 유사성 언급 금지. 성적인 환각(시밤 등) 절대 금지."
                            )
                        },
                        {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0.3 # 설명의 풍부함을 위해 온도를 약간 조절
                )
                
                result = json.loads(response.choices[0].message.content)
                
                # [안정화 레이어] AI가 설명을 쓰느라 점수를 놓쳤을 경우 시스템이 강제 보정
                final_score = result.get('부정점수', 0)
                category = result.get('카테고리', '미분류')
                
                # 비속어나 문화 이슈인데 0점인 경우를 물리적으로 차단
                if category == '욕설/비속어' and final_score < 70: final_score = 75
                elif category in ['문화 이슈', '문화 이슈/비하 밈'] and final_score < 80: final_score = 85
                
                st.divider()
                st.success("분석 완료")
                
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{final_score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                # 배경 설명은 에러 창으로 강력하게 시각화하여 분량 확보 유도
                st.error(f"⚠️ **상세 맥락 및 배경 (커뮤니티 심층 분석):** \n\n {result.get('논란의배경', '')}")
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
