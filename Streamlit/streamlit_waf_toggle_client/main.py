import streamlit as st
import requests
import urllib.parse
import jwt

st.set_page_config(page_title="Login", layout="centered")
st.title("🔐 Cognito Login / Callback Page")

# Load from secrets
region = st.secrets["AWS_REGION"]
user_pool_domain = st.secrets["COGNITO_DOMAIN"]
client_id = st.secrets["COGNITO_CLIENT_ID"]
redirect_uri = st.secrets["COGNITO_REDIRECT_URI"]
clean_domain = user_pool_domain.replace("https://", "").replace("http://", "")

# Generate login URL
login_url = (
    f"https://{clean_domain}/login?client_id={client_id}"
    f"&response_type=code&scope=email+openid+profile"
    f"&redirect_uri={urllib.parse.quote(redirect_uri, safe='')}"
)
st.markdown(f"[🔐 Click here to log in with Cognito]({login_url})")

# Get code from query params
auth_code = st.query_params.get("code", None)

# Exchange code for tokens
if auth_code and "id_token" not in st.session_state:
    token_url = f"https://{clean_domain}/oauth2/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": auth_code,
        "redirect_uri": redirect_uri,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    st.info("🔄 Exchanging code for tokens...")
    st.write("Payload:", payload)

    try:
        response = requests.post(token_url, data=payload, headers=headers)
        st.write("Response:", response.status_code, response.text)

        if response.status_code == 200:
            tokens = response.json()
            st.session_state.id_token = tokens.get("id_token")
            st.experimental_rerun()
        else:
            st.error(f"❌ Token exchange failed: {response.text}")
    except Exception as e:
        st.error(f"❌ Exception during token exchange: {e}")

# Show user profile if logged in
if "id_token" in st.session_state:
    try:
        decoded = jwt.decode(st.session_state.id_token, options={"verify_signature": False})
        st.success("✅ Logged in successfully!")
        st.markdown("### 👤 User Profile")
        st.json(decoded)

        if "admin" in decoded.get("cognito:groups", []):
            st.info("You are an **admin** user.")
        else:
            st.warning("You are logged in, but not an admin.")
    except Exception as e:
        st.error(f"❌ Error decoding token: {e}")

# Logout
st.markdown("---")
st.markdown("### 🔓 Logout")

logout_url = (
    f"https://{clean_domain}/logout?client_id={client_id}"
    f"&logout_uri={urllib.parse.quote(redirect_uri, safe='')}"
)

if st.button("Logout"):
    st.session_state.clear()
    st.markdown(f"[Click here to logout]({logout_url})", unsafe_allow_html=True)
