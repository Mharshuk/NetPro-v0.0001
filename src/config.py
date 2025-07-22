import os
from dataclasses import dataclass

@dataclass
class Config:
    kafka_bootstrap: str = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
    kafka_topic: str = os.getenv("KAFKA_TOPIC", "flows.raw-json")
    kafka_ssl_cert: str | None = os.getenv("KAFKA_SSL_CERT")
    kafka_ssl_key: str | None = os.getenv("KAFKA_SSL_KEY")
    kafka_ssl_ca: str | None = os.getenv("KAFKA_SSL_CA")

    aws_s3_bucket: str | None = os.getenv("AWS_S3_BUCKET")
    aws_region: str | None = os.getenv("AWS_REGION")
    aws_access_key: str | None = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key: str | None = os.getenv("AWS_SECRET_ACCESS_KEY")

    azure_connstr: str | None = os.getenv("AZURE_BLOB_CONNSTR")

    gcp_project: str | None = os.getenv("GCP_PROJECT")
    gcp_sub_id: str | None = os.getenv("GCP_SUB_ID")
    google_credentials: str | None = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    mirror_tls_cert: str | None = os.getenv("MIRROR_TLS_CERT")
    mirror_tls_key: str | None = os.getenv("MIRROR_TLS_KEY")
    mirror_port: int = int(os.getenv("MIRROR_PORT", "443"))
    buffer_dir: str = os.getenv("BUFFER_DIR", "/data/buffer")
