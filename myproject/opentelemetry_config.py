import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor


def configure_opentelemetry():
    """配置OpenTelemetry"""
    # 设置资源信息
    resource = Resource.create(
        attributes={
            "service.name": os.getenv("OTEL_SERVICE_NAME", "my-opentelemetry-service"),
            "deployment.environment": os.getenv("ENVIRONMENT", "development"),
        }
    )

    # 创建Tracer Provider
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # 根据环境决定使用哪种exporter
    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        # 使用OTLP exporter发送到collector
        otlp_exporter = OTLPSpanExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
            insecure=True,  # 在生产环境中应使用TLS
        )
        span_processor = BatchSpanProcessor(otlp_exporter)
    else:
        # 开发环境中使用控制台输出
        console_exporter = ConsoleSpanExporter()
        span_processor = BatchSpanProcessor(console_exporter)

    provider.add_span_processor(span_processor)

    # 自动检测和注入Django和Celery的追踪
    DjangoInstrumentor().instrument()
    CeleryInstrumentor().instrument()

    print("OpenTelemetry configured successfully")


def get_tracer(name):
    """获取tracer实例"""
    return trace.get_tracer(name)