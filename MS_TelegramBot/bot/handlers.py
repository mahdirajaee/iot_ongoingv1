import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from typing import Dict, Any

router = Router()
logger = logging.getLogger("TelegramBot.Handlers")

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle the /start command"""
    await message.answer(
        "👋 Welcome to the Smart IoT Bolt monitoring bot!\n\n"
        "I can help you monitor your IoT devices and receive notifications about anomalies.\n\n"
        "Available commands:\n"
        "/status - Get current system status\n"
        "/subscribe - Subscribe to alerts\n"
        "/unsubscribe - Unsubscribe from alerts\n"
        "/help - Show this help message"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle the /help command"""
    await message.answer(
        "📖 <b>Available Commands</b>\n\n"
        "/status - Get current system status\n"
        "/subscribe - Subscribe to alerts\n"
        "/unsubscribe - Unsubscribe from alerts\n"
        "/help - Show this help message"
    )

@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
    """Handle the /subscribe command"""
    # Get the alert service from the bot_data
    alert_service = message.bot.get("alert_service")
    if not alert_service:
        logger.error("Alert service not configured")
        await message.answer("⚠️ Bot configuration error. Please contact the administrator.")
        return
    
    # Add the chat to the admin list
    success = await alert_service.add_admin_chat(message.chat.id)
    if success:
        await message.answer("✅ You have been subscribed to alerts!")
    else:
        await message.answer("ℹ️ You are already subscribed to alerts.")

@router.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: Message):
    """Handle the /unsubscribe command"""
    # Get the alert service from the bot_data
    alert_service = message.bot.get("alert_service")
    if not alert_service:
        logger.error("Alert service not configured")
        await message.answer("⚠️ Bot configuration error. Please contact the administrator.")
        return
    
    # Remove the chat from the admin list
    success = await alert_service.remove_admin_chat(message.chat.id)
    if success:
        await message.answer("✅ You have been unsubscribed from alerts!")
    else:
        await message.answer("ℹ️ You are not subscribed to alerts.")

@router.message(Command("status"))
async def cmd_status(message: Message):
    """Handle the /status command"""
    # Here you would typically fetch status from other services
    await message.answer(
        "📊 <b>System Status</b>\n\n"
        "🟢 All systems operational\n"
        "🔄 Last update: just now"
    )

@router.message()
async def echo(message: Message):
    """Handle any other message"""
    await message.answer(
        "I'm not sure what you mean. Try using one of the available commands:\n"
        "/status, /subscribe, /unsubscribe, /help"
    ) 