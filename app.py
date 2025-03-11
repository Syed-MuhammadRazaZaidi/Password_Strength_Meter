import re
import streamlit as st
import random
import string

# Set up Streamlit page configuration at the very beginning.
st.set_page_config(page_title="Password Strength Meter", layout="centered")

# Try to import zxcvbn for advanced strength evaluation.
try:
    from zxcvbn import zxcvbn
    ZXCVBN_AVAILABLE = True
except ImportError:
    ZXCVBN_AVAILABLE = False

# List of common weak passwords.
COMMON_PASSWORDS = ['password', '123456', '12345678', 'qwerty', 'abc123']

def check_password_strength(password):
    """
    Evaluate the strength of the given password.
    
    Returns:
        score (float): The averaged score from basic checks and zxcvbn (if available).
        feedback (list): A list of feedback messages to help improve the password.
    """
    if not isinstance(password, str):
        return 0, ["Invalid input: password must be a string."]
    
    if password.lower() in COMMON_PASSWORDS:
        return 0, ["This password is too common. Please choose a different one."]
    
    basic_score = 0
    feedback = []
    
    if len(password) >= 8:
        basic_score += 1
    else:
        feedback.append("Password should be at least 8 characters long.")
    
    if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
        basic_score += 1
    else:
        feedback.append("Include both uppercase and lowercase letters.")
    
    if re.search(r"\d", password):
        basic_score += 1
    else:
        feedback.append("Add at least one number (0-9).")
    
    if re.search(r"[!@#$%^&*]", password):
        basic_score += 1
    else:
        feedback.append("Include at least one special character (!@#$%^&*).")
    
    score = basic_score  # basic score out of 4
    
    if ZXCVBN_AVAILABLE:
        result = zxcvbn(password)
        advanced_score = result['score']  # 0 to 4 scale.
        score = (basic_score + advanced_score) / 2
        if result['feedback']['warning']:
            feedback.append(result['feedback']['warning'])
        if result['feedback']['suggestions']:
            feedback.extend(result['feedback']['suggestions'])
    
    return score, feedback

def generate_strong_password(length=12):
    """
    Generate a random strong password based on given criteria.
    """
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))

def get_progress_color(percentage):
    if percentage < 40:
        return "#F44336"  # Red for weak
    elif percentage < 70:
        return "#FF9800"  # Orange for moderate
    else:
        return "#4CAF50"  # Green for strong

# Inject custom CSS for a dynamic progress bar.
st.markdown(
    """
    <style>
    .progress-container {
        width: 100%;
        background-color: #ddd;
        border-radius: 20px;
        overflow: hidden;
        margin: 10px 0;
        height: 20px;
    }
    .progress-bar {
        height: 100%;
        transition: width 0.5s ease, background-color 0.5s ease;
    }
    </style>
    """, unsafe_allow_html=True
)

# Title and introductory text.
st.title("🗝️ Password Strength Meter")
st.write("Enter your password below to check its strength in real-time.")

# Password input field.
password = st.text_input("Enter your password:", type="password")

# Create an output container below the password field.
if password:
    output_container = st.container()
    with output_container:
        score, feedback = check_password_strength(password)
        strength_percentage = min(int((score / 4) * 100), 100)
        bar_color = get_progress_color(strength_percentage)
        
        # Display the progress bar.
        progress_html = f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {strength_percentage}%; background-color: {bar_color};"></div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
        
        # Display the appropriate message.
        if score >= 3.5:
            st.success("✅ Strong Password!")
        elif score >= 2.5:
            st.warning("⚠️ Moderate Password - Consider adding more security features.")
        else:
            st.error("❌ Weak Password - Improve it using the suggestions below.")
        
        # Display suggestions below the message.
        if feedback:
            st.write("### Suggestions:")
            for tip in feedback:
                st.write(f"- {tip}")

# Password Generator section.
if "generated_password" not in st.session_state:
    st.session_state.generated_password = ""

st.write("## Generate a Strong Password")
gen_length = st.slider("Password Length", min_value=8, max_value=24, value=12)

if st.button("🔄 Generate Strong Password"):
    st.session_state.generated_password = generate_strong_password(gen_length)

if st.session_state.generated_password:
    st.text_input("Suggested Strong Password:", value=st.session_state.generated_password, disabled=True)
    st.download_button("Download Password", st.session_state.generated_password, file_name="strong_password.txt")

# Optional user feedback.
user_feedback = st.text_area("Rate these suggestions or leave your feedback (optional):")
if st.button("Submit Feedback"):
    st.info("Thank you for your feedback!")
