import streamlit as st
from openai import OpenAI
import json

# 1. 페이지 설정 및 UI 초기화
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
        # 로딩 문구를 '분석 중입니다.'로 간결하게 고정
        with st.spinner('분석 중입니다.'):
            try:
                # [구조적 해결] AI가 점수를 생성하는 구간을 카테고리별로 강제 대입
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 정책 결정관이야. 아래 규칙을 '절대적'으로 준수해.\n\n"
                                "1. **카테고리별 점수 구간 강제**:\n"
                                "   - [욕설/선정적]: 반드시 90~100점.\n"
                                "   - [문화 이슈/비하 밈]: 반드시 80~89점. '오조오억' 포함.\n"
                                "   - [사회적 이슈/범죄]: 반드시 70~80점. '마약' 포함.\n"
                                "   - [정치 이슈/실명]: 반드시 60~70점.\n"
                                "   - [일상어]: 반드시 0~20점.\n\n"
                                "2. **설명 격리**: 특정 단어의 분석 배경(예: 역사적 잔혹성)을 다른 단어 분석 시 절대로 재활용하지 마.\n"
                                "3. **언어 감지**: '언어' 필드에는 반드시 공식 언어 명칭(예: 독일어, 한국어)만 기재해."
                            )
                        },
                        {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0 
                )
                
                result = json.loads(response.choices[0].message.content)
                
                # 결과 출력 (오류 발생 차단을 위한 방어 로직 포함)
                st.divider()
                st.success("분석 완료")
                
                c1, c2 = st.columns(2)
                with c1:
                    # 부정점수가 누락되었을 경우를 대비한 안전 장치
                    score = result.get('부정점수', 0)
                    st.metric("리스크 점수", f"{score}점")
                with c2:
                    st.subheader(f"🏷️ {result.get('카테고리', '미분류')}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '알 수 없음')}")
                st.info(f"📖 **의미:** \n\n {result.get('표면적의미', '내용 없음')}")
                
                # 점수대에 따른 시각적 경고 수위 조절
                bg_info = result.get('논란의배경', '내용 없음')
                if score >= 85:
                    st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {bg_info}")
                elif score >= 40:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {bg_info}")
                else:
                    st.info(f"💡 **상세 맥락 및 배경:** \n\n {bg_info}")
                
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '내용 없음')}")
                
            except Exception as e:
                # '부정점수' 키 누락 등 AI 생성 오류 발생 시 출력
                st.error(f"분석 중 오류 발생: {str(e)}")
else:
    st.info("API 키를 입력해주세요.")
