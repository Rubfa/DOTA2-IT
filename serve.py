import os
import shutil
from pathlib import Path

import django
from waitress import serve

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DOTA2SS.settings')

from django.conf import settings  # noqa: E402
from django.core.management import call_command  # noqa: E402


def bootstrap_sqlite_database():
    database = settings.DATABASES['default']
    if database.get('ENGINE') != 'django.db.backends.sqlite3':
        return

    target_path = Path(database['NAME'])
    seed_path = Path(settings.BASE_DIR) / 'db.sqlite3'

    print(f'Using SQLite database: {target_path}')

    if target_path.exists():
        print('SQLite database already exists in persistent storage.')
        return

    target_path.parent.mkdir(parents=True, exist_ok=True)

    if seed_path.exists() and seed_path.resolve() != target_path.resolve():
        shutil.copy2(seed_path, target_path)
        print(f'Copied seed database from {seed_path} to {target_path}')


def bootstrap_django():
    django.setup()
    bootstrap_sqlite_database()
    call_command('migrate', interactive=False)
    call_command('collectstatic', interactive=False, verbosity=0)
    print('Static files collected.')


def load_application():
    from DOTA2SS.wsgi import application

    return application


if __name__ == '__main__':
    bootstrap_django()
    application = load_application()
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8000'))
    threads = int(os.getenv('WAITRESS_THREADS', '4'))
    serve(application, host=host, port=port, threads=threads)
