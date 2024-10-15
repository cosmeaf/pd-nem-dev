# core/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import warnings
from celery.utils.log import get_logger

logger = get_logger(__name__)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

# Defina o módulo de configurações do Django para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Crie a aplicação Celery
app = Celery('core')

# Carregue as configurações do Celery a partir das configurações do Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobrir automaticamente as tasks definidas nos apps instalados
app.autodiscover_tasks()
