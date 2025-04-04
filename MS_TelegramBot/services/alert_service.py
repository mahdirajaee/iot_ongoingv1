import logging
import asyncio
from typing import Dict, Any, Optional
from aiogram import Bot
from aiogram.enums import ParseMode

class AlertService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = logging.getLogger("TelegramBot.AlertService")
        self.admin_chat_ids = []  # Should be loaded from a config or database
        
    async def add_admin_chat(self, chat_id: int):
        """Add a chat ID to the admin list"""
        if chat_id not in self.admin_chat_ids:
            self.admin_chat_ids.append(chat_id)
            self.logger.info(f"Added chat ID {chat_id} to admin list")
            return True
        return False
        
    async def remove_admin_chat(self, chat_id: int):
        """Remove a chat ID from the admin list"""
        if chat_id in self.admin_chat_ids:
            self.admin_chat_ids.remove(chat_id)
            self.logger.info(f"Removed chat ID {chat_id} from admin list")
            return True
        return False
    
    async def send_alert(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Send an alert message to all admin chats"""
        if not self.admin_chat_ids:
            self.logger.warning("No admin chat IDs configured, alert not sent")
            return
            
        formatted_message = message
        if data:
            # Add data details to the message
            for key, value in data.items():
                formatted_message += f"\n{key}: {value}"
                
        for chat_id in self.admin_chat_ids:
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=formatted_message,
                    parse_mode=ParseMode.HTML
                )
                self.logger.info(f"Alert sent to chat {chat_id}")
            except Exception as e:
                self.logger.error(f"Failed to send alert to chat {chat_id}: {str(e)}")
    
    async def handle_analytics_notification(self, data: Dict[str, Any]):
        """Handle notifications from the Analytics service"""
        alert_type = data.get("type", "unknown")
        message = data.get("message", "No message provided")
        
        if alert_type == "anomaly":
            await self.send_alert(f"⚠️ <b>Anomaly Detected</b>: {message}", data)
        elif alert_type == "threshold":
            await self.send_alert(f"🔴 <b>Threshold Alert</b>: {message}", data)
        elif alert_type == "prediction":
            await self.send_alert(f"📊 <b>Prediction Alert</b>: {message}", data)
        else:
            await self.send_alert(f"ℹ️ <b>Notification</b>: {message}", data) 