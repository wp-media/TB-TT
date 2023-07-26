from sources.TechTeamBot import TechTeamBot
from flask import Flask

# This `app` represents your existing Flask app
flask_app = Flask(__name__)
app = TechTeamBot(flask_app)
app.setup()
# Start the server on port 3000
if __name__ == "__main__":
    app.run()
