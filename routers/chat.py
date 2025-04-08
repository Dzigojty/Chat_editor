from telethon import TelegramClient, __version__ as telethon_version
from telethon.tl.types import InputPeerEmpty, ReactionEmoji
from telethon.tl.functions.messages import SendReactionRequest
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from schemas.user import User
from config import settings
import logging
import asyncio


router = APIRouter(prefix="/chat")
logger = logging.getLogger(__name__)


async def get_all_messages(client, entity):
    all_messages = []
    async for message in client.iter_messages(entity):
        all_messages.append({
            "id": message.id,
            "text": message.text,
            "date": message.date,
            "sender": message.sender_id
        })
        # Опционально: логирование прогресса
        if len(all_messages) % 100 == 0:
            logger.info(f"Загружено {len(all_messages)} сообщений")
    return all_messages


async def send_reaction_safe(client, entity, message_id, reaction):
    """Универсальный метод отправки реакции"""
    try:
        reaction_obj = ReactionEmoji(emoticon=reaction)
        
        if hasattr(client, 'send_reaction'):
            return await client.send_reaction(
                entity=entity,
                message_id=message_id,
                reaction=[reaction_obj]
            )
        
        return await client(SendReactionRequest(
            peer=entity,
            msg_id=message_id,
            reaction=[reaction_obj]
        ))
    except Exception as e:
        logger.error(f"Ошибка отправки реакции: {str(e)}", exc_info=True)
        raise


async def process_dialog(client, dialog):
    try:
        # Условия пропуска диалогов (добавлена проверка на юзера)
        skip_conditions = (
            not dialog.is_user,  # <-- Восстановлена проверка!
            isinstance(dialog.entity, InputPeerEmpty),
            getattr(dialog, 'archived', False)
        )
        
        if any(skip_conditions):
            logger.debug(f"Пропущен диалог: {dialog.name}")
            return None
        
         # Получаем ВСЕ сообщения с пагинацией
        all_messages = []
        offset_id = 0
        has_reactions = False
        
        while True:
            messages = await client.get_messages(
                dialog.entity,
                limit=100,
                offset_id=offset_id
            )
            
            if not messages:
                break
                
            # Проверяем каждое сообщение на наличие реакций
            for message in messages:
                if message.reactions:
                    logger.debug(f"Найдены реакции в чате {dialog.name} (ID сообщения: {message.id})")
                    has_reactions = True
                    break
                    
            if has_reactions:
                return None
                
            all_messages.extend(messages)
            offset_id = messages[-1].id
            await asyncio.sleep(1)  # Задержка между запросами

        print(all_messages)

        if not all_messages:
            logger.debug(f"Пустой чат: {dialog.name}")
            return None

        # Если дошли сюда - реакций нет ни в одном сообщении
        # Отправляем реакцию на последнее сообщение
        last_message = all_messages[0]
        await send_reaction_safe(client, dialog.entity, last_message.id, "👀")
        
        # Задержка между чатами
        await asyncio.sleep(1)
        
        logger.info(f"Обработан диалог: {dialog.name} (Отправлена реакция на сообщение {last_message.id})")
        return dialog.name
    
    except Exception as e:
        logger.error(f"Ошибка обработки {dialog.name}: {str(e)}", exc_info=True)
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
            await client.start()
            
            logger.info(f"Telethon version: {telethon_version}")
            logger.info("Получение списка диалогов...")
            
            # Получаем только диалоги из основной папки
            dialogs = await client.get_dialogs()
            processed = []
            
            for dialog in dialogs:
                result = await process_dialog(client, dialog)
                if result:
                    processed.append(result)
                    logger.info(f"Обработан диалог: {result}")
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "success",
                    "processed_dialogs": processed,
                    "count": len(processed),
                    "telethon_version": telethon_version
                }
            )
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
