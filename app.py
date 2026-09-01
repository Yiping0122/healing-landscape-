from __future__ import annotations

import math
import time

import numpy as np
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Healing Landscape Digital Twin",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

GREEN = "#507D69"
INK = "#17352D"
MUTED = "#668078"
CORAL = "#D87F68"
PAPER = "#F7F6EF"

PRESETS = {
    1: dict(sdnn=62, bpm=70, qtc=410, lfhf=1.1),
    2: dict(sdnn=47, bpm=85, qtc=430, lfhf=2.0),
    3: dict(sdnn=36, bpm=95, qtc=450, lfhf=3.2),
    4: dict(sdnn=25, bpm=105, qtc=470, lfhf=5.0),
    5: dict(sdnn=17, bpm=115, qtc=490, lfhf=7.0),
}
LEVEL_NAMES = {1: "Normal", 2: "Mild Stress", 3: "Moderate Stress", 4: "High Stress", 5: "Extreme Stress"}
RECOMMENDED = {1: "Personal", 2: "Room", 3: "Room", 4: "Building", 5: "Room"}
SCALE_TIME = {"Personal": "< 5 s", "Room": "15–30 s", "Building": "1–5 min", "Landscape": "5–15 min"}
INTERVENTIONS = {
    1: "Baseline monitoring",
    2: "Low-intensity restoration",
    3: "Recovery–escalation review",
    4: "Cooling and sensory refuge",
    5: "Protective Recovery / Active Support",
}
ENVIRONMENT = {
    1: "Stable restorative context",
    2: "Moderate thermal / acoustic exposure",
    3: "Elevated combined exposure",
    4: "High thermal / acoustic exposure",
    5: "Extreme combined exposure scenario",
}
THEORY = {
    1: "Homeostatic Maintenance",
    2: "Stress Recovery Theory",
    3: "Attention Restoration Theory",
    4: "Healing-environment support",
    5: "Protective Recovery Principle",
}
STEPS = ["Sense", "Represent", "Infer", "Explain", "Map", "Review", "Update"]
QUESTIONS = [
    "What is being sensed?",
    "How is the physical situation represented digitally?",
    "What state does the AI infer?",
    "Why did the model make this prediction?",
    "What environmental response follows?",
    "Should the recommendation be accepted or modified?",
    "What changes after the intervention?",
]


def initialise() -> None:
    defaults = {
        "stage": 0,
        "preset": 1,
        "sdnn": 62,
        "bpm": 70,
        "qtc": 410,
        "lfhf": 1.1,
        "scale": "Personal",
        "decision": "Pending",
        "feedback": "Not started",
        "action": INTERVENTIONS[1],
        "intensity": "Low",
        "pathway": "A",
        "modified": False,
        "last_level": 1,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def score() -> float:
    s = (
        (70 - st.session_state.sdnn) / 55
        + (st.session_state.bpm - 55) / 65
        + (st.session_state.qtc - 390) / 110
        + (st.session_state.lfhf - 0.5) / 7.5
    ) / 4
    return max(0.0, min(1.0, s))


def level_from_score(value: float) -> int:
    return min(5, int(value / 0.2) + 1)


def reset_decision() -> None:
    st.session_state.decision = "Pending"
    st.session_state.feedback = "Not started"
    st.session_state.modified = False


def apply_preset(level: int) -> None:
    for key, value in PRESETS[level].items():
        st.session_state[key] = value
    st.session_state.preset = level
    st.session_state.scale = RECOMMENDED[level]
    st.session_state.action = INTERVENTIONS[level]
    st.session_state.intensity = "High" if level >= 4 else "Moderate" if level >= 2 else "Low"
    st.session_state.last_level = level
    reset_decision()


def sync_level_state(level: int) -> None:
    """Keep every view aligned when physiology crosses an operational level."""
    if st.session_state.last_level == level:
        return
    st.session_state.action = INTERVENTIONS[level]
    st.session_state.scale = RECOMMENDED[level]
    st.session_state.intensity = "High" if level >= 4 else "Moderate" if level >= 2 else "Low"
    st.session_state.last_level = level
    reset_decision()


def response_summary(level: int) -> str:
    if level == 5:
        return "Context-dependent · Personal/Room immediate → Building/Landscape escalation"
    scale = RECOMMENDED[level]
    return f"{scale} · {SCALE_TIME[scale]}"


def represented_spatial_state(level: int) -> str:
    if level == 3 and st.session_state.decision == "Pending":
        return "Room-scale intervention context"
    if level == 5:
        return f"{st.session_state.scale} immediate layer · context-dependent escalation"
    return f"{st.session_state.scale} layer selected"


def represented_intervention_state(level: int) -> str:
    if st.session_state.decision == "Monitor Only":
        return "No intervention · monitoring"
    if st.session_state.decision == "Pending":
        if level == 3:
            return "Recovery–escalation review pending"
        return f"{st.session_state.action} pending"
    return st.session_state.action


def goto(index: int) -> None:
    st.session_state.stage = index


def card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f'<div class="metric-card"><span>{label}</span><strong>{value}</strong><small>{note}</small></div>',
        unsafe_allow_html=True,
    )


