from __future__ import annotations

from datetime import date, timedelta
from html import escape

import streamlit as st

from treatment_rules import ScheduledRule, calculate_guide


st.set_page_config(
    page_title="자동차사고 한방치료 안내",
    layout="wide",
)


def fmt(value: date) -> str:
    return value.strftime("%Y.%m.%d")


def fmt_period(item: ScheduledRule) -> str:
    end = fmt(item.end_date) if item.end_date else "이후 계속"
    return f"{fmt(item.start_date)} - {end}"


def schedule_rows(items: list[ScheduledRule]) -> str:
    rows: list[str] = []
    for item in items:
        cls = "current" if item.is_current else ""
        marker = '<span class="badge">현재</span>' if item.is_current else ""
        rows.append(
            f'<tr class="{cls}"><td>{fmt_period(item)}</td>'
            f"<td>{escape(item.frequency)}{marker}</td></tr>"
        )
    return "".join(rows)


def report_html(
    patient_name: str,
    birth_date: date,
    accident_date: date,
    initial_visit_date: date,
    reference_date: date,
) -> str:
    result = calculate_guide(accident_date, initial_visit_date, reference_date)
    ict = result["ict"]
    safe_name = escape(patient_name.strip() or "환자 성명 미입력")

    return f"""
    <section class="print-sheet">
      <div class="title-row">
        <div>
          <p class="eyebrow">AUTO ACCIDENT CARE GUIDE</p>
          <h1>한방치료 이용 안내서</h1>
          <p class="subtitle">사고 이후 치료 가능 빈도와 산정 기준을 한눈에 확인하세요.</p>
        </div>
        <div class="reference">
          <span>안내 기준일</span>
          <strong>{fmt(reference_date)}</strong>
          <small>수상 {result["injury_day"]}일차</small>
        </div>
      </div>

      <div class="patient-card">
        <div><span>성명</span><strong>{safe_name}</strong></div>
        <div><span>생년월일</span><strong>{fmt(birth_date)}</strong></div>
        <div><span>사고일</span><strong>{fmt(accident_date)}</strong></div>
        <div><span>초진일</span><strong>{fmt(initial_visit_date)}</strong></div>
      </div>

      <div class="section-title">
        <h2>내원 및 치료 횟수 안내</h2>
        <p>강조된 행은 기준일에 해당하는 구간입니다.</p>
      </div>

      <div class="status-grid">
        <article><label>내원 / 추나요법</label><strong>{result["visit_chuna_current"]}</strong><small>추나요법 최대 20회</small></article>
        <article><label>약침술</label><strong>{result["pharmacopuncture_current"]}</strong><small>사고일 기준</small></article>
        <article><label>자락관법</label><strong>{result["cupping_current"]}</strong><small>초진일 기준 · {result["visit_day"]}일차</small></article>
      </div>

      <div class="rules-grid">
        <div class="rule-panel">
          <h3>내원 / 추나요법 <em>사고일 기준</em></h3>
          <table><tbody>{schedule_rows(result["visit_chuna_schedule"])}</tbody></table>
        </div>
        <div class="rule-panel">
          <h3>약침술 <em>사고일 기준</em></h3>
          <table><tbody>{schedule_rows(result["pharmacopuncture_schedule"])}</tbody></table>
        </div>
        <div class="rule-panel ict">
          <h3>ICT <em>사고일 기준</em></h3>
          <p class="phase">{escape(str(ict["phase"]))}</p>
          <div class="ict-row"><span>외래</span><b>{escape(str(ict["outpatient"]))}</b></div>
          <div class="ict-row"><span>입원</span><b>{escape(str(ict["inpatient"]))}</b></div>
          <p class="mini">1-17일: 외래 1회/2부위, 입원 2회/2부위<br>18일 이후: 외래 1회/1부위, 입원 2회/1부위</p>
        </div>
        <div class="rule-panel">
          <h3>자락관법 <em>초진일 기준</em></h3>
          <table><tbody>{schedule_rows(result["cupping_schedule"])}</tbody></table>
        </div>
      </div>

      <div class="notice">
        <strong>확인 사항</strong>
        <p>이 안내서는 입력한 날짜를 기준으로 가능한 치료 빈도와 일일 산정 범위를 보여주는 참고자료입니다. 실제 치료 시행 여부, 환자 상태, 진료기록 및 보험 심사 결과에 따라 인정 내용은 달라질 수 있습니다.</p>
      </div>
      <footer>
        <span>ICT 근거: 건강보험심사평가원, 자동차보험진료수가에 관한 기준·심사지침(2023년 12월판, 2024.01.01 진료분부터 적용)</span>
        <span>내원·추나·약침·자락관법 구간: 기관 운영 설정값 / 배포 전 최신 기준 검토 필요</span>
      </footer>
    </section>
    """


