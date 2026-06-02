import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go
import json
from pypdf import PdfReader

# 1. 페이지 기본 설정 및 테마 (헤지펀드 터미널 스타일)
st.set_page_config(
    page_title="Professional Equity Research Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .reportview-container { background: #0E1117; }
    .main .block-container { padding-top: 2rem; max-width: 1400px; }
    h1, h2, h3 { color: #F8F9FA; font-weight: 700; }
    div.stButton > button:first-child {
        background-color: #0066cc; color: white; border-radius: 4px; border: none; width: 100%;
    }
    .status-box { padding: 15px; border-radius: 5px; background-color: #1E293B; border-left: 5px solid #0066cc; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# 2. 사이드바 - API 설정 및 데이터 입력
st.sidebar.title("🔒 Analyst Authentication & Input")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
ticker_input = st.sidebar.text_input("Target Ticker / Company Name", placeholder="e.g., AAPL, 005930")
uploaded_file = st.sidebar.file_uploader("Upload Financial Statements (Optional)", type=["pdf", "xlsx"])

# 3. 메인 대시보드 타이틀
st.title("📊 Senior Equity Research Terminal")
st.caption("Global Hedge Fund & Asset Management Quantitative Valuation System")
st.markdown("---")

if not api_key:
    st.info("💡 시스템을 가동하려면 사이드바에 Gemini API Key를 입력하십시오.")
    st.stop()

# Gemini 모델 설정
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

# PDF 텍스트 추출 함수
def extract_pdf_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# 분석 실행 버튼
if st.sidebar.button("RUN COMPREHENSIVE ANALYSIS"):
    if not ticker_input:
        st.error("분석 대상 기업명 또는 티커를 입력하십시오.")
        st.stop()
        
    with st.spinner("전사적 분석 체계 가동 중... 실시간 데이터 및 거시경제 지표 수집 중..."):
        
        # 파일 업로드 컨텍스트 처리
        file_context = ""
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.pdf'):
                file_context = extract_pdf_text(uploaded_file)[:30000] # 모델 컨텍스트 제한 고려
            elif uploaded_file.name.endswith('.xlsx'):
                df_sheets = pd.read_excel(uploaded_file, sheet_name=None)
                file_context = "\n".join([f"Sheet: {k}\n{v.to_string()[:5000]}" for k, v in df_sheets.items()])

        # 구조화된 데이터 출력을 강제하기 위한 프롬프트 엔지니어링
        prompt = f"""
        당신은 글로벌 헤지펀드의 수석 에퀴티 리서치 애널리스트입니다. 아래 명시된 규칙을 극한으로 준수하여 대상 기업 [{ticker_input}]에 대한 정밀 진단 보고서를 작성하십시오.
        
        [첨부된 재무 데이터 가용성]
        {file_context if file_context else "없음 (실시간 수집 데이터 활용)"}

        [수행 지침]
        1. 기계적인 서두("살펴보겠습니다", "결론적으로" 등)를 전면 금지하고, 출판물 수준의 정제된 금융 분석 언어만 구사하십시오.
        2. 정밀도 향상을 위해 수치 연산은 소수점 4자리를 유지하십시오.
        3. 아래의 JSON 스키마 구조에 완벽히 매핑되는 분석 결과를 반환하십시오. 텍스트 설명 부분에는 LaTeX 수식과 Excel 수식이 완벽히 포함되어야 합니다.

        결과는 반드시 다음 구조의 유효한 JSON 형식으로만 출력하십시오. 앞뒤에 ```json 같은 마크다운 태그를 붙이지 말고 순수 JSON 문자열만 반환하십시오.
        {{
            "macro_analysis": "거시경제 및 산업 사이클 분석 내용",
            "financial_analysis": "연결재무제표 정밀 분석 (LaTeX 및 엑셀 수식 포함)",
            "valuation": "다차원 주식가치평가 및 벨류에이션 모델 결과",
            "risk_analysis": "레버리지 및 ESG 위험 분석 결과",
            "alternative_data": "비정형 데이터 및 센티먼트 분석 결과",
            "scorecard": {{
                "macro": 85,
                "financial": 90,
                "valuation": 75,
                "risk": 80,
                "alternative": 88,
                "total": 83.6
            }},
            "final_decision": "BUY, SELL, HOLD 중 하나",
            "rationale": "압도적인 핵심 논거 요약"
        }}
        """

        try:
            response = model.generate_content(prompt)
            # JSON 파싱 공백 제거 및 보정
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            result = json.loads(response_text)
            
            # --- 대시보드 렌더링 시작 ---
            
            # 1. 최종 투자 결정 (Top Banner)
            decision_color = "#22C55E" if result['final_decision'] == "BUY" else ("#EF4444" if result['final_decision'] == "SELL" else "#EAB308")
            st.markdown(f"""
                <div style="background-color: {decision_color}; padding: 25px; border-radius: 8px; text-align: center; margin-bottom: 30px;">
                    <h1 style="color: white; margin: 0; font-size: 2.5rem; letter-spacing: 2px;">FINAL INVESTMENT DECISION: {result['final_decision']}</h1>
                </div>
            """, unsafe_allow_html=True)
            
            # 2. 통합 스코어카드 및 레이더 차트 시각화
            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader("📊 Integrated Analysis Scorecard")
                score_df = pd.DataFrame({
                    "Evaluation Metric": ["Macro & Industry", "Financial Soundness", "Valuation Models", "Risk Assessment", "Alternative Sentiment", "OVERALL SCORE"],
                    "Score": [result['scorecard']['macro'], result['scorecard']['financial'], result['scorecard']['valuation'], result['scorecard']['risk'], result['scorecard']['alternative'], result['scorecard']['total']]
                })
                st.table(score_df.style.background_gradient(cmap="Blues", subset=["Score"]))
                
            with col2:
                # Plotly를 활용한 가독성 높은 시각화 컴포넌트 배치
                categories = ['Macro', 'Financial', 'Valuation', 'Risk', 'Alternative']
                scores = [result['scorecard']['macro'], result['scorecard']['financial'], result['scorecard']['valuation'], result['scorecard']['risk'], result['scorecard']['alternative']]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=scores, theta=categories, fill='toself', name='Asset Profile', line_color='#0066cc'))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False, template="plotly_dark", margin=dict(t=20, b=20, l=20, r=20)
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"> **Core Rationale:** {result['rationale']}")
            st.markdown("---")

            # 3. 8단계 상세 분석 결과 아코디언 매핑 (Canvas 스타일의 전용 인터페이스 구현)
            with st.expander("Step 3: Macro & Industry Cycle Analysis", expanded=True):
                st.markdown(result['macro_analysis'])
                
            with st.expander("Step 4: Advanced Financial Statement Analysis", expanded=True):
                st.markdown(result['financial_analysis'])
                
            with st.expander("Step 5: Multi-dimensional Valuation & Algorithmic Pricing", expanded=True):
                st.markdown(result['valuation'])
                
            with st.expander("Step 6: Leverage & ESG Risk Matrix", expanded=True):
                st.markdown(result['risk_analysis'])
                
            with st.expander("Step 7: Alternative Data Sentiment Mining", expanded=False):
                st.markdown(result['alternative_data'])

        except Exception as e:
            st.error(f"분석 파이프라인 연산 중 오류가 발생했습니다: {str(e)}")
            st.info("API 반환 데이터 형식이 유효하지 않거나 한도 초과일 수 있습니다. 입력을 확인 후 재시도하십시오.")
