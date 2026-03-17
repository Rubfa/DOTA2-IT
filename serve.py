import os

from waitress import serve

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DOTA2SS.settings')

from DOTA2SS.wsgi import application  # noqa: E402


if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8000'))
    threads = int(os.getenv('WAITRESS_THREADS', '4'))
    serve(application, host=host, port=port, threads=threads)