def ecg_figure(bpm: int, sdnn: int, qtc: int) -> go.Figure:
    duration, fs = 8.0, 250
    t = np.linspace(0, duration, int(duration * fs))
    signal = np.zeros_like(t)
    rr = 60 / bpm
    beats, current, i = [], 0.5, 0
    while current < duration:
        beats.append(current)
        current += rr + math.sin(i * 2.17) * (sdnn / 1000) * 0.35
        i += 1
    stretch = (qtc - 390) / 110
    for beat in beats:
        signal += 0.08 * np.exp(-((t - (beat - 0.18)) / 0.035) ** 2)
        signal -= 0.12 * np.exp(-((t - (beat - 0.035)) / 0.012) ** 2)
        signal += 1.05 * np.exp(-((t - beat) / 0.014) ** 2)
        signal -= 0.22 * np.exp(-((t - (beat + 0.035)) / 0.018) ** 2)
        signal += 0.25 * np.exp(-((t - (beat + 0.24 + 0.07 * stretch)) / (0.07 + 0.02 * stretch)) ** 2)
    fig = go.Figure(go.Scatter(x=t, y=signal, mode="lines", line=dict(color=GREEN, width=2)))
    fig.update_layout(
        height=275,
        margin=dict(l=8, r=8, t=8, b=20),
        paper_bgcolor="#F0F4F1",
        plot_bgcolor="#F0F4F1",
        xaxis=dict(title="Simulated time (s)", gridcolor="#D9E4DE", zeroline=False),
        yaxis=dict(visible=False, range=[-0.35, 1.2]),
        showlegend=False,
    )
    return fig


def scene_html(level: int, scale: str, updated: bool = False) -> str:
    intensity = ["", "baseline", "mild", "moderate", "high", "extreme"][level]
    return f"""
    <div class="scene {intensity}">
      <div class="scene-label">{scale.upper()} LAYER · {'TWIN UPDATED' if updated else 'SIMULATED'}</div>
      <div class="sun"></div><div class="building"><div class="window">GREEN VIEW</div><div class="vent">AIRFLOW</div></div>
      <div class="person"><i></i><b></b><span>HRV</span></div>
      <div class="tree"><i></i><b></b></div><div class="water">restorative water</div>
      <div class="shade">SHADE ↑</div><div class="route">lower-exposure pathway</div>
    </div>"""


