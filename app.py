from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from chat_coordinator import get_concierge_response
from investigation_agent import InvestigationInput, generate_investigation_report

st.set_page_config(page_title="DVCI Operations Center", page_icon="🛡️", layout="wide")

st.markdown(
    """
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            direction: rtl;
        }
        [data-testid="stSidebar"] {
            direction: rtl;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    .reportview-container, .main, .block-container {
        background-color: #051529;
        color: #F4F7FB;
    }
    .stApp {
        background: linear-gradient(180deg, #061F3F 0%, #081F3C 100%);
        color: #F4F7FB;
    }
    .css-18e3th9 {
        padding-top: 1rem;
    }
    .css-1d391kg {
        background-color: #061F3F;
    }
    .css-1v3fvcr {
        background-color: #08254A;
        color: #F4F7FB;
        border-radius: 18px;
        padding: 1rem;
    }
    .css-1lcbmhc, .css-1avcm0n, .css-14xtw13, .css-1f0vkj0 {
        color: #F4F7FB;
    }
    .css-18ni7ap {
        background-color: #061F3F;
    }
    .css-1q8dd3e .stButton>button {
        background-color: #7D57FF;
        color: #fff;
        border: none;
    }
    .css-1q8dd3e .stButton>button:hover {
        background-color: #5E3ECA;
    }
    .stSidebar {
        background: #081F3C;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #0E2A55;
        border-radius: 14px;
        padding: 18px 24px;
        margin-bottom: 1rem;
    }
    .app-brand {
        font-size: 1.4rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    .app-subtitle {
        color: #A6BCCE;
        font-size: 0.95rem;
    }
    .card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 1.25rem;
    }
    .card h2, .card h3 {
        color: #FFFFFF;
    }
    .st-expander {
        background: rgba(255,255,255,0.04);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="app-header">
        <div>
            <div class="app-brand">DVCI | غرفة عمليات الامتثال</div>
            <div class="app-subtitle">توجيه فوري وإجراءات تشغيلية سريعة وفق أسلوب بنك الإنماء</div>
        </div>
        <div style="text-align:right; color:#FFFFFF; font-size:0.9rem;">تجربة العرض | Proactive Operations</div>
    </div>
    """,
    unsafe_allow_html=True,
)


def load_dashboard_html() -> str:
    dashboard_path = Path(__file__).with_name("smart_dashboard.html")
    if dashboard_path.exists():
        return dashboard_path.read_text(encoding="utf-8")
    return "<div style='color:white;padding:24px;'>لم يتم العثور على لوحة المراقبة.</div>"


def build_recommendations(report_data: dict) -> list[str]:
    recs: list[str] = []
    pattern = str(report_data.get("pattern", "")).lower()
    if "structuring" in pattern:
        recs.append("طلب كشف حساب للأشهر الستة الماضية من العميل.")
        recs.append("تحديث سجل التدقيق وتوثيق سبب الشذوذ.")
    recs.append("مراجعة التحليل السلوكي ضمن التقرير قبل اتخاذ أي إجراء نهائي.")
    recs.append("إرسال نسخة من التقرير إلى موظف الامتثال للمراجعة البشرية.")
    return recs


def build_report_snapshot() -> dict:
    sample_input = InvestigationInput(
        case_id="CASE-0001",
        demo_mode=True,
        cpp_findings={
            "pattern": "structuring",
            "transaction_count": 5,
            "amounts": [15000, 14800, 15200, 14950, 15100],
            "time_window_hours": 36,
            "threshold_sar": 60000,
            "confidence": 1.0,
        },
        client_profile={
            "customer_id": "SAMPLE-0001",
            "account_age_years": 2,
            "average_monthly_volume_sar": 8000,
            "risk_tier": "medium",
        },
    )
    report_obj = generate_investigation_report(sample_input)
    return {
        "case_id": report_obj.case_id,
        "status": report_obj.status,
        "demo_mode": report_obj.demo_mode,
        "within_time_budget": report_obj.within_time_budget,
        "ai_available": report_obj.ai_available,
        "behavioral_analysis": report_obj.behavioral_analysis,
        "interrogation_questions": report_obj.interrogation_questions,
        "sama_articles": report_obj.sama_articles,
        "raw_cpp_findings": report_obj.raw_cpp_findings,
        "markdown": report_obj.to_markdown(),
        "json": report_obj.to_json(),
        "pattern": "structuring",
        "risk_level": "high",
        "recommendations": build_recommendations({"pattern": "structuring"}),
    }


