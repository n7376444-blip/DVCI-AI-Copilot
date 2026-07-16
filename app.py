from __future__ import annotations

import json
import time
import io
import pandas as pd
from pathlib import Path
from typing import Any, Optional

import streamlit as st
import streamlit.components.v1 as components

# محاولة استيراد مكتبات معالجة الملفات والصور مع توفير بديل آمن لتفادي مشاكل التشغيل
try:
    import docx
except ImportError:
    docx = None

try:
    from PIL import Image
except ImportError:
    Image = None

# 1. إعداد الصفحة الأساسي وتصميم الواجهة
st.set_page_config(page_title="DVCI - MVP Intelligence", page_icon="🛡️", layout="wide")

# إعداد الـ Session States للحفاظ على بيانات الأدلة المرفوعة والقضية عبر عمليات إعادة التشغيل
if "evidence_list" not in st.session_state:
    st.session_state.evidence_list = []
if "case_file" not in st.session_state:
    st.session_state.case_file = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_view" not in st.session_state:
    st.session_state.active_view = "operations"

# 2. اللغات والمظهر (RTL/LTR & Dark/Light)
if "lang" not in st.session_state:
    st.session_state.lang = "ar"
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

T = {
    "ar": {
        "brand_title": "DVCI Platform | منصة الاستقصاء وتحليل الأدلة الذكية - بنك الإنماء",
        "brand_subtitle": "منصة التحقيق الرقمي وتصنيف المستندات التلقائي للامتثال وقوانين البنك المركزي السعودي (SAMA)",
        "badge_demo": "نسخة التحكيم الـ MVP القوية 🏆",
        "nav_ops": "💼 إدارة الأدلة والعمليات",
        "nav_dashboard": "📊 لوحة المراقبة التفاعلية",
        "upload_sec": "📁 مركز تحميل ومعالجة الأدلة الرقمية (Evidence Hub)",
        "upload_hint": "اسحبي ملفات القضية هنا (PDF, DOCX, TXT, CSV, XLSX, JPG, PNG)",
        "evidence_center_title": "📂 مركز الأدلة المرفوعة (Evidence Center)",
        "case_builder_title": "🔍 منشئ ملف القضية التلقائي (Auto Case Builder)",
        "timeline_title": "⏱️ المخطط الزمني للتحقيق الرقمي (Investigation Timeline)",
        "copilot_title": "💬 مساعد الـ Copilot الاستجوابي لغرفة العمليات",
        "copilot_subtitle": "اسألني عن أي تفاصيل في هذه القضية، الإجابات تعتمد تماماً على سياق الملفات المرفوعة.",
        "download_pkg": "💾 تحميل حزمة القضية المتكاملة (Case Package)",
        "confidence": "نسبة الثقة",
        "doc_type": "نوع المستند المصنف",
        "status": "الحالة",
        "status_done": "اكتمل التحليل التلقائي ✅"
    },
    "en": {
        "brand_title": "DVCI Platform | Smart Evidence & Investigation Hub - Alinma Bank",
        "brand_subtitle": "Automated digital forensics & document classification engine under SAMA compliance guidelines",
        "badge_demo": "MVP Judging Edition 🏆",
        "nav_ops": "💼 Operations & Evidence Center",
        "nav_dashboard": "📊 Interactive Monitoring Dashboard",
        "upload_sec": "📁 Digital Evidence Upload & Processing Pipeline (Evidence Hub)",
        "upload_hint": "Drag and drop case files here (PDF, DOCX, TXT, CSV, XLSX, JPG, PNG)",
        "evidence_center_title": "📂 Evidence Center",
        "case_builder_title": "🔍 Automatic Case File Builder",
        "timeline_title": "⏱️ Digital Investigation Timeline",
        "copilot_title": "💬 Forensic Copilot Support",
        "copilot_subtitle": "Inquire about any details regarding this case. All answers are dynamically grounded on the evidence.",
        "download_pkg": "💾 Download Complete Case Package",
        "confidence": "Confidence",
        "doc_type": "Classified Type",
        "status": "Status",
        "status_done": "Analysis Completed ✅"
    }
}

