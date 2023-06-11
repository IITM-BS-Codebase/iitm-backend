# database uri
# format: dialect+driver://username:password@host:port/database
postgresql: str

# discord OAuth stuff
discord_client_id: int
discord_client_secret: str

# Google OAuth stuff
google_client_id: str
google_client_secret: str

# PASETO private key. Get one using scripts/generate_keys.py
paseto_private_key: str

# URL of the frontend
frontend_url: str

# IPC with the bot
ipc_endpoint: str
ipc_secret: str
