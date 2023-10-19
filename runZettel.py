import os

from flask import Flask

from flask_cors import CORS


def create_app(test_config=None):
    # create and config the app
    app = Flask(__name__, instance_relative_config=True)
    
    CORS(app, origins='*')
    app.config.from_mapping(
        #this should be overidden w/ random value when deploying for security
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'zettapp.sqlite')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test_config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/health")
    def health():
        return "<h1>Zippidy Do Dah!!</h1>"
        #what else could I have RUN here that exposes some good stuff??

    from . import db
    db.init_app(app)
    
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app

if __name__ == "__main__":
    app = create_app()
    
