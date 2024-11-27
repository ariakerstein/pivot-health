from flask.cli import FlaskGroup
from app import app, db
from flask_migrate import init, migrate, upgrade

cli = FlaskGroup(app)

@cli.command("init_db")
def init_db():
    """Initialize the database."""
    init()
    migrate()
    upgrade()

if __name__ == '__main__':
    cli()
