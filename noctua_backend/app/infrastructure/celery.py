"""Configuração da fila de tarefas assíncronas do Noctua."""

import os

from celery import Celery

aplicacao_celery = Celery(
    "noctua",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    include=["app.infrastructure.tarefas_documento"],
)
aplicacao_celery.conf.update(
    task_track_started=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)