CSS = """
<style>
.stApp { background:#F7F6EF; color:#17352D; }
.block-container { max-width:1500px; padding-top:1.3rem; padding-bottom:2rem; }
h1,h2,h3 { color:#17352D; letter-spacing:-.025em; }
[data-testid="stSidebar"] { background:#FFFEFA; border-right:1px solid #D9E4DE; }
.eyebrow { color:#507D69; font-size:.72rem; font-weight:800; letter-spacing:.14em; margin-bottom:.2rem; }
.boundary { display:inline-block; background:#E3EEE7; border:1px solid #C8DDD1; color:#315F50; padding:.45rem .75rem; border-radius:999px; font-size:.76rem; }
.live { display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:#D9E4DE; border:1px solid #D9E4DE; margin:.8rem 0 1rem; }
.live div { background:#FFFEFA; padding:.65rem .85rem; } .live span,.metric-card span { display:block;color:#668078;font-size:.72rem;text-transform:uppercase;letter-spacing:.06em; }
.live strong { display:block;font-size:1.05rem;margin:.15rem 0; } .live small,.metric-card small { color:#668078;font-size:.7rem; }
.metric-card { min-height:104px;background:#F0F4F1;border:1px solid #D9E4DE;padding:1rem;margin:.25rem 0; }
.metric-card strong { display:block;font-size:1.25rem;margin:.45rem 0;color:#17352D; }
.state-row { border-bottom:1px solid #D9E4DE;padding:.85rem .2rem;display:grid;grid-template-columns:190px 1fr;gap:1rem; }
.state-row span { color:#668078; }.state-row strong { color:#17352D; }
.callout { border-left:4px solid #D87F68;background:#FFF0EB;padding:1rem 1.2rem;margin:.7rem 0; }
.success-callout { border-left-color:#507D69;background:#E3EEE7; }
.chain { display:flex;align-items:center;justify-content:center;gap:.7rem;background:#FFFEFA;border:1px solid #D9E4DE;padding:1rem;margin-bottom:1rem;font-weight:700; }
.chain .active { color:#D87F68; }.chain i { color:#8AA297;font-style:normal; }
.response { border:1px solid #D9E4DE;background:#FFFEFA;padding:1.1rem;min-height:240px; }
.response h3 { margin:.1rem 0 .2rem;font-size:1.2rem; }.response small { color:#668078; }.response p { display:flex;justify-content:space-between;border-top:1px solid #E1E9E4;padding:.75rem 0;margin:0; }.response b { color:#507D69; }
.scene {height:355px;position:relative;overflow:hidden;border:1px solid #C9D8D0;background:linear-gradient(#DDECE9 0 50%,#B8C99F 50%);}
.scene-label {position:absolute;z-index:8;top:12px;left:12px;background:#17352D;color:white;padding:7px 10px;font-size:11px;font-weight:700;letter-spacing:.08em;}
.sun {position:absolute;width:58px;height:58px;border-radius:50%;background:#F2DF9F;right:9%;top:12%;box-shadow:0 0 0 16px rgba(242,223,159,.25)}
.building {position:absolute;left:5%;bottom:18%;width:42%;height:50%;background:#F5F1E6;border:3px solid #9EB6AA}.window {position:absolute;right:8%;top:20%;width:34%;height:38%;background:#B9D4C5;display:grid;place-items:center;font-size:10px;color:#315F50}.vent {position:absolute;left:10%;top:35%;padding:6px;border:1px solid #8AA297;font-size:9px}
.person {position:absolute;left:34%;bottom:16%;width:45px;height:112px;z-index:4}.person i {position:absolute;width:27px;height:27px;border-radius:50%;left:9px;background:#B87962}.person b {position:absolute;width:34px;height:70px;border-radius:18px 18px 8px 8px;top:29px;left:5px;background:#54756D}.person span {position:absolute;left:-21px;top:45px;background:white;border:1px solid #D87F68;color:#B55E4A;padding:3px;font-size:9px}
.tree {position:absolute;right:15%;bottom:24%;width:115px;height:165px}.tree i {position:absolute;width:15px;height:90px;background:#796D52;bottom:0;left:50px}.tree b {position:absolute;width:115px;height:100px;border-radius:50%;background:#70977C;top:0}.water {position:absolute;right:3%;bottom:7%;width:31%;height:12%;border-radius:50%;background:#9CC9CD;color:#416970;display:grid;place-items:center;font-size:9px}.shade {position:absolute;right:18%;top:22%;color:#315F50;font-weight:700}.route {position:absolute;right:38%;bottom:5%;color:#6D6252;font-size:10px}.high .sun,.extreme .sun{background:#EFA97F}.high .shade,.extreme .shade{color:#D87F68}.extreme .scene-label{background:#D87F68}
@media(max-width:800px){.live{grid-template-columns:1fr}.state-row{grid-template-columns:1fr}.chain{flex-wrap:wrap}.scene{height:310px}}
</style>
"""


initialise()
st.markdown(CSS, unsafe_allow_html=True)

st.markdown('<div class="eyebrow">ONE EVOLVING STATE · SEVEN DIGITAL-TWIN VIEWS</div>', unsafe_allow_html=True)
title_col, badge_col = st.columns([3, 1])
with title_col:
    st.title("Healing Landscape Digital Twin")
    st.caption("From physiological sensing to multi-scale healing-environment intervention")