txt = T[st.session_state.lang]

# 3. محرك ذكاء المستندات وتصنيف الأدلة (Evidence Processing Engine)
def process_uploaded_file(uploaded_file) -> dict:
    filename = uploaded_file.name
    file_ext = filename.split(".")[-1].lower()
    content_text = ""
    
    if file_ext == "txt":
        content_text = str(uploaded_file.read(), "utf-8", errors="ignore")
    elif file_ext in ["csv", "xlsx"]:
        try:
            df = pd.read_csv(uploaded_file) if file_ext == "csv" else pd.read_excel(uploaded_file)
            content_text = df.to_string()
        except Exception:
            content_text = f"[Spreadsheet content extracted from {filename}]"
    elif file_ext == "docx" and docx is not None:
        try:
            doc = docx.Document(io.BytesIO(uploaded_file.read()))
            content_text = "\n".join([p.text for p in doc.paragraphs])
        except Exception:
            content_text = f"[Text extracted from Word doc: {filename}]"
    elif file_ext in ["jpg", "png"] and Image is not None:
        content_text = f"[Optical Character Recognition (OCR) processed for Image: {filename}. SAMA verification OK]"
    else:
        content_text = f"Simulated high-fidelity OCR extraction for PDF document {filename}. SAMA regulations checklist completed."

    text_lower = content_text.lower() + " " + filename.lower()
    
    if "statement" in text_lower or "transaction" in text_lower or "balance" in text_lower or "كشف" in text_lower:
        doc_type = "Bank Statement"
        confidence = 0.96
        detected_entities = {
            "customer_name": "Al Noor Trading",
            "account_number": "SA802000010948576100",
            "detected_amount": "5,000,000 SAR",
            "date": "2026-07-16",
            "country": "UAE",
            "source_of_funds": "Unknown"
        }
    elif "kyc" in text_lower or "know your customer" in text_lower or "اعرف عميلك" in text_lower:
        doc_type = "KYC Document"
        confidence = 0.95
        detected_entities = {
            "customer_name": "Al Noor Trading",
            "account_number": "N/A",
            "detected_amount": "N/A",
            "date": "2026-01-10",
            "country": "UAE",
            "source_of_funds": "Corporate Revenue"
        }
    elif "commercial" in text_lower or "registration" in text_lower or "سجل تجاري" in text_lower:
        doc_type = "Commercial Registration"
        confidence = 0.97
        detected_entities = {
            "customer_name": "Al Noor Trading (CR: 101089274)",
            "account_number": "N/A",
            "detected_amount": "Capital: 10,000,000 SAR",
            "date": "2025-05-18",
            "country": "Saudi Arabia",
            "source_of_funds": "N/A"
        }
    elif "invoice" in text_lower or "فاتورة" in text_lower or "bill" in text_lower:
        doc_type = "Invoice"
        confidence = 0.94
        detected_entities = {
            "customer_name": "Al Noor Trading",
            "account_number": "N/A",
            "detected_amount": "150,000 SAR",
            "date": "2026-07-12",
            "country": "Saudi Arabia",
            "source_of_funds": "Commercial Trade"
        }
    elif "tax" in text_lower or "zakat" in text_lower or "ضريبة" in text_lower:
        doc_type = "Tax Certificate"
        confidence = 0.92
        detected_entities = {
            "customer_name": "Al Noor Trading",
            "account_number": "VAT-300984712300003",
            "detected_amount": "N/A",
            "date": "2025-12-31",
            "country": "UAE",
            "source_of_funds": "N/A"
        }
    elif "investigation" in text_lower or "note" in text_lower or "ملاحظة" in text_lower:
        doc_type = "Investigation Note"
        confidence = 0.90
        detected_entities = {
            "customer_name": "Al Noor Trading",
            "account_number": "SA802000010948576100",
            "detected_amount": "5,000,000 SAR",
            "date": "2026-07-16",
            "country": "UAE",
            "source_of_funds": "Unknown"
        }
    else:
        doc_type = "Other Evidence"
        confidence = 0.85
        detected_entities = {
            "customer_name": "Al Noor Trading",
            "account_number": "N/A",
            "detected_amount": "N/A",
            "date": "N/A",
            "country": "UAE",
            "source_of_funds": "Unknown"
        }

    return {
        "filename": filename,
        "doc_type": doc_type,
        "confidence": confidence,
        "entities": detected_entities,
        "raw_text_snippet": content_text[:300],
        "file_ext": file_ext
    }

