"""Sentry and OpenTelemetry bootstrap (spec 13 §3, §4). Both are optional locally."""

from typing import Any

import sentry_sdk
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio

from app.core.config import Settings
from app.core.redaction import scrub
from app.core.request_context import get_request_id


def sentry_before_send(event: dict[str, Any], _hint: dict[str, Any]) -> dict[str, Any] | None:
    request_id = get_request_id()
    if request_id:
        event.setdefault("tags", {})["request_id"] = request_id
    for key in ("request", "extra", "contexts", "breadcrumbs", "user"):
        if key in event:
            event[key] = scrub(event[key])
    return event


def init_sentry(settings: Settings) -> None:
    if not settings.sentry_dsn:
        return
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment or settings.app_env,
        release=settings.release,
        traces_sample_rate=0.0,  # tracing goes through OTel
        send_default_pii=False,
        before_send=sentry_before_send,  # type: ignore[arg-type]
    )


def init_tracing(app: FastAPI, settings: Settings) -> None:
    if not settings.otel_exporter_otlp_endpoint:
        return
    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": settings.service_name,
                "service.version": settings.release,
                "deployment.environment": settings.app_env,
            }
        ),
        sampler=ParentBasedTraceIdRatio(settings.otel_trace_sample_rate),
    )
    # The exporter reads OTEL_EXPORTER_OTLP_ENDPOINT / _HEADERS from the environment.
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(
        app, tracer_provider=provider, excluded_urls="healthz,readyz"
    )
