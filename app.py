from sources.TechTeamBot import TechTeamBot
from flask import Flask
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# This `app` represents your existing Flask app
flask_app = Flask(__name__)
app = TechTeamBot(flask_app)
app.setup()
# Start the server on port 3000
if __name__ == "__main__":
    app.run(host='0.0.0.0')