with badge_col:
    st.markdown('<div class="boundary">● Offline physiological inference framework</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Physiological State Simulator")
    st.caption("Shared state · interactive demonstration")
    st.markdown("#### Preset stress level")
    preset_cols = st.columns(5)
    for i, col in enumerate(preset_cols, 1):
        if col.button(f"L{i}", use_container_width=True, type="primary" if st.session_state.preset == i else "secondary"):
            apply_preset(i)
            st.rerun()
    st.markdown("#### Manual physiology")
    old = (st.session_state.sdnn, st.session_state.bpm, st.session_state.qtc, st.session_state.lfhf)
    st.slider("SDNN (ms)", 15, 70, key="sdnn")
    st.slider("BPM", 55, 120, key="bpm")
    st.slider("QTc (ms)", 390, 500, key="qtc")
    st.slider("LF/HF", 0.5, 8.0, step=0.1, key="lfhf")
    new = (st.session_state.sdnn, st.session_state.bpm, st.session_state.qtc, st.session_state.lfhf)
    if old != new:
        st.session_state.preset = 0
        reset_decision()
    current_score = score()
    current_level = level_from_score(current_score)
    st.metric("StressScore", f"{current_score:.2f}", help="Demonstration normalised stress-state index")
    st.caption("Not a clinically validated score or diagnosis.")
    if st.button("Reset baseline", use_container_width=True):
        apply_preset(1)
        goto(0)
        st.rerun()

current_score = score()
current_level = level_from_score(current_score)
sync_level_state(current_level)

st.markdown(
    f'<div class="live"><div><span>Live state</span><strong>{current_score:.2f}</strong><small>Demonstration normalised index</small></div>'
    f'<div><span>Operational level</span><strong>Level {current_level} · {LEVEL_NAMES[current_level]}</strong><small>Operational discretisation</small></div>'
    f'<div><span>Decision / feedback</span><strong>{st.session_state.decision} · {st.session_state.feedback}</strong><small>One persistent session state</small></div></div>',
    unsafe_allow_html=True,
)

nav = st.columns(7)
for i, (col, name) in enumerate(zip(nav, STEPS)):
    if col.button(f"{i+1:02d}\n{name}", key=f"nav_{i}", use_container_width=True, type="primary" if st.session_state.stage == i else "secondary"):
        goto(i)
        st.rerun()

stage = st.session_state.stage
st.markdown(f'<div class="eyebrow">{stage+1:02d} · {STEPS[stage].upper()}</div>', unsafe_allow_html=True)
st.header(QUESTIONS[stage])
st.caption(f"Level {current_level} · {LEVEL_NAMES[current_level]}")

if stage == 0:
    left, right = st.columns([2.2, 1])
    with left:
        st.subheader("Physiological sensing")
        st.plotly_chart(ecg_figure(st.session_state.bpm, st.session_state.sdnn, st.session_state.qtc), use_container_width=True, config={"displayModeBar": False})
        cols = st.columns(4)
        vals = [("SDNN", f"{st.session_state.sdnn} ms"), ("BPM", str(st.session_state.bpm)), ("QTc", f"{st.session_state.qtc} ms"), ("LF/HF", f"{st.session_state.lfhf:.1f}")]
        for col, (label, value) in zip(cols, vals):
            with col: card(label, value)
    with right:
        st.subheader("Environmental sensing")
        for label, value in [("Thermal", "High exposure" if current_level > 3 else "Context state"), ("Lighting", "Modulation candidate" if current_level > 1 else "Baseline"), ("Acoustic", "Buffering candidate" if current_level > 2 else "Natural context"), ("Airflow", "Support candidate"), ("Landscape", "Green view · canopy · water")]:
            st.markdown(f'<div class="state-row"><span>{label}</span><strong>{value}</strong></div>', unsafe_allow_html=True)

elif stage == 1:
    st.subheader("Twin State Repository")
    rows = [
        ("Human state", f"Level {current_level} · {LEVEL_NAMES[current_level]}"),
        ("Physiology", f"SDNN {st.session_state.sdnn} · BPM {st.session_state.bpm} · QTc {st.session_state.qtc} · LF/HF {st.session_state.lfhf:.1f}"),
        ("Environment state", ENVIRONMENT[current_level]),
        ("Spatial / asset state", represented_spatial_state(current_level)),
        ("Decision state", st.session_state.decision),
        ("Intervention state", represented_intervention_state(current_level)),
        ("Feedback state", st.session_state.feedback),
    ]
    for label, value in rows:
        st.markdown(f'<div class="state-row"><span>{label}</span><strong>{value}</strong></div>', unsafe_allow_html=True)

elif stage == 2:
    st.markdown('<div class="chain"><span>Feature vector</span><i>→</i><span>Random Forest</span><i>→</i><span>Demonstration index</span><i>→</i><span class="active">Operational class</span></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for col, (label, value) in zip(cols, [("SDNN evidence", f"{st.session_state.sdnn} ms"), ("BPM evidence", str(st.session_state.bpm)), ("QTc evidence", f"{st.session_state.qtc} ms"), ("LF/HF evidence", f"{st.session_state.lfhf:.1f}")]):
        with col: card(label, value)
    st.markdown(f'<div class="callout success-callout"><b>Operational class: Level {current_level} · {LEVEL_NAMES[current_level]}</b><br>Classification provides an operational state for intervention mapping, not a clinical diagnosis.</div>', unsafe_allow_html=True)

elif stage == 3:
    sd = max(0, min(1, (70 - st.session_state.sdnn) / 55))
    drivers = {"rel_SDNN": sd, "ecg_SDNN": sd * .82, "BPM": max(0, (st.session_state.bpm - 55) / 65) * .68, "QTc": max(0, (st.session_state.qtc - 390) / 110) * .55, "LF/HF": max(0, (st.session_state.lfhf - .5) / 7.5) * .5}
    chart = go.Figure(go.Bar(x=list(drivers.values()), y=list(drivers.keys()), orientation="h", marker_color=[CORAL] + [GREEN] * 4))
    chart.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), xaxis=dict(visible=False, range=[0, 1]), yaxis=dict(autorange="reversed"), paper_bgcolor=PAPER, plot_bgcolor=PAPER)
    left, right = st.columns([1.4, 1])
    with left: st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})
    with right:
        st.markdown(f'<div class="callout"><b>Leading feature: rel_SDNN</b><br><br>Reduced SDNN relative to baseline is the dominant driver of the current Level {current_level} representation. BPM, QTc and LF/HF provide supporting context.<br><br><small>Deterministic display based on the manuscript model logic.</small></div>', unsafe_allow_html=True)

