from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    @app.get("/")
    def index():
        return {
            "code": 200,
            "message": "E-commerce Analysis System is running",
            "data": None,
        }

    @app.get("/health")
    def health():
        return {
            "code": 200,
            "message": "ok",
            "data": {
                "service": "flask"
            },
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)