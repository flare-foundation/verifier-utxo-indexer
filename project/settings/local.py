from .common import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

MEDIA_ROOT = "/appdata/media/"

DJANGO_ADMIN_PATH = "_admin/"

# django-cors-headers
CORS_ALLOW_ALL_ORIGINS = True

# django-types
from django.db.models.query import QuerySet

for cls in [QuerySet]:
    cls.__class_getitem__ = classmethod(lambda cls, *args, **kwargs: cls)  # type: ignore [attr-defined]
