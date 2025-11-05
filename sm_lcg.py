import streamlit as st
import pandas as pd

# --------------------------
# 🔧 Page Configuration
# --------------------------
st.set_page_config(page_title="Monte Carlo Demand Simulation", page_icon="🎲")
st.title("🎯 Dynamic Monte Carlo Demand Simulation using LCG")

st.write("""
This app simulates **daily product demand** using a **Linear Congruential Generator (LCG)**  
and maps random numbers to discrete demand outcomes based on your custom probability distribution.
""")

# --------------------------
# ⚙️ LCG Parameters
# --------------------------
st.sidebar.header("⚙️ LCG Parameters")
a = st.sidebar.number_input("Multiplier (a)", min_value=1, max_value=1000, value=13)
c = st.sidebar.number_input("Increment (c)", min_value=0, max_value=1000, value=7)
m = st.sidebar.number_input("Modulus (m)", min_value=2, max_value=10000, value=100)
X0 = st.sidebar.number_input("Seed (X₀)", min_value=0, max_value=10000, value=35)
n_days = st.sidebar.slider("Number of Days to Simulate", 1, 100, 10)

# --------------------------
# 📦 Demand & Probability Inputs (Dynamic + Horizontal)
# --------------------------
st.subheader("📦 Define Your Demand Distribution")

# Choose number of demand points
num_demands = st.number_input("Number of demand values:", min_value=2, max_value=10, value=6)

# Default data (extends or trims automatically)
default_demands_all = [0, 10, 20, 30, 40, 50]
default_probs_all = [0.01, 0.20, 0.15, 0.50, 0.12, 0.02]

# If user chooses fewer or more, auto-adjust
default_demands = (default_demands_all + [0] * 10)[:num_demands]
default_probs = (default_probs_all + [round(1/num_demands, 2)] * 10)[:num_demands]

# --- Demand Inputs (horizontal row)
st.markdown("#### ✏️ Enter Demand Values Horizontally")
demand_cols = st.columns(num_demands)
demand_values = [demand_cols[i].number_input(f"D{i+1}", value=default_demands[i], key=f"demand_{i}") for i in range(num_demands)]

# --- Probability Inputs (horizontal row)
st.markdown("#### 🎯 Enter Corresponding Probabilities Horizontally")
prob_cols = st.columns(num_demands)
probabilities = [prob_cols[i].number_input(f"P{i+1}", value=default_probs[i], step=0.01, key=f"prob_{i}") for i in range(num_demands)]

# --------------------------
# 🧮 Normalize Probabilities
# --------------------------
prob_sum = sum(probabilities)
if prob_sum == 0:
    st.error("⚠️ Probabilities cannot all be zero.")
else:
    if abs(prob_sum - 1.0) > 1e-6:
        st.warning(f"⚠️ Probabilities sum to {prob_sum:.2f}. Normalizing automatically.")
        probabilities = [p / prob_sum for p in probabilities]

# --------------------------
# 📈 Compute Cumulative Probabilities
# --------------------------
cum_probs, cum_sum = [], 0
for p in probabilities:
    cum_sum += p
    cum_probs.append(round(cum_sum, 4))

st.write("### 📊 Cumulative Probability Table")
cum_df = pd.DataFrame({
    "Demand": demand_values,
    "Probability": probabilities,
    "Cumulative Probability": cum_probs
})
st.dataframe(cum_df, hide_index=True)

# --------------------------
# 🧠 LCG Functions
# --------------------------
def generate_lcg(seed, a, c, m, n):
    numbers = []
    X = seed
    for _ in range(n):
        X = (a * X + c) % m
        numbers.append(X)
    return numbers

def map_to_demand(u, demands, cum_probs):
    for i, cp in enumerate(cum_probs):
        if u <= cp:
            return demands[i]
    return demands[-1]

# --------------------------
# 🧾 Run Simulation
# --------------------------
X_values = generate_lcg(X0, a, c, m, n_days)
U_values = [x / m for x in X_values]
demands_generated = [map_to_demand(u, demand_values, cum_probs) for u in U_values]

# --------------------------
# 📋 Results Table
# --------------------------
df = pd.DataFrame({
    "Day": range(1, n_days + 1),
    "X (LCG)": X_values,
    "U = X/m": [round(u, 4) for u in U_values],
    "Demand": demands_generated
})

st.subheader("🧾 Simulation Results")
st.dataframe(df, hide_index=True)

# --------------------------
# 📉 Calculations
# --------------------------
if n_days >= 6:
    avg_6 = sum(demands_generated[:6]) / 6
    st.write(f"**Average demand for first 6 days:** {avg_6:.2f}")

avg_n = sum(demands_generated) / n_days
st.write(f"**Average demand for first {n_days} days:** {avg_n:.2f}")

if n_days >= 5:
    st.write(f"**Expected demand on 5th day:** {demands_generated[4]}")

# --------------------------
# 📈 Visualization
# --------------------------
st.subheader("📈 Demand Trend Over Time")
st.line_chart(df.set_index("Day")["Demand"], height=300)

# --------------------------
# ℹ️ Sidebar Tips
# --------------------------
st.sidebar.markdown("---")
st.sidebar.write("💡 **Tip:** Default values reflect a standard discrete demand distribution. Modify and observe changes dynamically!")
