import streamlit as st
import base64
import time
from groq import Groq
from dotenv import load_dotenv

# ————— CONFIG ——————————————————————
#API_KEY   = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
MODEL = "llama3-70b-8192"
load_dotenv ()
client = Groq()


st.set_page_config(layout="centered", page_title="Hakim AI Companion")

# load and encode
with open("Assigments/Assigment2/HakimCompanion.png", "rb") as f:
    data = base64.b64encode(f.read()).decode()

htmlSidebar = f"""
<!--<div class="chat-header"> -->
<div style="display:flex; align-items:center;">
  <img src="data:image/png;base64,{data}" width="40"/>
  <h2 style="margin:0 0 0 5px;">HAKIM AI Companion</h2>
</div>
<!--</div>-->
"""



st.sidebar.markdown(htmlSidebar, unsafe_allow_html=True)
# draws a thin rule
#st.sidebar.divider()
# a thin line with minimal vertical padding
st.sidebar.markdown(
    '<hr style="border:none; border-top:1px solid #ddd; margin:2px 0;" />',
    unsafe_allow_html=True
)
# Sidebar
st.sidebar.header("Welcome! Mohammed, Jawed")
#st.sidebar.divider()
st.sidebar.markdown(
    '<hr style="border:none; border-top:1px solid #ddd; margin:2px 0;" />',
    unsafe_allow_html=True
)
# A radio button acts like a menu

if st.sidebar.button("🏠 Home"):
    st.header("Home")
    st.write("Here you can tweak your preferences…")
if st.sidebar.button("🎨 Customize"):
    st.header("Customize")
    st.write("Here you can tweak your preferences…")
if st.sidebar.button("⚙️ Settings"):
    st.header("Settings")
    st.write("General app settings go here…")
if st.sidebar.button("🚪 Logout"):
    st.warning("You’ve been logged out. 👋")
#--------------------------
# available models
MODEL_OPTIONS = [
    "mannat-2.1-beta",
    "llama3-70b-8192",
    "gemma2-9b-it",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "whisper-large-v3"
]

#session_state to persist the choice across reruns
if "model" not in st.session_state:
    st.session_state.model = MODEL_OPTIONS[0]

# Top bar: two columns, dropdown on the left, blank (or logo/title) on the right to display model
col1, col2 = st.columns([1, 4], gap="small")
with col1:
    st.session_state.model = st.selectbox(
        "Choose your Model:", MODEL_OPTIONS, index=MODEL_OPTIONS.index(st.session_state.model)
    )

with col2:
   
    st.markdown("")  # placeholder
#---------------------
st.markdown(
    """
    <style>
    /* constrain width to ~360px and center it */
    .reportview-container .main {
      max-width: 360px;
      margin: 0 auto;
      padding-top: 1rem;
    }
    /* top “notch” header */
    .chat-header {
      display: flex;
      align-items: center;
      padding: 0.5rem;
      background: #5c4dff;
      color: white;
      border-radius: 0.5rem 0.5rem 0 0;
    }
    .chat-header img {
      width: 24px;
      cursor: pointer;
      margin-right: 0.5rem;
    }
    .chat-container {
      background: #f5f5f5;
      height: 600px;
      overflow-y: auto;
      padding: 1rem;
      border-radius: 0 0 0.5rem 0.5rem;
    }
    /* input bar pinned at bottom */
    .chat-input {
      position: fixed;
      bottom: 1rem;
      left: 50%;
      transform: translateX(-50%);
      width: 360px;
      display: flex;
      gap: 0.5rem;
    }
    .chat-input > div { flex: 1; }
    
    </style>
    """,
    unsafe_allow_html=True,
)


htmlMain = f"""
<div class="chat-header">
  <div style="display:flex; flex-direction:column; align-items:flex-start;">
    <div style="display:flex; align-items:center;">
      <img src="data:image/png;base64,{data}" width="30" style="margin-right:4px;"/>
      <h1 style="margin:0; font-size:2.5rem;">HAKIM AI Companion</h1>
    </div>
    <span style="margin-top:4px; font-size:0.875rem; color:#e0e0e0;">
      Your personalized AI health assistant
    </span>
  </div>
</div>
"""
st.markdown(htmlMain, unsafe_allow_html=True)

