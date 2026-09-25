Pasted text.txt
Document
Pasted text(1).txt
Document
and what was problem through sied of google ai studio
Pasted text(2).txt
Document
Pasted text (2).txt
Document

Yes, Heena, I’ve got the current app.py. 👍

I can work directly from this version. I can see that it already has:

Gemini gemini-3.8-flash
Text input
Microphone/voice input
Conversation history
Official service links
Structured, attractive answers
429 quota handling
Voice requests sent directly to Gemini

So we don't need to rebuild NextStep AI from scratch.

If your goal is to solve the slow/429 problem from the app side, I can now modify this exact file and give you one complete app.py, keeping the existing UI and features while reducing unnecessary Gemini requests.

so give compleyely working fast professional app.py

Yes, Heena. I rebuilt the app around the exact problem in your current version.

What this version changes
⚡ One Gemini request per user action. No fallback loop that can consume extra quota.
🎙️ Microphone beside the search box.
💬 Proper Send button, so typing doesn't automatically trigger Gemini.
🧠 Keeps recent conversation context, but limits it to reduce unnecessary tokens.
🔗 Official source appears only for an actual service request.
✨ Professional structured answers with summary, steps, documents, and next action.
🛡️ API key remains in st.secrets.
🚦 Clear handling for 429 RESOURCE_EXHAUSTED.
🧹 No giant HTML feature-card blocks.
🆕 New Conversation button.
💡 Suggested prompts.
🗣️ Voice requests use the same Gemini model.
🔧 Technical errors are hidden inside an expandable section.

Your previous version was already making a direct Gemini call, but the new version deliberately avoids adding fallback calls when Gemini returns 429.

Download the complete app.py

Download the corrected complete app.py

Put this file in your GitHub repo as app.py, keeping your existing Streamlit Secret:

GEMINI_API_KEY = "your-existing-key"

Important: This can make the app faster and prevent your code from unnecessarily increasing quota usage, but if Google's project quota is genuinely exhausted, the app cannot bypass Google's 429 limit. The code will now tell you that clearly instead of pretending the Gemini connection is broken. 

app.py
Code
i didnt understood

No problem 😭. I made it sound way more complicated than it is.

You do not need to understand the code right now. Just do these steps:

1. Download the new file

Download app.py

2. Open your GitHub repository

Go to your nextstep-ai repository.

3. Replace your old app.py
Open app.py
Click Edit ✏️
Select all the old code
Delete it
Open the downloaded app.py
Copy all of its code
Paste it into GitHub
Click Commit changes
4. Don't change your API key

Your Streamlit Secret should remain:

GEMINI_API_KEY = "your-existing-key"

Do not put the API key inside app.py or GitHub.

5. Wait for Streamlit

Streamlit should automatically redeploy after the GitHub commit.

Then test:

"I want to apply for an income certificate."

If Gemini quota is available, NextStep AI should answer normally.

If you still see 429 / RESOURCE_EXHAUSTED, that's Google's quota limit, not a problem with your interface. The new code will show that clearly instead of giving the vague "trouble connecting to AI service" message.

So basically:

Download → replace app.py on GitHub → commit → Streamlit redeploys → test. 🚀

app.py
Code

Library
/
app.py
999
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
import json
import re
import time


import streamlit as st
from google import genai
from google.genai import types




# ============================================================
# PAGE
# ============================================================


st.set_page_config(
    page_title="NextStep AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)




# ============================================================
# GEMINI
# ============================================================


MODEL_NAME = "gemini-3.8-flash"


try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    client_error = None
except Exception as exc:
    client = None
    client_error = str(exc)




# ============================================================
