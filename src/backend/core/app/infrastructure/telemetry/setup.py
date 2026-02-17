"""OpenTelemetry setup and configuration."""

from __future__ import annotations

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def init_telemetry(settings: object) -> None:
    """Initialize OpenTelemetry with OTLP gRPC exporter and FastAPI instrumentation.

    Configures a TracerProvider with the OTLP gRPC exporter, registers it as the
    global tracer provider, and applies FastAPI auto-instrumentation.

    Args:
        settings: Application settings object. Must expose ``otel_service_name``
            and ``otel_exporter_otlp_endpoint`` attributes.
    """
    resource = Resource.create(
        {"service.name": settings.otel_service_name}  # type: ignore[attr-defined]
    )

    exporter = OTLPSpanExporter(
        endpoint=settings.otel_exporter_otlp_endpoint,  # type: ignore[attr-defined]
        insecure=True,
    )

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)

    FastAPIInstrumentor().instrument()


def get_tracer(name: str) -> trace.Tracer:
    """Return a named tracer from the global tracer provider.

    Args:
        name: Instrumentation scope name, typically ``__name__``.

    Returns:
        A :class:`opentelemetry.trace.Tracer` instance.
    """
    return trace.get_tracer(name)