# ————— HELPERS ——————————————————————
def groq_reply(prompt: str):
    """
    Call Groq synchronously and return the full text reply.
    You could also use groq.inference.stream() for chunked output.
    """
    resp = client.inference.sync(
        model=MODEL,
        inputs=[{"role": "user", "content": prompt}],
        parameters={"temperature":0.7}
    )

    return resp.choices[0].message["content"]
# ------------------------------------------


history_container = st.container()
# ————— CHAT SETUP ——————————————————————
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role":"assistant","text":"Jawed, how can I help you… or attach a file?"}
    ]

history_container = st.container()

# ————— SEND CALLBACK ——————————————————————
def send():
    prompt_obj = st.session_state.user_input
    if not prompt_obj:
        return

    user_txt = prompt_obj.text
    files    = prompt_obj["files"]

    # echo user
    if user_txt:
        st.session_state.messages.append({"role":"user","text":user_txt})
    for f in files:
        st.session_state.messages.append({"role":"user","text":f"📎 Uploaded file: {f.name}"})

    
    thinking_placeholder = st.empty()
    thinking_bubble = thinking_placeholder.chat_message("assistant")
#Animate “thinking…”
    for dots in ["", ".", "..", "..."] * 2:
        thinking_bubble.write(f"🤖 thinking{dots}")
        time.sleep(0.2)
        thinking_placeholder.empty()
        thinking_bubble = thinking_placeholder.chat_message("assistant")

    # call Groq
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role":"user","content": user_txt or f.name}],
        )
        reply = resp.choices[0].message.content
    except Exception as e:
        reply = f"⚠️ Error: {e}"

    thinking_placeholder.empty()
    st.session_state.messages.append({"role":"assistant","text":f" 🤖: {reply}"})


# ————— RENDER HISTORY ——————————————————————
# ❶ Chat history container
history_container = st.container()
with history_container:
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["text"])

# ————— CHAT INPUT ——————————————————————


st.chat_input(
    "How can I help you… or attach a file?",
    key="user_input",
    accept_file=True,
    file_type=["png","jpg","pdf","txt"],
    on_submit=send
)

#prompt = st.chat_input("I want to know...", key="user_input",max_chars=None,accept_file=True,file_type=["jpg", "jpeg", "png", "txt", "pdf"], on_submit=send)
#st.chat_input("I want to know...", key="user_input",max_chars=None,accept_file=True,file_type=["jpg", "jpeg", "png", "txt", "pdf"], on_submit=send)
#st.chat_input("Type a message...", key="user_input",accept_file=True, on_submit=send)
#if prompt and prompt.text:
 #   st.chat_message("user").write(prompt.text)
    #st.write_stream(stream_data(prompt.text))
  #  st.chat_message("ai").write(f"HC: {prompt.text}\n")
#st.chat_message("ai").write(f"HC: This feature is currently not available for public use. We apologize for any inconvenience.")

#if prompt and prompt["files"]:
 #   st.image(prompt["files"][0])
# render it
#st.markdown(htmlMain, unsafe_allow_html=True)


#col_icon, col_title = st.columns([1, 8], gap="small")
#with col_icon:
 #   st.image("HakimCompanion.png", width=40)      # adjust width to taste
#with col_title:
 #   st.title("HAKIM Companion")

#tab = st.radio("", ["Chat", "Profile"], horizontal=True)

#if tab == "Chat":
 #   st.header("🏠 Chat")
  #  if st.button("Get Started", use_container_width=True):
   #     st.success("Let’s go!")

#elif tab == "Profile":
 #   st.header("👤 Profile")
  #  st.text_input("Name")
   # st.text_input("Email")

#st.subheader("Hello MD!\n,I'm your personalize companion")

#st.markdown(htmlMain, unsafe_allow_html=True)
#st.subheader("How can I help\n you? ")