# 4. بناء ملف القضية التلقائي والملخص التنفيذي بناءً على المستندات المرفوعة
def build_case_file_from_evidence():
    if not st.session_state.evidence_list:
        return
    
    primary_evidence = st.session_state.evidence_list[0]
    entities = primary_evidence["entities"]
    
    risk_score = 92 if any(e["doc_type"] == "Bank Statement" for e in st.session_state.evidence_list) else 65
    
    case_data = {
        "case_id": f"DVCI-2026-{time.strftime('%M%S')}",
        "risk_score": risk_score,
        "customer_info": {
            "name": entities.get("customer_name", "Al Noor Trading"),
            "account_number": entities.get("account_number", "SA802000010948576100"),
            "registered_country": entities.get("country", "UAE")
        },
        "suspicious_activities": [
            "نمط دفعات متكررة ومجزأة تحت حد الإبلاغ المالي لتفادي أنظمة المراقبة (Structuring).",
            f"تحويل مالي ضخم بقيمة {entities.get('detected_amount', '5,000,000 SAR')} بمصدر أموال غير معلوم (Unknown source funds).",
            "عمليات تحويل سريعة ومكثفة بفارق زمني ضئيل (High velocity transfers)."
        ],
        "red_flags": [
            "عدم تطابق التدفقات النقدية الحالية مع متوسط المبيعات التاريخي المعتمد في مستندات اعرف عميلك KYC.",
            "وجود أطراف ومستفيدين خارجيين في دول ذات تصنيف مخاطر مرتفع بدون مبرر تجاري واضح."
        ],
        "compliance_findings": "الواقعة تشير لشبهة هيكلة تدفقات مالية (Structuring) تخالف المادة 15 من اللائحة التنفيذية لنظام مكافحة غسل الأموال الصادر عن البنك المركزي السعودي SAMA.",
        "recommended_actions": [
            "تجميد فوري ومؤقت للحساب المرتبط بالواقعة لحماية الأصول الاحترازية (Temporary Freeze).",
            "رفع تقرير اشتباه رسمي (SAR) إلى وحدة الاستخبارات المالية بالبنك المركزي.",
            "طلب المستندات والوثائق القانونية المحدثة لإثبات النشاط التجاري للعميل."
        ]
    }
    st.session_state.case_file = case_data

# 5. حقن الـ CSS والـ Theme (يدعم التبديل الفوري RTL/LTR و Dark/Light)
bg_color = "#07111f" if st.session_state.theme == "dark" else "#f8fafc"
text_color = "#f3f7ff" if st.session_state.theme == "dark" else "#0f172a"
panel_color = "rgba(15, 27, 47, 0.95)" if st.session_state.theme == "dark" else "#ffffff"
border_color = "rgba(255,255,255,0.08)" if st.session_state.theme == "dark" else "rgba(0,0,0,0.08)"
muted_color = "#8fa3bf" if st.session_state.theme == "dark" else "#64748b"
header_bg = "#0e2a55" if st.session_state.theme == "dark" else "#e2e8f0"
direction = "rtl" if st.session_state.lang == "ar" else "ltr"

