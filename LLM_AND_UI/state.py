import streamlit as st

def init_session_state():
    defaults = {
        "scrape_df": None,
        "upload_df": None,
        "manual_df": None,
        "active_section": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v if v is not None else __empty_df()

import streamlit as st

def freeze_ui_for_others(current):
    active = st.session_state.get("active_section", None)

    # Fix: Make sure active_section is a string
    if isinstance(active, str) and active != current:
        st.info(f"🔒 '{active}' is currently processing. Please wait...")
        st.stop()

def unlock_ui():
    st.session_state.active_section = None


def __empty_df():
    import pandas as pd
    return pd.DataFrame()
