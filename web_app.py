from flask import Flask, render_template
from dotenv import load_dotenv

from config.loader import get_setting, load_settings
from routes.recap_routes import recap_bp


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)

    settings = load_settings()
    max_upload_mb = int(get_setting(settings, ["server", "max_upload_mb"], 200))
    app.config["MAX_CONTENT_LENGTH"] = max_upload_mb * 1024 * 1024

    app.register_blueprint(recap_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
