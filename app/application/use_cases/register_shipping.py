from ..interfaces.uow import UnitOfWorkProtocol
from ..interfaces.message_broker import MessageProducerProtocol


class RegisterShippingUseCase:
    def __init__(self, uow: UnitOfWorkProtocol, broker: MessageProducerProtocol):
        self.uow = uow
        self.broker = broker

    async def __call__(self) -> None:
        async with self.uow:
            pass
