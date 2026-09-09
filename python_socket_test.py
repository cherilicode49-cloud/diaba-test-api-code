# import socketio

# # Initialize the client
# sio = socketio.Client()

# @sio.event
# def connect():
#     print("🚀 Connected to server successfully!")

# @sio.event
# def disconnect():
#     print("❌ Disconnected from server")

# # Force the transport protocol to avoid engine version mismatches
# sio.connect(
#     "https://api-diaba.icode49solution.com", 
#     transports=['websocket', 'polling']
# )

# sio.wait()



import socketio

sio = socketio.Client()

@sio.event
def connect():
    print("🚀 Connected to server successfully!")

@sio.event
def connect_error(data):
    # This will print the precise error message returned from Uvicorn/Django
    print(f"❌ Connection error details: {data}")

@sio.event
def disconnect():
    print("❌ Disconnected from server")

try:
    sio.connect("https://api-diaba.icode49solution.com")
    sio.wait()
except Exception as e:
    print(f"Caught main exception: {e}")