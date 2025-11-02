import pika
import json
import threading
from app.config import get_settings

settings = get_settings()


class MessageConsumer:
    """Message consumer for handling user events"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
    
    def _connect(self):
        parameters = pika.URLParameters(settings.rabbitmq_url)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        # Declare exchange
        self.channel.exchange_declare(
            exchange='user_events',
            exchange_type='topic',
            durable=True
        )
        
        # Declare queue
        result = self.channel.queue_declare(queue='order_service_user_events', durable=True)
        queue_name = result.method.queue
        
        # Bind queue to exchange with routing patterns
        self.channel.queue_bind(
            exchange='user_events',
            queue=queue_name,
            routing_key='user.*'
        )
        
        return queue_name
    
    def callback(self, ch, method, properties, body):
        """Handle incoming messages"""
        try:
            message = json.loads(body)
            event_type = message.get('event_type')
            
            print(f"[Order Service] Received event: {event_type}")
            print(f"[Order Service] User ID: {message.get('user_id')}")
            print(f"[Order Service] Username: {message.get('username')}")
            
            # Here you can add business logic based on user events
            # For example: cancel orders if user is deleted
            if event_type == 'user.deleted':
                user_id = message.get('user_id')
                print(f"[Order Service] User {user_id} deleted. Consider handling their orders.")
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"[Order Service] Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start_consuming(self):
        """Start consuming messages"""
        queue_name = self._connect()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self.callback
        )
        
        print('[Order Service] Waiting for user events...')
        self.channel.start_consuming()
    
    def start_in_thread(self):
        """Start consumer in a separate thread"""
        consumer_thread = threading.Thread(target=self.start_consuming, daemon=True)
        consumer_thread.start()
        return consumer_thread