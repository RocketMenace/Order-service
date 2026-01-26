from dishka import make_async_container

from app.infrastructure.ioc_container.providers import (
    ApplicationSettingsProvider, AppNotificationsServiceProvider,
    AppPaymentsServiceProvider, DatabaseProvider, DatabaseSessionProvider,
    HTTPClientProvider, HTTPClientSettingsProvider, InboxWorkerProvider,
    KafkaConfigProvider, KafkaConsumerProvider, KafkaProducerProvider,
    OutboxNotificationsWorkerProvider, OutboxPaymentsWorkerProvider,
    OutboxShippingWorkerProvider, ShippingResponseUseCaseProvider,
    UnitOfWorkProvider)


def create_workers_container():
    return make_async_container(
        ApplicationSettingsProvider(),
        HTTPClientSettingsProvider(),
        DatabaseProvider(),
        HTTPClientProvider(),
        AppPaymentsServiceProvider(),
        AppNotificationsServiceProvider(),
        KafkaConfigProvider(),
        KafkaProducerProvider(),
        KafkaConsumerProvider(),
        InboxWorkerProvider(),
        OutboxPaymentsWorkerProvider(),
        OutboxNotificationsWorkerProvider(),
        OutboxShippingWorkerProvider(),
        ShippingResponseUseCaseProvider(),
        UnitOfWorkProvider(),
        DatabaseSessionProvider(),
    )
