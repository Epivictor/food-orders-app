import streamlit as st
import pandas as pd
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# --------------------------------
# ΡΥΘΜΙΣΕΙΣ LOGIN
# --------------------------------
users = {
    "kifisia": {"password": "1234", "store": "Κηφισιά"},
    "marousi": {"password": "1234", "store": "Μαρούσι"},
    "panormou": {"password": "1234", "store": "Πανόρμου"},
    "pratirio": {"password": "1234", "store": "Πρατήριο"},
    "admin": {"password": "admin", "store": "Διαχειριστής"},
}

# --------------------------------
# ΑΡΧΕΙΟ ΑΠΟΘΗΚΕΥΣΗΣ
# --------------------------------
FILE = "orders.xlsx"
if os.path.exists(FILE):
    orders = pd.read_excel(FILE)
else:
    orders = pd.DataFrame(columns=["Κατάστημα", "Προϊόν", "Ποσότητα"])

# --------------------------------
# LOGIN
# --------------------------------
st.title("📦 Σύστημα Παραγγελιών Βιομηχανίας Τροφίμων")

username = st.text_input("Όνομα χρήστη")
password = st.text_input("Κωδικός", type="password")

if st.button("Σύνδεση"):
    if username in users and users[username]["password"] == password:
        st.session_state["user"] = username
        st.success(f"✅ Καλώς ήρθες, {users[username]['store']}!")
    else:
        st.error("❌ Λάθος στοιχεία")

# --------------------------------
# ΑΝ Ο ΧΡΗΣΤΗΣ ΕΙΝΑΙ ΣΥΝΔΕΔΕΜΕΝΟΣ
# --------------------------------
if "user" in st.session_state:
    user = st.session_state["user"]
    store = users[user]["store"]

    if user == "admin":
        st.subheader("📊 Συγκεντρωτικό")
        st.dataframe(orders)

        if st.button("Δημιουργία Συγκεντρωτικού (Excel)"):
            summary = orders.groupby("Προϊόν")["Ποσότητα"].sum().reset_index()
            summary.to_excel("συγκεντρωτικό.xlsx", index=False)
            st.success("✅ Δημιουργήθηκε το αρχείο 'συγκεντρωτικό.xlsx'")

        if st.button("Δημιουργία Συγκεντρωτικού (PDF)"):
            summary = orders.groupby("Προϊόν")["Ποσότητα"].sum().reset_index()

            # Δημιουργία PDF
            c = canvas.Canvas("συγκεντρωτικό.pdf", pagesize=A4)
            width, height = A4

            c.setFont("Helvetica-Bold", 16)
            c.drawString(200, height - 50, "Συγκεντρωτικό Παραγγελιών")

            c.setFont("Helvetica", 12)
            y = height - 100
            c.drawString(50, y, "Προϊόν")
            c.drawString(300, y, "Σύνολο")
            y -= 20

            for _, row in summary.iterrows():
                c.drawString(50, y, str(row["Προϊόν"]))
                c.drawString(300, y, str(row["Ποσότητα"]))
                y -= 20
                if y < 50:  # νέα σελίδα αν γεμίσει
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = height - 50

            c.save()
            st.success("✅ Δημιουργήθηκε το αρχείο 'συγκεντρωτικό.pdf'")

    else:
        st.subheader(f"📋 Παραγγελίες καταστήματος: {store}")

        product = st.text_input("Προϊόν")
        quantity = st.number_input("Ποσότητα", min_value=0, step=1)

        if st.button("Καταχώρηση"):
            new_order = pd.DataFrame([[store, product, quantity]], columns=orders.columns)
            orders = pd.concat([orders, new_order], ignore_index=True)
            orders.to_excel(FILE, index=False)
            st.success("✅ Η παραγγελία καταχωρήθηκε!")

        st.write("### Οι παραγγελίες μου")
        st.dataframe(orders[orders["Κατάστημα"] == store])