if "messages" not in st.session_state:
    st.session_state.messages = []

if "report_data" not in st.session_state:
    st.session_state.report_data = build_report_snapshot()

if "case_context" not in st.session_state:
    st.session_state.case_context = {
        "case_id": st.session_state.report_data["case_id"],
        "status": st.session_state.report_data["status"],
        "pattern": st.session_state.report_data["pattern"],
        "risk_level": st.session_state.report_data["risk_level"],
        "behavioral_analysis": st.session_state.report_data["behavioral_analysis"],
        "recommendations": st.session_state.report_data["recommendations"],
    }

st.title("غرفة عمليات الامتثال - DVCI")
st.caption("واجهة موحدة للتقرير الذكي والتوصيات والشات التشغيلي")

if "active_view" not in st.session_state:
    st.session_state.active_view = "operations"

view_options = {
    "operations": "لوحة العمليات",
    "dashboard": "لوحة المراقبة الذكية",
}
selected_view = st.radio(
    "التنقل",
    options=list(view_options.keys()),
    format_func=lambda key: view_options[key],
    horizontal=True,
    key="active_view",
)

if selected_view == "operations":
    col1, col2, col3 = st.columns(3)
    col1.metric("مستوى المخاطر", "عالي 🚨", "+15%")
    col2.metric("حالة الحالة", "تحت المراجعة ⏳")
    col3.metric("زمن المعالجة", "0.8 ثانية ⚡")

    st.divider()

    with st.sidebar:
        st.header("سياق الحالة")
        st.json(st.session_state.case_context)
        if st.button("إعادة توليد التقرير"):
            st.session_state.report_data = build_report_snapshot()
            st.session_state.case_context = {
                "case_id": st.session_state.report_data["case_id"],
                "status": st.session_state.report_data["status"],
                "pattern": st.session_state.report_data["pattern"],
                "risk_level": st.session_state.report_data["risk_level"],
                "behavioral_analysis": st.session_state.report_data["behavioral_analysis"],
                "recommendations": st.session_state.report_data["recommendations"],
            }
            st.rerun()
        if st.button("مسح المحادثة"):
            st.session_state.messages = []

    col_report, col_chat = st.columns([1.6, 1.0], gap="large")

    with col_report:
        st.markdown("""
        <div class="card">
            <h2>ملخص التحقيق</h2>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**الحالة:** {st.session_state.report_data['case_id']}")
        st.markdown(f"**الحالة التشغيلية:** {st.session_state.report_data['status']}")
        st.markdown(f"**التحليل اللغوي متاح:** {'نعم' if st.session_state.report_data['ai_available'] else 'لا'}")
        st.markdown(f"**ضمن ميزانية الزمن:** {'نعم' if st.session_state.report_data['within_time_budget'] else 'لا'}")

        st.markdown("""
        <div class="card">
            <h3>التوصيات التشغيلية</h3>
        </div>
        """, unsafe_allow_html=True)
        for rec in st.session_state.report_data["recommendations"]:
            st.markdown(f"- {rec}")

        with st.expander("عرض التقرير الكامل", expanded=True):
            st.markdown(st.session_state.report_data["markdown"])

        with st.expander("الأساس الحتمي من C++", expanded=False):
            st.json(st.session_state.report_data["raw_cpp_findings"])

    with col_chat:
        st.markdown("""
        <div class="card">
            <h2>مساعد غرفة العمليات</h2>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("💬 المساعد الذكي لغرفة العمليات")
        chat_container = st.container(height=400)

        for message in st.session_state.messages:
            with chat_container.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("اكتبي استفسارك هنا..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            chat_container.chat_message("user").markdown(prompt)

            with chat_container.chat_message("assistant"):
                with st.spinner("جاري التحليل..."):
                    response = get_concierge_response(
                        prompt,
                        {
                            **st.session_state.case_context,
                            "report_markdown": st.session_state.report_data["markdown"],
                            "raw_cpp_findings": st.session_state.report_data["raw_cpp_findings"],
                        },
                    )
                    st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.markdown("""
    <div class="card" style="margin-bottom: 1rem;">
        <h2>لوحة المراقبة الذكية</h2>
        <p style="color: #A6BCCE;">واجهة تشغيلية حية مع مؤشرات الأداء والسجل البرمجي المباشر.</p>
    </div>
    """, unsafe_allow_html=True)
    components.html(load_dashboard_html(), height=1400, scrolling=True)
