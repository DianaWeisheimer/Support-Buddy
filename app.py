import requests
import streamlit as st

st.set_page_config(
    page_title="Support Buddy",
    page_icon="🔧",
    layout="wide",
)

API_URL = "http://localhost:8000/api"

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    header[data-testid="stHeader"] { background: transparent; }

    .app-header {
        display: flex; align-items: center; gap: 14px;
        padding-bottom: 1.2rem;
        border-bottom: 1px solid rgba(128,128,128,0.15);
        margin-bottom: 1.5rem;
    }
    .app-logo {
        width: 40px; height: 40px; background: #0F6E56;
        border-radius: 10px; display: flex;
        align-items: center; justify-content: center; font-size: 20px;
    }
    .app-title    { font-size: 20px; font-weight: 600; margin: 0; }
    .app-subtitle { font-size: 13px; opacity: 0.5; margin: 0; }
    .badge {
        font-size: 11px; font-weight: 500;
        background: #E1F5EE; color: #0F6E56;
        padding: 3px 10px; border-radius: 20px; margin-left: auto;
    }
    .result-box {
        border-left: 3px solid #0F6E56;
        background: rgba(15,110,86,0.08);
        padding: 14px 18px; border-radius: 0 8px 8px 0;
        font-size: 14px; line-height: 1.7; margin-top: 0.5rem;
    }
    .result-box-blue {
        border-left: 3px solid #3B82F6;
        background: rgba(59,130,246,0.08);
        padding: 14px 18px; border-radius: 0 8px 8px 0;
        font-size: 14px; line-height: 1.7; margin-top: 0.5rem;
    }
    .case-detail-header {
        background: rgba(15,110,86,0.07);
        border: 1px solid rgba(15,110,86,0.2);
        border-radius: 10px; padding: 16px 20px; margin-bottom: 1.2rem;
    }
    .case-detail-id   { font-size: 12px; font-weight: 600; color: #0F6E56; margin-bottom: 4px; }
    .case-detail-desc { font-size: 15px; font-weight: 500; line-height: 1.5; }
    .section-label {
        font-size: 12px; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.06em; opacity: 0.5; margin-bottom: 8px;
    }
    .step-item {
        display: flex; align-items: flex-start; gap: 10px;
        padding: 9px 12px; border-radius: 8px;
        background: rgba(128,128,128,0.07);
        margin-bottom: 6px; font-size: 14px; line-height: 1.5;
    }
    .step-num {
        font-size: 11px; font-weight: 600; color: #0F6E56;
        min-width: 20px; padding-top: 2px; opacity: 0.8;
    }
    .sidebar-header {
        font-size: 12px; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.06em; opacity: 0.5; margin-bottom: 10px;
    }
    .status-dot {
        display: inline-block; width: 8px; height: 8px;
        border-radius: 50%; margin-right: 6px;
    }
    .status-ok  { background: #22c55e; }
    .status-err { background: #ef4444; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {
    "suggest_result": None,
    "improve_result": None,
    "viewing_case": None,
    "editing": False,
    "new_steps": [],        # steps do formulário de novo case
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ────────────────────────────────────────────────────────────────────
def api_is_online() -> bool:
    try:
        r = requests.get(f"{API_URL.replace('/api', '')}/health", timeout=2)
        return r.status_code == 200
    except Exception:
        return False

def reset_to_new_case():
    st.session_state.viewing_case   = None
    st.session_state.suggest_result = None
    st.session_state.improve_result = None
    st.session_state.editing        = False
    st.session_state.new_steps      = []

def render_steps_list(steps: list[str]):
    """Renderiza a lista de steps numerada, do mais recente ao mais antigo."""
    if not steps:
        st.caption("No steps added yet.")
        return
    for i, step in enumerate(steps):
        st.markdown(
            f'<div class="step-item">'
            f'<span class="step-num">#{i+1}</span>'
            f'<span>{step}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    online = api_is_online()
    st.markdown(
        f'<span class="status-dot {"status-ok" if online else "status-err"}"></span>'
        f'<span style="font-size:13px;opacity:0.6">{"API online" if online else "API offline"}</span>',
        unsafe_allow_html=True,
    )
    st.divider()

    if st.button("＋  New case", use_container_width=True, type="primary"):
        reset_to_new_case()
        st.rerun()

    st.divider()

    st.markdown('<div class="sidebar-header">Saved cases</div>', unsafe_allow_html=True)
    try:
        cases = requests.get(f"{API_URL}/cases", timeout=3).json()
        if not cases:
            st.caption("No cases saved yet.")
        else:
            for case in cases:
                preview = case["case_description"][:55]
                if len(case["case_description"]) > 55:
                    preview += "…"
                if st.button(f"#{case['id']}  {preview}", key=f"case_{case['id']}", use_container_width=True):
                    st.session_state.viewing_case   = case
                    st.session_state.suggest_result = None
                    st.session_state.improve_result = None
                    st.session_state.editing        = False
                    st.rerun()
    except Exception:
        st.caption("Could not load cases.")

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
    <div class="app-header">
        <div class="app-logo">🔧</div>
        <div>
            <div class="app-title">Support Buddy</div>
            <div class="app-subtitle">AI-powered support engineering tool</div>
        </div>
        <span class="badge">SAP / Ariba</span>
    </div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# VIEW A — Case detail
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.viewing_case:
    case = st.session_state.viewing_case
    steps: list[str] = case.get("investigation_steps") or []

    st.markdown(f"""
        <div class="case-detail-header">
            <div class="case-detail-id">CASE #{case['id']}</div>
            <div class="case-detail-desc">{case['case_description']}</div>
        </div>
    """, unsafe_allow_html=True)

    col_title, col_btn = st.columns([6, 1])
    with col_btn:
        edit_label = "Cancel" if st.session_state.editing else "✏️ Edit"
        if st.button(edit_label, use_container_width=True):
            st.session_state.editing = not st.session_state.editing
            st.rerun()

    # ── Modo edição ────────────────────────────────────────────────────────────
    if st.session_state.editing:
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown('<div class="section-label">Investigation steps</div>', unsafe_allow_html=True)
            render_steps_list(steps)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">Add new step</div>', unsafe_allow_html=True)

            new_step_input = st.text_area(
                "new_step_input",
                placeholder="e.g.: Checked cXML payload — error 400 on PO confirmation...",
                height=90,
                label_visibility="collapsed",
                key="edit_step_input",
            )
            if st.button("＋ Add step", key="btn_add_edit"):
                if new_step_input.strip():
                    # Novo step vai pro topo (índice 0) — mais recente primeiro
                    updated_steps = [new_step_input.strip()] + steps
                    with st.spinner("Saving and generating new suggestions..."):
                        try:
                            r = requests.put(
                                f"{API_URL}/cases/{case['id']}",
                                json={
                                    "case_description": case["case_description"],
                                    "investigation_steps": updated_steps,
                                },
                                timeout=30,
                            )
                            r.raise_for_status()
                            updated_case = dict(case)
                            updated_case["investigation_steps"] = updated_steps
                            updated_case["ai_response"] = r.json()["suggestions"]
                            st.session_state.viewing_case = updated_case
                            st.session_state.editing = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Write a step before adding.")

        with col_right:
            st.markdown('<div class="section-label">Current AI response</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-box">{case["ai_response"]}</div>', unsafe_allow_html=True)

    # ── Modo visualização ──────────────────────────────────────────────────────
    else:
        tab_view, tab_msg = st.tabs(["🗒️  Investigation", "✉️  Message improver"])

        with tab_view:
            col_steps, col_ai = st.columns(2)

            with col_steps:
                st.markdown('<div class="section-label">Investigation steps</div>', unsafe_allow_html=True)
                render_steps_list(steps)

            with col_ai:
                st.markdown('<div class="section-label">AI response</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-box">{case["ai_response"]}</div>', unsafe_allow_html=True)

        with tab_msg:
            st.caption("Refine a customer message using this case's full context.")

            tone = st.selectbox(
                "Tone",
                ["Professional & empathetic", "Concise & technical", "Friendly & reassuring", "Formal"],
                key="detail_tone",
            )
            customer_message = st.text_area(
                "Your draft message",
                placeholder="e.g.: Hi, we checked the logs and found an error in the EDI mapping...",
                height=120,
                key="detail_msg_draft",
            )

            if st.button("Improve message →", type="primary", key="btn_improve_detail"):
                if not customer_message.strip():
                    st.warning("Write a draft message first.")
                else:
                    with st.spinner("Improving message..."):
                        try:
                            steps_text = "\n".join(
                                f"{i+1}. {s}" for i, s in enumerate(steps)
                            )
                            r = requests.post(
                                f"{API_URL}/improve",
                                json={
                                    "customer_message": customer_message,
                                    "tone": tone,
                                    "case_description": case["case_description"],
                                    "investigation_steps": steps_text,
                                },
                                timeout=30,
                            )
                            r.raise_for_status()
                            st.session_state.improve_result = r.json()["improved_message"]
                        except Exception as e:
                            st.error(f"Error: {e}")

            if st.session_state.improve_result:
                st.markdown(
                    f'<div class="result-box-blue">{st.session_state.improve_result}</div>',
                    unsafe_allow_html=True,
                )
                st.code(st.session_state.improve_result, language=None)

# ══════════════════════════════════════════════════════════════════════════════
# VIEW B — New case form
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown("#### Case context")

    col1, col2 = st.columns([3, 1])
    with col1:
        case_description = st.text_area(
            "Problem description",
            placeholder="Describe the customer's reported issue...",
            height=110,
            label_visibility="collapsed",
        )
    with col2:
        st.selectbox("Category", ["", "Integration (API/EDI)", "Approval / workflow", "Procurement / PO", "Performance", "Other"])
        st.selectbox("Priority", ["P3 – Medium", "P2 – High", "P1 – Critical", "P4 – Low"])

    # Steps input
    st.markdown("#### Investigation steps")

    col_input, col_btn = st.columns([5, 1])
    with col_input:
        step_input = st.text_input(
            "step_input",
            placeholder="Add a step you've already investigated...",
            label_visibility="collapsed",
            key="new_step_input",
        )
    with col_btn:
        if st.button("＋ Add", use_container_width=True):
            if step_input.strip():
                # Novo step vai pro topo — mais recente primeiro
                st.session_state.new_steps = [step_input.strip()] + st.session_state.new_steps
                st.rerun()
            else:
                st.warning("Write a step first.")

    # Lista de steps adicionados
    if st.session_state.new_steps:
        st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
        for i, step in enumerate(st.session_state.new_steps):
            col_step, col_del = st.columns([10, 1])
            with col_step:
                st.markdown(
                    f'<div class="step-item">'
                    f'<span class="step-num">#{i+1}</span>'
                    f'<span>{step}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with col_del:
                if st.button("✕", key=f"del_{i}", help="Remove step"):
                    st.session_state.new_steps.pop(i)
                    st.rerun()
    else:
        st.caption("No steps added yet.")

    st.divider()

    tab_suggest, tab_improve = st.tabs(["💡  Next steps", "✉️  Message improver"])

    with tab_suggest:
        st.caption("Claude analyzes your case and investigation log to suggest what to do next.")

        if st.button("Suggest next steps →", type="primary", key="btn_suggest"):
            if not case_description.strip():
                st.warning("Fill in the problem description first.")
            else:
                with st.spinner("Analyzing case..."):
                    try:
                        r = requests.post(
                            f"{API_URL}/suggest",
                            json={
                                "case_description": case_description,
                                "investigation_steps": st.session_state.new_steps,
                            },
                            timeout=30,
                        )
                        r.raise_for_status()
                        st.session_state.suggest_result = r.json()["suggestions"]
                    except Exception as e:
                        st.error(f"Error: {e}")

        if st.session_state.suggest_result:
            st.markdown(
                f'<div class="result-box">{st.session_state.suggest_result}</div>',
                unsafe_allow_html=True,
            )

    with tab_improve:
        st.caption("Write a draft reply and Claude will refine it using the case context.")

        st.selectbox("Tone", ["Professional & empathetic", "Concise & technical", "Friendly & reassuring", "Formal"])
        customer_message = st.text_area(
            "Your draft message",
            placeholder="e.g.: Hi, we checked the logs and found an error in the EDI mapping...",
            height=120,
        )

        if st.button("Improve message →", type="primary", key="btn_improve"):
            if not customer_message.strip():
                st.warning("Write a draft message first.")
            else:
                with st.spinner("Improving message..."):
                    try:
                        steps_text = "\n".join(
                            f"{i+1}. {s}" for i, s in enumerate(st.session_state.new_steps)
                        )
                        r = requests.post(
                            f"{API_URL}/improve",
                            json={
                                "customer_message": customer_message,
                                "case_description": case_description,
                                "investigation_steps": steps_text,
                            },
                            timeout=30,
                        )
                        r.raise_for_status()
                        st.session_state.improve_result = r.json()["improved_message"]
                    except Exception as e:
                        st.error(f"Error: {e}")

        if st.session_state.improve_result:
            st.markdown(
                f'<div class="result-box-blue">{st.session_state.improve_result}</div>',
                unsafe_allow_html=True,
            )
            st.code(st.session_state.improve_result, language=None)