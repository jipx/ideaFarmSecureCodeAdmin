import streamlit as st
import requests
import jwt
import datetime

st.set_page_config(page_title="Toggle WAF", layout="centered")
st.title("🛡️ Toggle WAF Protection")

# --- 1. Ensure user is authenticated ---
if "id_token" not in st.session_state:
    st.warning("You must be logged in to access this page.")
    st.markdown("[🔑 Go to login page](main)")
    st.stop()

# --- 2. Decode JWT and validate ---
try:
    decoded = jwt.decode(st.session_state.id_token, options={"verify_signature": False})
    
    # Optional: token expiry check
    exp = decoded.get("exp")
    if exp and datetime.datetime.utcfromtimestamp(exp) < datetime.datetime.utcnow():
        st.error("Your session has expired. Please log in again.")
        st.stop()

    if "admin" not in decoded.get("cognito:groups", []):
        st.error("Access denied. Admins only.")
        st.stop()

except Exception as e:
    st.error(f"Token validation failed: {e}")
    st.stop()

st.success("✅ You are authorized as an admin.")

# --- 3. Show current WAF status (via GET) ---
st.markdown("### 📡 Current WAF Status")
api_url = st.secrets["API_GATEWAY_URL"]

try:
    status_resp = requests.get(api_url, headers={
        "Authorization": f"Bearer {st.session_state.id_token}"
    })
    if status_resp.ok:
        current_status = status_resp.json().get("current_mode", "unknown")
        st.info(f"Current WAF Mode: **{current_status}**")
    else:
        st.warning("Unable to fetch current WAF mode.")
except Exception as e:
    st.warning(f"Error fetching current status: {e}")

# --- 4. Toggle WAF Mode ---
st.markdown("### 🔄 Choose New WAF Mode")
mode = st.selectbox("Select WAF mode:", ["normal", "block"])

if mode == "normal":
    st.markdown("✔️ **Normal Mode:** Standard traffic is allowed.")
else:
    st.markdown("⛔ **Block Mode:** All incoming requests will be blocked.")

# Confirm + toggle button only enabled after checkbox
if st.checkbox("✅ I confirm I want to apply this mode."):
    if st.button("⚡ Send Toggle Request"):
        try:
            response = requests.post(api_url,
                headers={
                    "Authorization": f"Bearer {st.session_state.id_token}",
                    "Content-Type": "application/json"
                },
                json={"mode": mode}
            )
            if response.ok:
                st.success(f"✅ WAF toggled to `{mode}`")
                st.code(f"{datetime.datetime.now()}: {response.json()}", language="json")
                with st.expander("🔍 Full Response"):
                    st.json(response.json())
            else:
                st.error(f"❌ Toggle failed: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"Request error: {e}")
