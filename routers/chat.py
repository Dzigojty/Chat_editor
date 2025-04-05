from telethon import TelegramClient, __version__ as telethon_version
from telethon.tl.types import InputPeerEmpty
from telethon.tl.functions.messages import SendReactionRequest
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from telethon.tl.types import ReactionEmoji  # Добавляем импорт
from schemas.user import User
from config import settings
import logging
import asyncio

router = APIRouter(prefix="/chat")
logger = logging.getLogger(__name__)

async def send_reaction_safe(client, entity, message_id, reaction):
    """Универсальный метод отправки реакции"""
    try:
        # Создаем объект реакции
        reaction_obj = ReactionEmoji(emoticon=reaction)
        
        # Для Telethon 1.28+
        if hasattr(client, 'send_reaction'):
            return await client.send_reaction(
                entity=entity,
                message_id=message_id,
                reaction=[reaction_obj]  # Передаем список реакций
            )
        
        # Для старых версий
        return await client(SendReactionRequest(
            peer=entity,
            msg_id=message_id,
            reaction=[reaction_obj]  # Всегда список
        ))
    except Exception as e:
        logger.error(f"Ошибка отправки реакции: {str(e)}")
        raise

async def process_dialog(client, dialog):
    try:
        # Пропускаем не-пользователей и пустые диалоги
        if not dialog.is_user or isinstance(dialog.entity, InputPeerEmpty):
            return None
        
        # Получаем последнее сообщение
        messages = await client.get_messages(dialog.entity, limit=1)
        if not messages:
            return None
        
        last_msg = messages[0]
        
        # Пропускаем сообщения с реакциями
        if last_msg.reactions:
            return None
        
        # Отправляем реакцию
        await send_reaction_safe(client, dialog.entity, last_msg.id, "👀")
        
        # Добавляем задержку для избежания FloodWait
        await asyncio.sleep(1)
        
        return dialog.name
    
    except Exception as e:
        logger.error(f"Ошибка обработки диалога: {str(e)}")
        return None

@router.get("/change/", response_model=dict)
async def change_chat():
    """Добавление реакций в последние сообщения диалогов"""
    try:
        async with TelegramClient(
            session='session_name',
            api_id=settings.API_ID,
            api_hash=settings.API_HASH
        ) as client:
            # Инициализация соединения
            await client.start()
            
            logger.info(f"Используется Telethon версии {telethon_version}")
            logger.info("Получение списка диалогов...")
            
            # Получаем и обрабатываем диалоги
            dialogs = await client.get_dialogs()
            processed = []
            
            for dialog in dialogs:
                dialog_name = await process_dialog(client, dialog)
                if dialog_name:
                    processed.append(dialog_name)
                    logger.info(f"Обработан диалог: {dialog_name}")
            
            return {
                "status": "success",
                "processed_dialogs": processed,
                "count": len(processed),
                "telethon_version": telethon_version
            }
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )