import streamlit as st

st.title("Session State: Zähler-App")

"""
Falscher Ansatz ohne st.session_state:

counter = 0

if st.button("Hochzählen"):
    counter +=1

st.write(counter)

Problem:
Bei jedem Klick wird das gesamte Skript neu ausgeführt.
Dadurch wird counter immer wieder auf 0 gesetzt und zählt nicht korrekt weiter.

"""

if "counter" not in st.session_state:
    st.session_state.counter = 0

st.write(f"Aktueller Zählerstand: {st.session_state.counter}")

if st.button("Hochzählen"):
    st.session_state.counter += 1
    st.rerun()

if st.button("Reset"):
    st.session_state.counter = 0
    st.rerun()