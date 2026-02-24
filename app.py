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
    # 입력창 placeholder 빈칸 유지
    word_input = st.text_input("분석할 단어:", placeholder="").strip()

    if st.button("분석"):
        # 로딩 문구를 '분석 중입니다.'로 완전히 고정
        with st.spinner('분석 중입니다.'):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 정책 결정관이자 한국 온라인 커뮤니티 전문가야.\n\n"
                                "1. **심층 분석 보고서 작성 규칙 (설명 강화)**:\n"
                                "   - [표면적 의미]: 부정형 표현 없이 실제 의미만 기재.\n"
                                "   - [상세 맥락 및 배경]: 어느 커뮤니티 유래인지, 왜 조롱/비하로 변질됐는지 심층 분석하여 풍부하게 서술.\n"
                                "   - [판단 근거]: 정책적 관리 필요성을 논리적으로 기술.\n\n"
                                "2. **점수 및 카테고리 가이드 (로직 고정)**:\n"
                                "   - [욕설/비속어]: 90~100점 (변형어는 75~85점).\n"
                                "   - [문화 이슈/비하 밈]: 80~89점. '오조오억', '운지' 등 절대 0점 금지.\n"
                                "   - [정치 이슈]: 60~70점. '김영삼' 등 단순 실명은 0점 유지.\n\n"
                                "3. **금지 사항**: 한국어 욕설 발음 유사성 언급 금지, 성적 환각(시밤 등) 절대 금지."
                            )
                        },
                        {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0.3 
                )
                
                result = json.loads(response.choices[0].message.content)
                
                # [보정 레이어] AI가 누락한 점수를 시스템이 강제 교정
                final_score = result.get('부정점수', 0)
                category = result.get('카테고리', '미분류')
                
                if category == '욕설/비속어' and final_score < 70: final_score = 75
                elif category in ['문화 이슈', '문화 이슈/비하 밈'] and final_score < 80: final_score = 85
                
                st.divider()
                st.success("분석 완료")
                
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{final_score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                # 80점 이상 위험어는 붉은색 에러창으로 상세 배경 출력
                if final_score >= 80:
                    st.error(f"⚠️ **상세 맥락 및 배경 (커뮤니티 심층 분석):** \n\n {result.get('논란의배경', '')}")
                else:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result.get('논란의배경', '')}")
                    
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
