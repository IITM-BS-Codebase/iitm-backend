# Backend Infrastructure for the IITM BSc Discord

## Setup

### 1. Discord OAuth Setup
1. Navigate to the [discord developer portal](https://discord.com/developers/applications) and create a new app
2. On the sidebar navigate to OAuth2 > General
3. Add `http://localhost:8081/discord/auth/login/callback` as the redirect URL
4. In the Default Authorization Link section, select custom URL from the drop down and add the same URL as above
5. It should look like this
![image](https://github.com/IITM-BS-Codebase/iitm-backend/assets/42805453/b735a18d-e9d0-4cbd-9352-4eca3f5ddc6e)
6. On the sidebar navigate to OAuth2 > URL generator
7. Pick appropriate scopes, in this case `identify` and `guilds` and choose the previously added URL as the redirect
8. Copy the generated Redirect URL

### 2. Configuration Variables
1. Create a new file named `.env` and add the following
```env
#DISCORD OAUTH DETAILS
DISCORD_CLIENT_ID=PASTE CLIENT ID
DISCORD_CLIENT_SECRET="PASTE CLIENT SECRET"
DISCORD_OAUTH_REDIRECT="http://localhost:8081/discord/auth/login/callback"
DISCORD_OAUTH_URL="PASTE THE LONG GENERATED REDIRECT URL"

FRONTEND_URL="http://localhost:8080/"

#DATABASE
DB_CONNECTION_STRING="postgresql+psycopg2://user:password@hostname/database_name" 

#SECURITY
SECURITY_KEY="something-secret"
JWT_SECRET_KEY="something-secret-but-for-jwt"
```

## Running the backend
#### Make sure you set `debug=False` in `main.py` when running in prod

- Install the requirements by running `pip install -r requirements.txt`
- Run the backend with `python3 main.py`