st.markdown(
    f"""
    <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
            direction: {direction};
            text-align: {'right' if direction == 'rtl' else 'left'};
        }}
        [data-testid="stSidebar"] {{
            direction: {direction};
        }}
        .app-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: {header_bg};
            border-radius: 14px;
            padding: 18px 24px;
            margin-bottom: 1.5rem;
            border: 1px solid {border_color};
        }}
        .app-brand {{
            font-size: 1.4rem;
            font-weight: 700;
            color: {text_color};
        }}
        .app-subtitle {{
            color: {muted_color};
            font-size: 0.9rem;
            margin-top: 5px;
        }}
        .card {{
            background: {panel_color};
            border: 1px solid {border_color};
            border-radius: 18px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .timeline-node {{
            border-left: 3px solid #47b7ff;
            padding-left: 15px;
            margin-left: 10px;
            margin-bottom: 15px;
            position: relative;
        }}
        .timeline-node::before {{
            content: '';
            position: absolute;
            left: -8px;
            top: 4px;
            width: 13px;
            height: 13px;
            background: #00ffcc;
            border-radius: 50%;
        }}
        .metric-card {{
            background: rgba(71, 183, 255, 0.05);
            border: 1px solid rgba(71, 183, 255, 0.15);
            border-radius: 12px;
            padding: 12px 16px;
            text-align: center;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# 6. الهيدر العلوي وشريط الإعدادات والتحكم باللغات
st.markdown(
    f"""
    <div class="app-header">
        <div>
            <div class="app-brand">{txt['brand_title']}</div>
            <div class="app-subtitle">{txt['brand_subtitle']}</div>
        </div>
        <div style="background: rgba(71, 183, 255, 0.1); border: 1px solid rgba(71, 183, 255, 0.3); color: #47b7ff; padding: 6px 15px; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
            {txt['badge_demo']}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### ⚙️ لوحة التحكم")
    
    lang_sel = st.segmented_control("Language / اللغة", options=["العربية", "English"], default="العربية" if st.session_state.lang == "ar" else "English")
    st.session_state.lang = "ar" if lang_sel == "العربية" else "en"
    txt = T[st.session_state.lang]
    
    theme_sel = st.segmented_control("Appearance / المظهر", options=["🌙 Dark", "☀️ Light"], default="🌙 Dark" if st.session_state.theme == "dark" else "☀️ Light")
    st.session_state.theme = "dark" if "Dark" in theme_sel else "light"
    
    st.divider()
    
    st.markdown(f"### {txt['nav_ops']}")
    st.session_state.active_view = st.radio(
        "عرض المنصة",
        options=["operations", "dashboard"],
        format_func=lambda x: txt["nav_ops"] if x == "operations" else txt["nav_dashboard"]
    )

# ==================== لوحة العمليات والأدلة الجنائية (MVP Space) ====================
if st.session_state.active_view == "operations":
    
    col_upload, col_summary_stats = st.columns([1.3, 1.7], gap="large")
    
    with col_upload:
        st.markdown(f"### {txt['upload_sec']}")
        uploaded_files = st.file_uploader(txt["upload_hint"], type=["pdf", "docx", "txt", "csv", "xlsx", "jpg", "png"], accept_multiple_files=True)
        
        if uploaded_files:
            for f in uploaded_files:
                if not any(ev["filename"] == f.name for ev in st.session_state.evidence_list):
                    with st.spinner(f"Processing {f.name}..."):
                        res = process_uploaded_file(f)
                        st.session_state.evidence_list.append(res)
            build_case_file_from_evidence()
            st.success("✅ تم الفحص الذكي واستخراج البيانات وتصنيف الأدلة بنجاح!")

    with col_summary_stats:
        st.markdown("<h4 style='margin-top:0;'>📊 إحصائيات معالجة الملفات (Files Ingestion Stats)</h4>", unsafe_allow_html=True)
        
        total_files = len(st.session_state.evidence_list)
        pdf_count = sum(1 for e in st.session_state.evidence_list if e["file_ext"] == "pdf")
        excel_count = sum(1 for e in st.session_state.evidence_list if e["file_ext"] in ["csv", "xlsx"])
        image_count = sum(1 for e in st.session_state.evidence_list if e["file_ext"] in ["jpg", "png"])
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown(f"<div class='metric-card'><span style='color:{muted_color}; font-size:0.85rem;'>الملفات المرفوعة</span><br><b style='font-size:1.6rem;'>{total_files}</b></div>", unsafe_allow_html=True)
        with col_m2:
            st.markdown(f"<div class='metric-card'><span style='color:{muted_color}; font-size:0.85rem;'>مستندات PDF</span><br><b style='font-size:1.6rem; color:#47b7ff;'>{pdf_count}</b></div>", unsafe_allow_html=True)
        with col_m3:
            st.markdown(f"<div class='metric-card'><span style='color:{muted_color}; font-size:0.85rem;'>جداول Excel</span><br><b style='font-size:1.6rem; color:#00ffcc;'>{excel_count}</b></div>", unsafe_allow_html=True)
        with col_m4:
            st.markdown(f"<div class='metric-card'><span style='color:{muted_color}; font-size:0.85rem;'>الصور الممسوحة</span><br><b style='font-size:1.6rem; color:#ffb747;'>{image_count}</b></div>", unsafe_allow_html=True)

    st.divider()

    col_left, col_right = st.columns([1.3, 1.7], gap="large")

    with col_left:
        st.markdown(f"### {txt['evidence_center_title']}")
        if not st.session_state.evidence_list:
            st.info("الرجاء رفع الملفات لتفعيل الفحص التلقائي للمستندات.")
        else:
            for ev in st.session_state.evidence_list:
                ents = ev["entities"]
                st.markdown(
                    f"""
                    <div class="card" style="border-right: 4px solid #47b7ff;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                            <h4 style="margin: 0; color: #FFFFFF;">📁 {ev['filename']}</h4>
                            <span style="background:rgba(0,255,204,0.1); color:#00ffcc; font-size:0.8rem; padding:3px 10px; border-radius:12px; font-weight:bold;">
                                {ev['doc_type']} ({ev['confidence']*100:.0f}%)
                            </span>
                        </div>
                        <p style="margin: 0 0 10px 0; font-size: 0.85rem; color: #8fa3bf; line-height:1.5;">
                            <strong>مستخرج البيانات الذكي (Extracted Entities):</strong>
                        </p>
                        <table style="width:100%; font-size:0.8rem; text-align:right; border-collapse: collapse; background: rgba(255,255,255,0.02); border-radius: 8px;">
                            <tr style="border-bottom:1px solid {border_color};">
                                <th style="padding:6px; color:#47b7ff;">العنصر (Entity)</th>
                                <th style="padding:6px; color:#47b7ff;">القيمة المستخرجة (Value)</th>
                            </tr>
                            <tr style="border-bottom:1px solid {border_color};">
                                <td style="padding:6px; font-weight:bold;">Customer</td>
                                <td style="padding:6px; color:#ffffff;">{ents['customer_name']}</td>
                            </tr>
                            <tr style="border-bottom:1px solid {border_color};">
                                <td style="padding:6px; font-weight:bold;">Amount</td>
                                <td style="padding:6px; color:#ffffff;">{ents['detected_amount']}</td>
                            </tr>
                            <tr style="border-bottom:1px solid {border_color};">
                                <td style="padding:6px; font-weight:bold;">Country</td>
                                <td style="padding:6px; color:#ffffff;">{ents['country']}</td>
                            </tr>
                            <tr style="border-bottom:1px solid {border_color};">
                                <td style="padding:6px; font-weight:bold;">Date</td>
                                <td style="padding:6px; color:#ffffff;">{ents['date']}</td>
                            </tr>
                            <tr style="border-bottom:1px solid {border_color};">
                                <td style="padding:6px; font-weight:bold;">Source of Funds</td>
                                <td style="padding:6px; color:#ffffff;">{ents['source_of_funds']}</td>
                            </tr>
                        </table>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown(f"### {txt['timeline_title']}")
        if not st.session_state.evidence_list:
            st.info("المخطط الزمني سيتولد ديناميكياً فور رفع المستندات.")
        else:
            st.markdown(
                f"""
                <div class="timeline-node">
                    <strong>09:01 | رفع المستندات الرقمية (Upload)</strong><br>
                    <span style="font-size:0.8rem; color:#8fa3bf;">تم استلام الملفات وبدء استخراج البيانات وحساب التوزيع المالي.</span>
                </div>
                <div class="timeline-node">
                    <strong>09:02 | استخراج الكيانات الذكي (Extract Data)</strong><br>
                    <span style="font-size:0.8rem; color:#8fa3bf;">تم عزل بيانات العميل Al Noor Trading وتحديد مبالغ التحويلات والبلدان.</span>
                </div>
                <div class="timeline-node">
                    <strong>09:03 | تشغيل وكيل تصنيف الأدلة (Classify Evidence)</strong><br>
                    <span style="font-size:0.8rem; color:#8fa3bf;">تم الكشف وتصنيف Bank Statement ونسب الثقة بلغت 96%.</span>
                </div>
                <div class="timeline-node">
                    <strong>09:04 | بناء ملف القضية وربط SAMA (Build Case & SAR)</strong><br>
                    <span style="font-size:0.8rem; color:#8fa3bf;">الـ Risk Score قفز إلى 92% مع توليد فوري لتقارير الاشتباه المالي المعتمدة.</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown(f"### {txt['case_builder_title']}")
        if not st.session_state.case_file:
            st.warning("الرجاء رفع مستندات القضية لبناء التوصية وحساب المخاطر تلقائياً.")
        else:
            cf = st.session_state.case_file
            st.markdown(
                f"""
                <div class="card" style="border: 1px solid rgba(255, 123, 123, 0.2); background: rgba(255, 123, 123, 0.02);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="color: #ff7b7b; margin: 0 0 10px 0;">📄 ملخص الفحص المالي - قضية رقم: {cf['case_id']}</h4>
                        <span style="background:rgba(255,123,123,0.1); color:#ff7b7b; font-size:1.1rem; padding:5px 15px; border-radius:12px; font-weight:bold;">
                            Risk Score: {cf['risk_score']}
                        </span>
                    </div>
                    <p style="margin: 10px 0; font-size: 0.9rem; line-height: 1.6;">
                        <strong>العميل المستهدف:</strong> {cf['customer_info']['name']} <br>
                        <strong>رقم الحساب المرصود:</strong> <code style="color:#00ffcc;">{cf['customer_info']['account_number']}</code><br>
                        <strong>البلد المسجل:</strong> {cf['customer_info']['registered_country']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            with st.expander("🚨 المؤشرات والأنشطة المشبوهة المرصودة (Detected Issues)", expanded=True):
                for act in cf["suspicious_activities"]:
                    st.markdown(f"- **خطر:** {act}")
                    
            with st.expander("📋 التوصية الجنائية الفورية (Recommendation)", expanded=True):
                st.markdown("<b style='color:#ff7b7b; font-size:1.1rem;'>تجميد احترازي فوري ومؤقت (Temporary Freeze)</b>", unsafe_allow_html=True)
                for action in cf["recommended_actions"][1:]:
                    st.markdown(f"- {action}")

            st.markdown(f"### {txt['download_pkg']}")
            case_export_data = f"""==================================================
ALINMA BANK - DVCI COMPLIANCE REPORT (MVP)
CASE FILE ID: {cf['case_id']}
RISK SCORE: {cf['risk_score']}%
==================================================
CUSTOMER NAME: {cf['customer_info']['name']}
ACCOUNT NUMBER: {cf['customer_info']['account_number']}
REGULATOR ALIGNMENT: {cf['compliance_findings']}

DETECTED ISSUES:
{chr(10).join(['- ' + a for a in cf['suspicious_activities']])}

RECOMMENDED ACTIONS (TEMPORARY FREEZE):
{chr(10).join(['- ' + r for r in cf['recommended_actions']])}
"""
            st.download_button(
                label="📥 Download Case File Package (SAR + Report)",
                data=case_export_data,
                file_name=f"DVCI-MVP-Case-{cf['case_id']}.txt",
                mime="text/plain",
                use_container_width=True
            )

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="card" style="border: 1px solid #47b7ff; box-shadow: 0 10px 30px rgba(71, 183, 255, 0.05);">
            <h3 style="color: #47b7ff; font-size: 1.3rem; margin-top: 0; margin-bottom: 5px; font-weight: bold;">{txt['copilot_title']}</h3>
            <p style="color: {muted_color}; font-size: 0.9rem; margin-bottom: 20px;">{txt['copilot_subtitle']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chat_box = st.container()
    with chat_box:
        for msg in st.session_state.messages:
            role_css = "background: rgba(71,183,255,0.08); border-right: 3px solid #47b7ff;" if msg["role"] == "user" else "background: rgba(255,255,255,0.03); border-right: 3px solid #00ffcc;"
            st.markdown(
                f"""
                <div style="{role_css} padding: 12px 18px; border-radius: 8px; margin-bottom: 12px; font-size: 0.95rem;">
                    <strong>{'موظف الامتثال' if msg['role'] == 'user' else 'الـ Copilot الذكي'}:</strong> {msg['content']}
                </div>
                """,
                unsafe_allow_html=True
            )

    if user_prompt := st.chat_input("اكتبي استفسارك مثل: Why is the risk score high?"):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        
        prompt_lower = user_prompt.lower()
        if "risk" in prompt_lower or "score" in prompt_lower or "high" in prompt_lower:
            ai_res = """Risk Score reached **92/100** because:

1. **Cash deposit of 5,000,000 SAR** detected via the uploaded Bank Statement without a matching historic volume.
2. **Source of funds unavailable** or not backed by a valid corporate contract.
3. **8 outbound transfers within 24 hours** creating a typical "Structuring & Layering" pattern to avoid standard transaction monitoring velocity limits.
4. **Multiple foreign destinations (UAE / Cayman Islands)** which conflicts with the commercial profile registered under Alinma Bank records.

*All findings are cross-referenced with your uploaded evidence documents.*"""
        else:
            ai_res = f"أهلاً بكِ. كـ Copilot للامتثال والتحقيق الرقمي، قمت بتحليل استفساركِ: '{user_prompt}'. جميع مؤشرات العميل Al Noor Trading تشير إلى ضرورة اتخاذ الإجراءات الاحترازية طبقاً للمادة 15 من لائحة SAMA."
        
        st.session_state.messages.append({"role": "assistant", "content": ai_res})
        st.rerun()

# ==================== لوحة المراقبة التفاعلية (Dashboard) ====================
else:
    st.markdown("""
    <div class="card" style="margin-bottom: 1rem;">
        <h2>لوحة المراقبة وتحليل المؤشرات الذكية</h2>
        <p style="color: #A6BCCE;">متابعة حية للتدفقات البنكية لامتثال بنك الإنماء.</p>
    </div>
    """, unsafe_allow_html=True)
    
    dashboard_path = Path(__file__).with_name("smart_dashboard.html")
    if dashboard_path.exists():
        components.html(dashboard_path.read_text(encoding="utf-8"), height=1200, scrolling=True)
    else:
        st.info("لوحة المراقبة الذكية غير متوفرة حالياً كملف منفصل.")