elif stage == 4:
    recommended = RECOMMENDED[current_level]
    if current_level == 5:
        st.info("Recommended strategy: **Protect first → context-dependent environmental escalation**")
        immediate, escalation = st.columns(2)
        with immediate:
            st.markdown('<div class="callout"><b>1 · Immediate protective response</b><br>Personal cooling · reduce immediate thermal/acoustic exposure · move to a shaded or quiet retreat · occupancy advisory · high-priority human review</div>', unsafe_allow_html=True)
        with escalation:
            st.markdown('<div class="callout success-callout"><b>2 · Environmental escalation</b><br>Room airflow/acoustic buffering → Building HVAC/zone control → Landscape shade, water, refuge and lower-exposure pathway, according to context</div>', unsafe_allow_html=True)
    else:
        st.info(f"Recommended scale: **{recommended} · {SCALE_TIME[recommended]}**")
        if current_level == 3:
            st.caption("Level 3 is a decision boundary rather than a fixed intervention state: room-scale moderate restoration proceeds to human review of restorative versus active-support pathways.")
    st.segmented_control("Explore intervention scale", list(SCALE_TIME), key="scale", selection_mode="single")
    if current_level != 5 and st.session_state.scale != recommended:
        st.warning(f"Exploring {st.session_state.scale}; the model recommendation remains {recommended}.")
    elif current_level == 5:
        st.caption("Level 5 determines urgency and intensity; the selected scale represents the current contextual layer, not a fixed severity-to-scale mapping.")
    st.markdown(scene_html(current_level, st.session_state.scale, st.session_state.feedback == "Simulated complete"), unsafe_allow_html=True)
    st.markdown(f'<div class="callout success-callout"><b>{st.session_state.action}</b><br>{st.session_state.scale} response · {st.session_state.intensity} intensity · simulated / protocol-level</div>', unsafe_allow_html=True)

