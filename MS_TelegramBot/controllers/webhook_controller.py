import cherrypy
import json
import logging
import os
import sys
from dotenv import load_dotenv
import asyncio

load_dotenv()

class WebhookController:
    def __init__(self, bot_service, notification_service):
        self.bot_service = bot_service
        self.notification_service = notification_service
        self.logger = logging.getLogger("TelegramBot.WebhookController")
        
        # Create a new event loop using the appropriate method based on Python version
        if sys.version_info >= (3, 13):
            self.loop = asyncio.new_event_loop()
            try:
                # Python 3.13+ compatibility
                asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
                asyncio.set_event_loop(self.loop)
            except Exception as e:
                self.logger.warning(f"Error setting event loop: {str(e)}")
        else:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
    
    @cherrypy.expose
    def index(self):
        return "Telegram Bot Webhook is running"
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def webhook(self):
        try:
            update_data = cherrypy.request.json
            self.logger.debug(f"Received update: {json.dumps(update_data)}")
            
            # Process the update asynchronously using aiogram
            if self.bot_service and hasattr(self.bot_service, 'feed_update'):
                # Python 3.13+ compatible way to run coroutine in another thread
                future = asyncio.run_coroutine_threadsafe(
                    self.bot_service.feed_update(update_data),
                    self.loop
                )
                # Prevent exceptions from being silently dropped
                try:
                    future.result(timeout=10)  # Wait for up to 10 seconds
                except asyncio.TimeoutError:
                    self.logger.warning("Webhook processing timed out")
                except Exception as e:
                    self.logger.error(f"Error in webhook processing: {str(e)}")
            else:
                self.logger.warning("Bot service not properly configured for webhook updates")
            
            return "OK"
        except Exception as e:
            self.logger.error(f"Error in webhook: {str(e)}")
            return "Error"
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def notification(self):
        try:
            data = cherrypy.request.json
            self.logger.info(f"Received notification: {json.dumps(data)}")
            
            # Process the notification asynchronously
            if self.notification_service:
                # Python 3.13+ compatible way to run coroutine in another thread
                future = asyncio.run_coroutine_threadsafe(
                    self.notification_service.handle_analytics_notification(data),
                    self.loop
                )
                # Prevent exceptions from being silently dropped
                try:
                    future.result(timeout=10)  # Wait for up to 10 seconds
                except asyncio.TimeoutError:
                    self.logger.warning("Notification processing timed out")
                except Exception as e:
                    self.logger.error(f"Error in notification processing: {str(e)}")
            else:
                self.logger.warning("Notification service not configured")
            
            return {"status": "success"}
        except Exception as e:
            self.logger.error(f"Error in notification endpoint: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def health(self):
        return {"status": "healthy", "service": "TelegramBot"}