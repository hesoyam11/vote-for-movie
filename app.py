from flask import Flask
from api1 import blueprint as api1

app = Flask(__name__)
app.config["RESTPLUS_VALIDATE"] = True

app.register_blueprint(api1)

if __name__ == "__main__":
    app.run(debug=True)
