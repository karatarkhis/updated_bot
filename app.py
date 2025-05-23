import streamlit as st
import pandas as pd

# ورودی‌ها
st.title("📦 ماشین حساب گمرکی")

nerkh_arz = st.number_input("🔹 نرخ ارز (ریال)", min_value=1000, format="%d")
arzesh = st.number_input("🔹 ارزش فوب کالا (دلار)", min_value=1.0, format="%.2f")
bimeh = st.number_input("🔹 مبلغ بیمه (ریال)", min_value=0, format="%d")
keraye_haml = st.number_input("🔹 مبلغ کرایه حمل (ریال)", min_value=0, format="%d")
makhaz = st.number_input("🔹 ماخذ (% درصد)", min_value=0.0, max_value=100.0, format="%.2f")

if st.button("📊 محاسبه"):
    # محاسبات
    fob = nerkh_arz * arzesh
    cif = fob + bimeh + keraye_haml
    hoghogh_vorodi = (cif * makhaz) / 100
    helal_ahmar = hoghogh_vorodi / 1000
    pasmand = (cif * 0.5) / 1000
    vat = (cif + hoghogh_vorodi + helal_ahmar) * 0.10

    # ساخت دیتافریم برای نمایش جدول
    data = {
        "شرح هزینه": [
            "ارزش سیف کالا",
            "حقوق ورودی کالا",
            "۱٪ هلال احمر",
            "♻️ مبلغ پسماند",
            "📌 مالیات بر ارزش افزوده (VAT)"
        ],
        "مقدار (ریال)": [
            f"{round(cif):,}",
            f"{round(hoghogh_vorodi):,}",
            f"{round(helal_ahmar):,}",
            f"{round(pasmand):,}",
            f"{round(vat):,}"
        ]
    }

    df = pd.DataFrame(data)

    # نمایش جدول نهایی
    st.markdown("## ✅ نتایج نهایی محاسبات گمرکی")
    st.table(df)
