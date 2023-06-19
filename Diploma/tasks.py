import os

from invoke import task, run


@task
def run(ctx):
    port = int(os.getenv("PORT", "80"))
    ctx.run(f'python manage.py runserver 0.0.0.0:{port}')
