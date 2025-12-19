import streamlit as st
import math

# ============================================================
# PAGE SETTINGS
# ============================================================
st.set_page_config(page_title="Solar Calculator", layout="centered")

st.markdown("""
    <style>
        .stApp {
            background-color: #ffffff;
            color: #000000;
        }
        h1, h2, h3, h4, h5, h6, p, label, span, div {
            color: #111111 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("☀️ Solar PV Calculator")
st.write("**Minimalist & Professional Edition**")

# ============================================================
# STEP 1 — FRONT SIDE ENERGY (Efront)
# ============================================================
st.header("🔶 STEP 1 — Front-Side Energy Output (Efront)")

# ----------------------- FTEMP -----------------------
st.subheader("1️⃣ Temperature Factor (ftemp)")
use_ftemp = st.checkbox("Use ftemp?", value=True)
if use_ftemp:
    Pcoef = st.number_input("Temperature Coefficient Pcoef (%/°C)", value=-0.3500)
    Tavg  = st.number_input("Average Temperature Tavg (°C)", value=35.0000)
    Tstc  = st.number_input("STC Temperature Tstc (°C)", value=25.0000)
    ftemp = 1 + ((Pcoef / 100) * (Tavg - Tstc))
else:
    ftemp = 1.0000

# ----------------------- AREA -----------------------
st.subheader("2️⃣ Panel Area")
panel_length = st.number_input("Panel Length (m)", value=2.0000)
panel_width  = st.number_input("Panel Width (m)", value=1.1000)
area = panel_length * panel_width
st.success(f"Panel Area = {area:.3f} m²")

# ----------------------- MAIN PARAMETERS -----------------------
st.subheader("3️⃣ Energy Parameters")

PSH = st.number_input("Peak Sun Hours (PSH)", value=4.5000)
PASTC = st.number_input("Panel Power at STC (W)", value=550.0000)

# ----------------------- OPTIONAL FACTORS -----------------------
st.write("### ⚙️ Optional Loss Factors")

def factor(label, value):
    use = st.checkbox(f"Use {label}", value=True)
    return st.number_input(label, value=value) if use else 1.0

fmm       = factor("Mismatch Factor (fmm)", 1.0)
fclean    = factor("Soiling Factor (fclean)", 0.98)
fdegrad   = factor("Degradation Factor (fdegrad)", 0.98)
fsunshade = factor("Shading Factor (fsunshade)", 1.0)
eta_cable = factor("Cable Efficiency", 0.98)
eta_inv   = factor("Inverter Efficiency", 0.97)

# ----------------------- Efront CALCULATION -----------------------
Efront = (PSH * PASTC * fmm * ftemp * fclean *
          fdegrad * fsunshade * eta_cable * eta_inv) / area

st.success(f"⚡ Front-side Energy (Efront) = **{Efront:.2f} Wh/m²**")

# ============================================================
# STEP 2 — BIFACIAL CALCULATION
# ============================================================
st.header("🔷 STEP 2 — Bifacial Energy Contribution")

use_bifacial = st.checkbox("Enable Bifacial Panel?", value=False)

if use_bifacial:
    bifaciality = st.number_input("Bifaciality Efficiency (e.g. 0.80)", value=0.80)
    albedo = st.number_input("Ground Albedo (e.g. sawit ≈ 0.12)", value=0.12)

    Erear = Efront * albedo * bifaciality
    Etotal = Efront + Erear
    gain = (Erear / Efront) * 100

    st.success(f"🔁 Rear Energy = {Erear:.2f} Wh/m²")
    st.success(f"⚡ Total Bifacial Energy = {Etotal:.2f} Wh/m²")
    st.info(f"📈 Bifacial Gain ≈ {gain:.2f} %")
else:
    Etotal = Efront
    st.info("Monofacial mode: Total Energy = Front Energy only")

st.markdown("---")

# ============================================================
# STEP 3 — PANEL FIT
# ============================================================
st.header("🔷 STEP 3 — Panel Layout")

Wroof = st.number_input("Area Width (m)", value=10.0)
Lroof = st.number_input("Area Length (m)", value=20.0)
spacing = st.number_input("Panel Spacing (m)", value=0.1)

N_land = math.floor(Wroof / (panel_width + spacing)) * \
         math.floor(Lroof / (panel_length + spacing))

N_port = math.floor(Wroof / (panel_length + spacing)) * \
         math.floor(Lroof / (panel_width + spacing))

col1, col2 = st.columns(2)
with col1:
    st.write("### Landscape")
    st.write(f"Total Panels: **{N_land}**")
with col2:
    st.write("### Portrait")
    st.write(f"Total Panels: **{N_port}**")

if N_land > N_port:
    st.success("✔ Landscape recommended")
elif N_port > N_land:
    st.success("✔ Portrait recommended")
else:
    st.info("Both orientations equal")
