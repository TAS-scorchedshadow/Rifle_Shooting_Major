from app import create_app

application = create_app()

# @app.shell_context_processor
# def make_shell_context():
#     return {'db': db, 'User': User, 'Stage': Stage, 'Shot': Shot}