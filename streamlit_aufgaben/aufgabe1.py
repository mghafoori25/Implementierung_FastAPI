import streamlit as st

st.title("Meine erste Streamlit-App")

# Streamlit führt das gesamte Skript bei jeder Änderung eines Widgets neu aus.
# Dadurch soeht man sofort, wie sich Eingaben auf die Ausgabe auswirken.

name = st.text_input("Wie heißt du?")
alter = st.slider("Wie alt bist du?", min_value=10, max_value=100, value=18)

st.write("Deine Eingaben:")
st.write(f"Name: {name}")
st.write(f"Alter: {alter}")

if name and alter >= 18:
    st.success(f"Hallo {name}, du bist volljährig.")
elif name and alter < 18:
    st.warning(f"Hallo {name}, du bist noch nicht volljährig.")
else:
    st.info("Bitte gib zuerst deinen Namen ein.")