CSS = """
<style>
:root {
  --ink: #11273a;
  --muted: #617181;
  --navy: #11354a;
  --teal: #077d75;
  --mist: #eef5f4;
  --line: #d8e3e2;
  --active: #e2f4ef;
  --warm: #faf8f2;
}
[data-testid="stAppViewContainer"] { background: #f1f5f5; }
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1160px; padding: 1.2rem 1.6rem 2rem; }
.input-help { color: #617181; font-size: .88rem; line-height: 1.5; }
.print-button {
  border: 0; border-radius: 8px; padding: .7rem 1.1rem; cursor: pointer;
  color: white; background: #077d75; font-size: .95rem; font-weight: 700;
  margin-bottom: .85rem;
}
.print-sheet {
  box-sizing: border-box; width: 210mm; min-height: 276mm; margin: 0 auto;
  padding: 13mm 14mm 11mm; background: white; color: var(--ink);
  box-shadow: 0 8px 32px rgba(17, 39, 58, .10);
  font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
}
.title-row { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 3px solid var(--navy); padding-bottom: 5mm; }
.eyebrow { color: var(--teal); letter-spacing: .16em; font-size: 9px; font-weight: 700; margin: 0 0 5px; }
h1 { color: var(--navy); font-size: 27px; letter-spacing: -.06em; margin: 0 0 5px; }
.subtitle { color: var(--muted); font-size: 11px; margin: 0; }
.reference { text-align: right; background: var(--mist); border-radius: 12px; padding: 11px 13px; min-width: 124px; }
.reference span, .reference small { display: block; color: var(--muted); font-size: 10px; }
.reference strong { display: block; color: var(--navy); font-size: 17px; margin: 4px 0; }
.patient-card { display: grid; grid-template-columns: repeat(4, 1fr); border: 1px solid var(--line); border-radius: 12px; margin-top: 6mm; overflow: hidden; }
.patient-card div { padding: 12px 13px; border-right: 1px solid var(--line); }
.patient-card div:last-child { border-right: 0; }
.patient-card span { display: block; color: var(--muted); font-size: 10px; margin-bottom: 5px; }
.patient-card strong { font-size: 13px; }
.section-title { display: flex; align-items: baseline; justify-content: space-between; margin: 8mm 0 3mm; }
.section-title h2 { font-size: 17px; margin: 0; letter-spacing: -.04em; }
.section-title p { color: var(--muted); font-size: 10px; margin: 0; }
.status-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.status-grid article { background: var(--navy); border-radius: 10px; color: white; min-height: 66px; padding: 10px 12px; }
.status-grid label { color: #bdcecf; display: block; font-size: 10px; margin-bottom: 5px; }
.status-grid strong { display: block; font-size: 15px; }
.status-grid small { color: #c9dbd9; font-size: 9px; }
.rules-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 9px; margin-top: 9px; }
.rule-panel { border: 1px solid var(--line); border-radius: 10px; padding: 10px; }
.rule-panel h3 { font-size: 12px; margin: 0 0 8px; color: var(--navy); }
.rule-panel h3 em { font-style: normal; color: var(--teal); float: right; font-size: 10px; }
table { border-collapse: collapse; width: 100%; font-size: 10px; }
td { border-top: 1px solid #e9efee; padding: 5px 4px; }
td:last-child { font-weight: 700; text-align: right; white-space: nowrap; }
tr.current { background: var(--active); color: #085b56; }
.badge { background: var(--teal); border-radius: 9px; color: white; font-size: 8px; margin-left: 5px; padding: 2px 5px; }
.phase { background: var(--active); border-radius: 7px; color: #075b55; font-size: 11px; font-weight: bold; margin: 0 0 7px; padding: 6px 8px; }
.ict-row { align-items: center; border-top: 1px solid #e9efee; display: flex; justify-content: space-between; font-size: 10px; padding: 5px 4px; }
.ict-row span { color: var(--muted); }
.mini { color: var(--muted); font-size: 9px; line-height: 1.55; margin: 7px 3px 0; }
.notice { background: var(--warm); border-left: 3px solid #c79d42; border-radius: 7px; display: flex; gap: 12px; margin-top: 9px; padding: 9px 11px; }
.notice strong { color: #6e5116; flex-shrink: 0; font-size: 11px; }
.notice p { color: #5c5660; font-size: 9.5px; line-height: 1.55; margin: 0; }
footer { border-top: 1px solid var(--line); color: var(--muted); display: flex; flex-direction: column; font-size: 8.5px; gap: 3px; line-height: 1.45; margin-top: 10px; padding-top: 8px; }
@media screen and (max-width: 940px) {
  .print-sheet { height: auto; min-height: unset; width: 100%; padding: 24px; }
  .patient-card, .status-grid, .rules-grid { grid-template-columns: 1fr; }
}
@page { size: A4 portrait; margin: 0; }
@media print {
  [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"],
  [data-testid="stDecoration"], .print-button, .input-help { display: none !important; }
  [data-testid="stAppViewContainer"], .main, .block-container {
    background: white !important; margin: 0 !important; padding: 0 !important; width: 210mm !important;
  }
  .print-sheet {
    box-shadow: none; height: 297mm; min-height: 297mm; margin: 0; overflow: hidden;
    page-break-after: avoid; page-break-inside: avoid;
  }
}
</style>
"""


st.markdown(CSS, unsafe_allow_html=True)

today = date.today()
with st.sidebar:
    st.header("안내서 입력")
    patient_name = st.text_input("성명", placeholder="홍길동")
    birth_date = st.date_input("생년월일", value=date(1990, 1, 1), max_value=today)
    accident_date = st.date_input("사고일", value=today - timedelta(days=10), max_value=today)
    initial_visit_date = st.date_input("초진일", value=today - timedelta(days=9), max_value=today)
    reference_date = st.date_input("안내 기준일", value=today, max_value=today)
    st.caption("기준일에 적용되는 치료 가능 빈도와 ICT 일일 기준을 계산합니다.")
    st.divider()
    st.markdown(
        """
        **계산 기준**

        - 내원/추나요법, 약침술, ICT: 사고일 기준
        - 자락관법: 초진일 기준
        - 추나요법: 최대 20회 안내 표시
        """
    )

st.markdown(
    '<button class="print-button" onclick="window.print()">A4 인쇄 / PDF 저장</button>',
    unsafe_allow_html=True,
)

try:
    html = report_html(
        patient_name, birth_date, accident_date, initial_visit_date, reference_date
    )
except ValueError as exc:
    st.error(str(exc))
    st.info("사고일, 초진일, 안내 기준일을 다시 확인해 주세요.")
else:
    st.markdown(html, unsafe_allow_html=True)
