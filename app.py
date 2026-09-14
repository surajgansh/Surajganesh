import datetime
import io
import os
import qrcode
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Om Diagnostic Centre - Pathology Management",
    page_icon="🏥",
    layout="wide",
)

# Custom Styling for Professional Letterhead & UI
st.markdown(
    """
    <style>
        .main-header {
            text-align: center;
            border-bottom: 3px solid #004080;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .lab-title {
            color: #004080;
            font-size: 28px;
            font-weight: bold;
            margin: 0;
        }
        .lab-subtitle {
            color: #555;
            font-size: 14px;
            margin: 5px 0;
        }
        .report-box {
            border: 2px solid #004080;
            padding: 20px;
            border-radius: 8px;
            background-color: #fff;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# A to Z Pathology Tests Directory with Prices & Units
TESTS_DATABASE = {
    "Blood Sugar Fasting (FBS)": {"price": 100, "unit": "mg/dL", "range": "70 - 100"},
    "Blood Sugar PP (PPBS)": {"price": 100, "unit": "mg/dL", "range": "< 140"},
    "Complete Blood Count (CBC)": {
        "price": 350,
        "unit": "Cells/cumm",
        "range": "Variable",
    },
    "Creatinine - Serum": {"price": 250, "unit": "mg/dL", "range": "0.6 - 1.2"},
    "Lipid Profile": {"price": 600, "unit": "mg/dL", "range": "Desired < 200"},
    "Liver Function Test (LFT)": {
        "price": 700,
        "unit": "U/L",
        "range": "Variable",
    },
    "Thyroid Profile (T3 T4 TSH)": {
        "price": 550,
        "unit": "uIU/mL",
        "range": "0.4 - 4.0",
    },
    "Urine Routine & Microscopy": {
        "price": 150,
        "unit": "Present/Absent",
        "range": "Nil",
    },
    "Widal Test (Typhoid)": {"price": 200, "unit": " titer", "range": "Negative"},
    "Uric Acid": {"price": 300, "unit": "mg/dL", "range": "3.5 - 7.2"},
}

# Sidebar Navigation
st.sidebar.title("Lab Navigation")
menu = st.sidebar.ionario(
    [
        "Patient & Test Entry (ESGY)",
        "A-Z Test Directory",
        "View Reports / Bill",
    ]
)

# Session State for storing patient records
if "patients" not in st.session_state:
  st.session_state["patients"] = []

if menu == "A-Z Test Directory":
  st.subheader("📋 A to Z Pathology Tests Master List")
  st.write(
    "Here is the complete list of available laboratory tests, standard prices,"
    " and reference ranges."
  )

  import pandas as pd

  df = pd.DataFrame.from_dict(TESTS_DATABASE, orient="index")
  df.reset_index(inplace=True)
  df.columns = ["Test Name", "Price (₹)", "Unit", "Normal Reference Range"]
  st.table(df)

elif menu == "Patient & Test Entry (ESGY)":
  st.subheader("📝 Patient Registration & Test Entry Form")

  with st.form("entry_form"):
    col1, col2 = st.columns(2)
    with col1:
      p_name = st.text_input("Patient Full Name")
      p_age = st.number_input("Age", min_value=1, max_value=120, value=25)
      p_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    with col2:
      p_phone = st.text_input("Mobile Number")
      ref_doctor = st.text_input(
          "Referring Doctor", value="Dr. Self / General Practitioner"
      )
      bill_date = st.date_input("Date", datetime.date.today())

    st.markdown("---")
    st.write("### Select Lab Tests")
    selected_tests = st.multiselect(
        "Choose tests from A-Z directory:", list(TESTS_DATABASE.keys())
    )

    discount = st.number_input(
        "Discount (₹)", min_value=0, max_value=5000, value=0
    )

    submit_btn = st.form_submit_button("Generate Bill & QR Code")

    if submit_btn:
      if p_name and selected_tests:
        total_amount = sum(TESTS_DATABASE[test]["price"] for test in selected_tests)
        net_amount = total_amount - discount

        # Unique Bill ID generation
        bill_id = f"OM-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        patient_record = {
            "bill_id": bill_id,
            "name": p_name,
            "age": p_age,
            "gender": p_gender,
            "phone": p_phone,
            "doctor": ref_doctor,
            "date": str(bill_date),
            "tests": selected_tests,
            "total": total_amount,
            "discount": discount,
            "net": net_amount,
        }

        st.session_state["patients"].append(patient_record)
        st.success(
            f"Patient Registered Successfully! Bill ID: {bill_id}"
        )
      else:
        st.error(
            "Please fill in the patient's name and select at least one test."
        )

elif menu == "View Reports / Bill":
  st.subheader("🖨️ Professional Letterhead & Report Generator")

  if not st.session_state["patients"]:
    st.info("No patient records found. Please add a patient entry first.")
  else:
    patient_names = [
        f"{p['name']} ({p['bill_id']})" for p in st.session_state["patients"]
    ]
    selected_patient_str = st.selectbox(
        "Select Patient for Letterhead", patient_names
    )

    # Find selected patient details
    selected_p = next(
        p
        for p in st.session_state["patients"]
        if f"{p['name']} ({p['bill_id']})" == selected_patient_str
    )

    # Professional Letterhead View
    st.markdown(
        """
        <div class="report-box">
            <div class="main-header">
                <p class="lab-title">OM DIAGNOSTIC CENTRE</p>
                <p class="lab-subtitle">Advanced Pathology Laboratory & Research Center</p>
                <p class="lab-subtitle">📞 Contact: +91 XXXXXXXXXX | ✉️ info@omdiagnostic.com</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:st.write(f"**Bill ID:** {selected_p['bill_id']}")
    
st.write(f"**Patient Name:** {selected_p['name']}")

with col1:
    st.write(f"**Bill ID:** {selected_p['bill_id']}")
    st.write(f"**Patient Name:** {selected_p['name']}")
    st.write(f"**Age/Gender:** {selected_p['age']} Yrs / {selected_p['gender']}")
with col2:
    st.write(f"**Date:** {selected_p['date']}")
    st.write(f"**Phone:** {selected_p['phone']}")
    st.write(f"**Referring Doctor:** {selected_p['doctor']}")
    
with col2:
    st.write(f"**Date:** {selected_p['date']}")
    st.write(f"**Phone:** {selected_p['phone']}")
    st.write(f"**Referring Doctor:** {selected_p['doctor']}")
with
      st.write(**Date:** {selected_p['date']})
      st.write(**Phone:** {selected_p['phone']})
      st.write(**Referring Doctor:** {selected_p['doctor']})

    st.markdown("---")
    st.write("### Test Results")

    # Display test results table
    table_data = []
    for test in selected_p["tests"]:
      table_data.append({
          "Test Description": test,
          "Result": "Normal / Verified",
          "Unit": TESTS_DATABASE[test]["unit"],
          "Reference Range": TESTS_DATABASE[test]["range"],
          "Price (₹)": TESTS_DATABASE[test]["price"],
      })

    import pandas as pd

    st.table(pd.DataFrame(table_data))

    st.markdown(f"**Total Amount:** ₹{selected_p['total']}")
    st.markdown(f"**Discount:** ₹{selected_p['discount']}")
    st.markdown(f"### Net Payable: ₹{selected_p['net']}")

    # Generate QR Code for Verification
    qr_data = f"Bill ID: {selected_p['bill_id']}\nName: {selected_p['name']}\nNet Amt: {selected_p['net']}\nStatus: Verified"
    qr = qrcode.make(qr_data)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    byte_im = buf.getvalue()

    col_qr, col_sign = st.columns([1, 1])
    with col_qr:
      st.write("**Scan to Verify Report:**")
      st.image(byte_im, width=120)

    with col_sign:
      st.markdown("<br><br>", unsafe_allow_html=True)
      st.markdown(
          "<p style='text-align: right; font-weight: bold;'>Authorized"
          " Signatory<br>Pathologist (Lab Technician)</p>",
          unsafe_allow_html=True,
      )

    st.markdown("</div>", unsafe_allow_html=True)