elif stage == 5:
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Current AI recommendation")
        st.markdown(f"### {st.session_state.action}")
        for label, value in [("Current evidence", f"SDNN {st.session_state.sdnn} · BPM {st.session_state.bpm} · QTc {st.session_state.qtc} · LF/HF {st.session_state.lfhf:.1f}"), ("Environmental context", ENVIRONMENT[current_level]), ("Recommended strategy", response_summary(current_level)), ("Current contextual layer", f"{st.session_state.scale} · {st.session_state.intensity} intensity"), ("Rationale", THEORY[current_level]), ("Validation", "Inference validated offline; intervention protocol-level / simulated")]:
            st.markdown(f'<div class="state-row"><span>{label}</span><strong>{value}</strong></div>', unsafe_allow_html=True)
        if current_level == 5:
            st.markdown('<div class="callout"><b>High-priority protective support</b><br>This is an extreme operational stress state, not a medical diagnosis or emergency-treatment recommendation.</div>', unsafe_allow_html=True)
    with right:
        if current_level == 3:
            st.session_state.pathway = st.radio("Recovery–escalation threshold", ["A", "B"], format_func=lambda x: "Path A · Restorative response" if x == "A" else "Path B · Active support", horizontal=True)
        st.subheader("Decision outcomes")
        a, b = st.columns(2)
        if a.button("Approve", use_container_width=True, type="primary"):
            st.session_state.decision, st.session_state.feedback, st.session_state.stage = "Approved", "Not started", 6
            st.rerun()
        if b.button("Modify", use_container_width=True):
            st.session_state.modified = True
        c, d = st.columns(2)
        if c.button("Escalate", use_container_width=True):
            scales = list(SCALE_TIME)
            idx = min(len(scales) - 1, scales.index(st.session_state.scale) + 1)
            st.session_state.scale = scales[idx]
            st.session_state.intensity = "High" if st.session_state.intensity != "Low" else "Moderate"
            st.session_state.decision, st.session_state.feedback, st.session_state.stage = "Escalated", "Not started", 4
            st.rerun()
        if d.button("Monitor Only", use_container_width=True):
            st.session_state.decision, st.session_state.feedback, st.session_state.stage = "Monitor Only", "Monitoring", 6
            st.rerun()
        if st.session_state.modified:
            with st.form("modify_form"):
                st.selectbox("Action", [INTERVENTIONS[current_level], "Restorative micro-setting", "Thermal / airflow adjustment", "Acoustic buffering", "Protected sensory refuge"], key="action")
                st.selectbox("Scale", list(SCALE_TIME), key="scale")
                st.selectbox("Intensity", ["Low", "Moderate", "High"], key="intensity")
                if st.form_submit_button("Confirm Modified Intervention", type="primary", use_container_width=True):
                    st.session_state.decision, st.session_state.feedback, st.session_state.modified, st.session_state.stage = "Modified", "Not started", False, 6
                    st.rerun()

else:
    decision = st.session_state.decision
    if decision == "Pending":
        st.warning("A review decision is required before intervention simulation.")
        if st.button("Go to Review", type="primary"): goto(5); st.rerun()
    elif decision == "Monitor Only":
        st.markdown('<div class="chain"><span>Monitor Only</span><i>→</i><span class="active">Feedback State: Monitoring</span><i>→</i><span>Await next sensing update</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="callout success-callout"><b>No intervention is initiated.</b><br>The twin preserves the current snapshot and waits for the next sensing update.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="chain"><span>Recommendation Approved</span><i>→</i><span class="active">Intervention Simulation</span><i>→</i><span>Twin State Updated</span></div>', unsafe_allow_html=True)
        complete = st.session_state.feedback == "Simulated complete"
        cols = st.columns(3)
        blocks = [
            ("Human response", [("Stress trajectory", "↓" if complete else "—"), ("SDNN", "Expected ↑" if complete else "Current"), ("BPM", "Expected ↓" if complete else "Current")]),
            ("Environment response", [("Environmental stressor", "Expected ↓" if complete else "Current"), ("Restorative exposure", "Expected ↑" if complete else "Selected"), ("Shade / acoustic quality", "Expected ↑" if complete else "Selected")]),
            ("Twin state", [("Intervention state", "Completed" if complete else "Pending"), ("Feedback state", "Simulated" if complete else "Pending"), ("Twin state", "Updated" if complete else "Current")]),
        ]
        for col, (heading, rows) in zip(cols, blocks):
            with col:
                html = f'<div class="response"><h3>{heading}</h3><small>{"Expected transition" if complete else "Current snapshot"}</small>' + "".join(f'<p><span>{a}</span><b>{b}</b></p>' for a, b in rows) + "</div>"
                st.markdown(html, unsafe_allow_html=True)
        if st.button("Simulate Intervention Response", type="primary", use_container_width=True, disabled=complete):
            with st.spinner("Simulating directional system-state transition…"):
                time.sleep(0.65)
            st.session_state.feedback = "Simulated complete"
            st.rerun()
        st.caption("Directional outcomes only: arrows express expected direction of system change. No individual recovery value, treatment effect, or measured therapeutic outcome is predicted.")

st.divider()
st.caption("Validated: offline ECG processing · HRV extraction · RF classification · SHAP interpretation  |  Protocol-level: intervention mapping · simulated feedback · multi-scale response  |  Not validated: clinical diagnosis · live actuation · measured recovery")
