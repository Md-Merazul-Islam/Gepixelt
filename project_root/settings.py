
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import timedelta
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ['*']  # Allow host

SECRET_KEY = 'django-insecure-&!r7t^bgt0s0geeqfzee&%zb&k4gym9p!vdx)s9r0&#v#i&x%9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = ['*']  # Allow host

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',  # Rest framework

    'corsheaders',
    'django_celery_beat',


    # Local apps
    'auths',
    'products',
    'payments',
    'orders',
    'dashboard',
    'weekorder',
    'autoemail',




    # for superbase data basee
    "whitenoise.runserver_nostatic",

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',


    "corsheaders.middleware.CorsMiddleware",  # corse headers middleware

    # for superbase data basee
    # ...
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # ...
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

ROOT_URLCONF = 'project_root.urls'  # project_root is the name of the project

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates',],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI_APPLICATION = 'project_root.wsgi.application'
WSGI_APPLICATION = 'project_root.wsgi.app'


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# extra settings add from me --------------------------------


# extra settings add from me --------------------------------
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',

]

SITE_ID = 1


LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        "rest_framework.authentication.SessionAuthentication",
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'EXCEPTION_HANDLER': 'utils.utils.custom_exception_handler',


}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=70),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

AUTH_USER_MODEL = 'auths.CustomUser'

SESSION_COOKIE_AGE = 3600  # 1 hour in seconds

# corse
CORS_ALLOW_ALL_ORIGINS = True
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5500',
    'http://127.0.0.1:5501',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://*.127.0.0.1',
    'https://gepixelitfrontend.vercel.app',
   'https://gepixelt.vercel.app',


]

CSRF_TRUSTED_ORIGINS = [
    'https://*.127.0.0.1',
    'http://localhost:8000',
    'http://127.0.0.1:5500',
    'http://127.0.0.1:5501',
    'http://127.0.0.1:8000',
    'http://localhost:3000',
    'http://localhost:5173',
    'https://gepixelitfrontend.vercel.app',
    'https://gepixelt.vercel.app',
]


CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'DELETE',
    'PATCH',
    'OPTIONS'
]


# --- Email  Backend --------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# # for email notification
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')



# ------.env start  ---------------------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 'django-insecure-&!r7t^bgt0s0geeqfzee&%zb&k4gym9p!vdx)s9r0&#v#i&x%9')


DEBUG = True


# ------.env end  ----------------------------------------------------------------------------------------


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# RENDER DATABASES`----------------------------------------------------------------`

# DATABASES = {
#     'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
# }

# # Postgres (local).----------------------------------------------------------------

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'mydb',
#         'USER': 'myuser',
#         'PASSWORD': 'mypassword',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# # Supabase (similar to AWS RDS).----------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.hdpwndhwouuodnkqzffq',
        'PASSWORD': 'viu8@UPQnuAQbKm',
        'HOST': 'aws-0-ap-southeast-1.pooler.supabase.com',
        'PORT': '6543',
    }
}


STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
STATIC_URL = "/static/"
# DigitalOcean Spaces (similar to AWS S3).----------------------------------------------------------------

# # DigitalOcean Spaces Credentials
AWS_S3_ENDPOINT_URL = os.getenv(
    "AWS_S3_ENDPOINT_URL", "https://nyc3.digitaloceanspaces.com")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_REGION = "nyc3"

AWS_S3_ADDRESSING_STYLE = "virtual"


# Public media file access (change ACL if needed)
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
    "ACL": "public-read",
}

# DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MEDIA_URL = f"https://{AWS_S3_ENDPOINT_URL}/"
# DigitalOcean Spaces Bucket URL
MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/"

# Static files (only if using DigitalOcean Spaces for static assets)
# STATIC_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/static/"

STRIPE_TEST_SECRET_KEY = os.getenv("STRIPE_TEST_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")
# STRIPE_TEST_PUBLIC_KEY = os.getenv("STRIPE_TEST_PUBLIC_KEY")


# settings.py

# Celery Configuration
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'  # Redis URL
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']  # Accept only JSON content
CELERY_TASK_SERIALIZER = 'json'  # Task data serialization method
CELERY_TIMEZONE = 'UTC'  # Timezone

PAYPAL_MODE = 'sandbox'  
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_TEST_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_TEST_SECRET_KEY')