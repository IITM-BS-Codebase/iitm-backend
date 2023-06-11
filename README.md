# Backend Infrastructure for the IITM B.Sc. Discord

## Setup

### 1. Discord OAuth Setup
1. Navigate to the [discord developer portal](https://discord.com/developers/applications) and create a new app
2. On the sidebar navigate to OAuth2 > General
3. Add `http://localhost:8081/discord/auth/login/callback` as the redirect URL

### 2. Google OAuth Setup
1. Navigate to the [Google developer console](https://console.developers.google.com)
2. Create a new project by going to Select a project > NEW PROJECT on the top left
3. To generate credentials, on the new page that appears, navigate to Credentials and
   click on `+ CREATE CREDENTIALS` on the top and select OAuth Client ID
4. Follow the prompts and answer the questions.
5. Add `http://localhost:8081` to authorized JavaScript origins and
   `http://localhost:8081/google/auth/login/callback` as an authorized redirect URI

### 2. Configuration Variables
1. Create a new file named `config.py` and fill it in according to the instructions in
   the stub file [`config.pyi`](config.pyi)

### Database setup

We use [PostgreSQL](https://www.postgresql.org), so you can install it locally on your
own computer, or opt for a hosted option, whichever is convenient. The format of the
connection string remains the same.

If you use Docker, you can use provided `docker-compose.yml` to spin up a server
quickly.

> :warning: If you don't have Postgres or the Postgres client libraries installed on
> your machine, `psycopg2` will fail to install. To work around this, either install the
> required libraries for your system, or replace that package with `psycopg2-binary` of
> the same version.


## Running the backend

At least Python 3.10 is required.

### Virtual Environments

It is recommended to use a virtual environment to run this app, or any of your python
projects.

1. Create a virtual environment: `python3 -m venv .venv`
2. Activate the environment
   - Unix: `source ./.venv/bin/activate`
   - Windows: `.\.venv\Scripts\activate`

#### Make sure you set `debug=False` in `main.py` when running in prod

- Install the requirements by running `pip install -r requirements.txt`
- Run the backend with `python3 main.py`
