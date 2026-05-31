"""Streamlit entrypoint placeholder.

Lane 3 owns the full UI. This placeholder keeps the app runnable enough for
early local smoke tests.
"""

from __future__ import annotations

from pathlib import Path

from src.graph import run_triage


def load_default_sample() -> str:
    sample = Path("samples/debt_collection.txt")
    if sample.exists():
        return sample.read_text(encoding="utf-8")
    return "Paste a legal letter here."


def main() -> None:
    try:
        import streamlit as st
    except Exception:
        result = run_triage(load_default_sample())
        print(result["verdict"])
        return

    st.set_page_config(page_title="LetterLens", layout="wide")
    st.title("LetterLens")
    st.caption("Legal-letter triage and orientation. Not legal advice.")

    if "letter_text" not in st.session_state:
        st.session_state.letter_text = load_default_sample()

    st.text_area("Letter text", key="letter_text", height=260)
    if st.button("Analyze", type="primary"):
        st.session_state.result = run_triage(st.session_state.letter_text)

    result = st.session_state.get("result")
    if result:
        st.subheader(result["verdict"]["value"].replace("_", " ").title())
        st.write(result["verdict"]["summary"])
        st.json(result)


if __name__ == "__main__":
    main()

