import os
import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Apply CGI module shim patch for Python 3.13+ compatibility
from utils.cgi_shim import apply_patch
if apply_patch():
    logging.info("Applied CGI module shim patch for Python 3.13+ compatibility")

from bot.handlers import router
from services.alert_service import AlertService
from services.resource_service import ResourceService
from api.server import APIServer

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("TelegramBot")

async def register_with_catalog(resource_service, service_ip, service_port):
    """Register the service with the Resource Catalog"""
    service_data = {
        "name": os.getenv("SERVICE_NAME", "TelegramBot"),
        "description": "Telegram Bot for Smart IoT Bolt monitoring and control",
        "endpoint": {
            "url": f"http://{service_ip}:{service_port}",
            "protocol": "REST"
        },
        "healthCheck": f"http://{service_ip}:{service_port}/health",
        "interfaces": [
            {
                "name": "notification",
                "description": "Endpoint to receive notifications from other services",
                "endpoint": f"http://{service_ip}:{service_port}/notification",
                "method": "POST"
            }
        ]
    }
    
    return await resource_service.register_with_catalog(service_data)

async def main():
    # Get configuration from environment variables
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    service_port = int(os.getenv("SERVICE_PORT", 8085))
    service_ip = os.getenv("SERVICE_IP", "127.0.0.1")
    resource_catalog_url = os.getenv("RESOURCE_CATALOG_URL")
    
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        return
    
    # Initialize the bot and dispatcher
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    
    # Store alert service in bot data for access from handlers
    alert_service = AlertService(bot)
    dp["alert_service"] = alert_service
    
    # Initialize services
    resource_service = ResourceService(resource_catalog_url)
    
    # Start the API server (using get_running_loop for Python 3.13 compatibility)
    loop = asyncio.get_running_loop()
    api_server = APIServer(service_ip, service_port, alert_service, loop)
    api_server.start()
    
    # Register with the Resource Catalog
    try:
        await register_with_catalog(resource_service, service_ip, service_port)
    except Exception as e:
        logger.error(f"Failed to register with Resource Catalog: {str(e)}")
    
    # Start the bot
    logger.info("Starting bot")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")