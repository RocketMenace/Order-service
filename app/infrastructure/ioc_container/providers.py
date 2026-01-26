from typing import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases import (CreateOrderUseCase,
                                       CreatePaymentUseCase,
                                       HandlePaymentResponseUseCase,
                                       RegisterShippingUseCase,
                                       ShippingResponseUseCase,
                                       UpdateOrderStatusUseCase)
from app.infrastructure.adapters import (BaseHTTPXClient, CatalogService,
                                         NotificationsService, PaymentsService)
from app.infrastructure.broker import KafkaConsumer, KafkaProducer
from app.infrastructure.config import (Database, HTTPClientSettings,
                                       KafkaConfig, Settings)
from app.infrastructure.uow import UnitOfWork
from app.infrastructure.workers import (InboxWorker, OutboxNotificationsWorker,
                                        OutboxPaymentsWorker,
                                        OutboxShippingWorker)


class ApplicationSettingsProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_app_settings(self) -> Settings:
        return Settings()


class HTTPClientSettingsProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_http_settings(self) -> HTTPClientSettings:
        return HTTPClientSettings()


class DatabaseProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_database(self, settings: Settings) -> Database:
        return Database(url=settings.db_url)


class DatabaseSessionProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_session(
        self, database: Database
    ) -> AsyncGenerator[AsyncSession, None]:
        async with database.get_session() as session:
            yield session


class HTTPClientProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_http_client(self, config: HTTPClientSettings) -> BaseHTTPXClient:
        return BaseHTTPXClient(config=config)


class CatalogServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_catalog_service(
        self, client: BaseHTTPXClient, settings: Settings
    ) -> CatalogService:
        return CatalogService(client=client, settings=settings)


class PaymentsServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_payments_service(
        self, client: BaseHTTPXClient, settings: Settings
    ) -> PaymentsService:
        return PaymentsService(client=client, settings=settings)


class AppPaymentsServiceProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_app_payments_service(self, settings: Settings) -> PaymentsService:
        http_settings = HTTPClientSettings()
        client = BaseHTTPXClient(config=http_settings)
        return PaymentsService(client=client, settings=settings)


class AppNotificationsServiceProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_app_notifications_service(
        self, settings: Settings
    ) -> NotificationsService:
        http_settings = HTTPClientSettings()
        client = BaseHTTPXClient(config=http_settings)
        return NotificationsService(client=client, settings=settings)


class KafkaConfigProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_kafka_config(self) -> KafkaConfig:
        return KafkaConfig()


class KafkaProducerProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_kafka_producer(self, config: KafkaConfig) -> KafkaProducer:
        return KafkaProducer(config=config)


class UnitOfWorkProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_unit_of_work(self, session: AsyncSession) -> UnitOfWork:
        return UnitOfWork(session=session)


class CreateOrderUseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_create_order_use_case(
        self,
        uow: UnitOfWork,
        catalog_service: CatalogService,
    ) -> CreateOrderUseCase:
        return CreateOrderUseCase(
            uow=uow,
            catalog_service=catalog_service,
        )


class CreatePaymentUseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_create_payment_use_case(
        self, uow: UnitOfWork, payments_service: PaymentsService
    ) -> CreatePaymentUseCase:
        return CreatePaymentUseCase(uow=uow, payments_service=payments_service)


class HandlePaymentResponseUseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_handle_payment_response_use_case(
        self, uow: UnitOfWork
    ) -> HandlePaymentResponseUseCase:
        return HandlePaymentResponseUseCase(uow=uow)


class UpdateOrderStatusUseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_update_order_status_use_case(
        self, uow: UnitOfWork
    ) -> UpdateOrderStatusUseCase:
        return UpdateOrderStatusUseCase(uow=uow)


class RegisterShippingUseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_register_shipping_use_case(
        self, uow: UnitOfWork, broker: KafkaProducer
    ) -> RegisterShippingUseCase:
        return RegisterShippingUseCase(uow=uow, broker=broker)


class ShippingResponseUseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_shipping_response_use_case(
        self, uow: UnitOfWork
    ) -> ShippingResponseUseCase:
        return ShippingResponseUseCase(uow=uow)


class OutboxPaymentsWorkerProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_outbox_payment_worker(
        self, database: Database, payments_service: PaymentsService
    ) -> OutboxPaymentsWorker:
        return OutboxPaymentsWorker(
            database=database, payments_service=payments_service
        )


class InboxWorkerProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_inbox_worker(self, database: Database) -> InboxWorker:
        return InboxWorker(database=database)


class OutboxNotificationsWorkerProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_outbox_notifications_worker(
        self, database: Database, notifications_service: NotificationsService
    ) -> OutboxNotificationsWorker:
        return OutboxNotificationsWorker(
            database=database, notifications_service=notifications_service
        )


class OutboxShippingWorkerProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_outbox_shipping_worker(
        self, database: Database, broker: KafkaProducer
    ) -> OutboxShippingWorker:
        return OutboxShippingWorker(database=database, broker=broker)


class KafkaConsumerProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_kafka_consumer(
        self, config: KafkaConfig, use_case: ShippingResponseUseCase
    ) -> KafkaConsumer:
        return KafkaConsumer(config=config, use_case=use_case)
