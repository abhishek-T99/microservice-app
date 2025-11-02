import pika
from app.config import get_settings
from app.schemas.order import OrderEvent

settings = get_settings()


class MessagePublisher:
    """Message publisher following Dependency Inversion Principle"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        parameters = pika.URLParameters(settings.rabbitmq_url)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        # Declare exchange
        self.channel.exchange_declare(
            exchange='order_events',
            exchange_type='topic',
            durable=True
        )
    
    def publish_order_event(self, event: OrderEvent):
        if not self.channel or self.channel.is_closed:
            self._connect()
        
        routing_key = event.event_type
        message = event.model_dump_json()
        
        self.channel.basic_publish(
            exchange='order_events',
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # persistent
                content_type='application/json'
            )
        )
    
    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()