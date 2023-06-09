import logging
from src import create_app, setup_auth, setup_routes    

logger = logging.basicConfig()

app, api = create_app() 
setup_auth(app)
setup_routes(app)

if __name__ == '__main__':
    app.run(port=8081, debug=True)
