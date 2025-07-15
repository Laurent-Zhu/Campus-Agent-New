"""
WSGI config for campus_agent project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

import logging
logging.basicConfig(level=logging.DEBUG)  # 启用调试日志
logger = logging.getLogger(__name__)

try:
    from django.core.wsgi import get_wsgi_application
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_agent.settings')
    application = get_wsgi_application()
except Exception as e:
    logger.error(f"WSGI 应用加载失败: {str(e)}", exc_info=True)
    raise
