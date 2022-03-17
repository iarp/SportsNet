from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

CACHE_DIR = BASE_DIR / "cache"
LOGGING_DIR = BASE_DIR / "logs"

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, True)
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env.str(
    "DJANGO_SECRET_KEY", "+-8ny_iz$o53(2+m1pb%lfm9)$(40e@ejfya@k_k76!qno3ng%"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = env.str(
    "DJANGO_ALLOWED_HOSTS", "orhc.iarp.ca localhost 127.0.0.1"
).split(" ")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "team",
    "qualifications",
    "crispy_forms",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "sekizai",
    # 'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.facebook',
    # 'allauth.socialaccount.providers.microsoft',
    # 'allauth.socialaccount.providers.linkedin,'
    "iarp_django_utils",
    "django_templated_emailer",
    "phonenumber_field",
    "reversion",
]

if env.bool("DJANGO_LOAD_EXTRA_EXTENSIONS", False):  # pragma: no cover
    INSTALLED_APPS.extend(
        [
            "django_extensions",
        ]
    )

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "sportsnet.auth_backend.LoginRequiresStaffTypeWebAccessTrueBackend",
    # "django.contrib.auth.backends.ModelBackend",
    # "allauth.account.auth_backends.AuthenticationBackend",
]

ROOT_URLCONF = "sportsnet.urls"
SITE_ID = 1
SESSION_COOKIE_NAME = "sportsnet_sessionid"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "sekizai.context_processors.sekizai",
                "sportsnet.template_context.add_season",
                "sportsnet.template_context.add_django_settings",
                "sportsnet.template_context.sys_app_name",
            ],
        },
    },
]

WSGI_APPLICATION = "sportsnet.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {
    "default": env.db(default=f"sqlite:///{BASE_DIR}/db.sqlite3"),
}
if env.str("GITHUB_WORKFLOW", default=None):  # pragma: no cover
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "github_actions",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "127.0.0.1",
            "PORT": "5432",
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "core.User"

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"

USE_I18N = False
LOCALE_PATHS = [BASE_DIR / "locales"]

USE_TZ = True


STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATIC_ROOT = BASE_DIR / "static"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_DIRS = [
    BASE_DIR / "templates" / "static",
]

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "core:index"
LOGOUT_REDIRECT_URL = "core:index"

# ACCOUNT_ADAPTER = 'sportsnet.allauth_adapters.MyOverriddenDefaultAccountAdapter'
# SOCIALACCOUNT_ADAPTER = 'sportsnet.allauth_adapters.MyOverriddenDefaultSocialAccountAdapter'

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGOUT_REDIRECT_URL = LOGOUT_REDIRECT_URL
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# if not DEBUG:
#     ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
            "openid",
        ],
        "AUTH_PARAMS": {
            "access_type": "offline",
            "include_granted_scopes": "true",
        },
    },
    "facebook": {
        "SCOPE": ["email", "public_profile"],
        "FIELDS": [
            "id",
            "email",
            "name",
            "first_name",
            "last_name",
            "verified",
            "locale",
            "timezone",
            "link",
            "gender",
            "updated_time",
        ],
        "VERIFIED_EMAIL": True,
    },
    "microsoft": {
        # 'SCOPE': ['Calendars.ReadWrite', 'Files.ReadWrite', 'Tasks.ReadWrite', 'User.Read'],
        "SCOPE": ["User.Read", "offline_access"],
    },
    "linkedin": {
        "SCOPE": [
            "r_emailaddress",
        ],
        "PROFILE_FIELDS": [
            "id",
            "first-name",
            "last-name",
            "email-address",
        ],
    },
}

CRISPY_TEMPLATE_PACK = "bootstrap4"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

PHONENUMBER_DEFAULT_REGION = "CA"
