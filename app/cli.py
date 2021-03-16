import click, os

def register(app):
    @app.cli.group()
    def blueprint():
        """Blueprint creation commands."""
        pass

    @blueprint.command()
    @click.argument('name')
    def create(name):
        """Create new Flask Blueprint"""
        bp_name = os.path.abspath(os.path.dirname(__name__)) + f'/app/blueprints/{name}'
        try:
            if not os.path.exists(bp_name):
                os.makedirs(bp_name)
                init_file = open(f'{bp_name}/__init__.py', 'w')
                init_file.close()
                views_file = open(f'{bp_name}/views.py', 'w')
                views_file.close()
                models_file = open(f'{bp_name}/models.py', 'w')
                print('Blueprint created successfully.')
        except Exception as error:
            print(f"Something went wrong with creating the Blueprint {bp_name}.")
            print(error)