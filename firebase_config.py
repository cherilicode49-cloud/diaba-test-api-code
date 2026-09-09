import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("diaba-2029f-firebase-adminsdk-fbsvc-81c7c321761.json")
firebase_admin.initialize_app(cred)
print(cred, 'Cred check ')

agent_cred = credentials.Certificate("diaba-chat-agent-2029f-firebase-adminsdk-fbsvc-81c7c321761.json")

try:
    agent_app = firebase_admin.get_app("agent_app")
    print("Agent Firebase Initialized")
except ValueError:
    agent_app = firebase_admin.initialize_app(agent_cred, name="agent_app")
    print("Agent Firebase Initialized")