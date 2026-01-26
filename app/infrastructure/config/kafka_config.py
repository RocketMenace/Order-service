from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    bootstrap_server: str = Field(default="", alias="KAFKA_BOOTSTRAP")
    default_topic: str = Field(
        default="student_system_order.events", alias="KAFKA_TOPIC"
    )
