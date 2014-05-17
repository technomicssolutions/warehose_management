DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'smartbook',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'hr',
        'PASSWORD': 'root',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '5433',                      # Set to empty string for default.
    }
}
