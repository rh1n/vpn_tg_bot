# app/services/xui.py
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from app.config.settings import settings
from app.utils.logger import logger
import uuid

class XUIService:
    def __init__(self):
        self.base_url = settings.PANEL_URL.rstrip('/')
        self.username = settings.PANEL_USERNAME
        self.password = settings.PANEL_PASSWORD
        self.inbound_id = settings.PANEL_INBOUND_ID
        self.session: Optional[aiohttp.ClientSession] = None
        self.token: Optional[str] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def login(self) -> bool:
        """Авторизация в панели 3x-ui"""
        try:
            url = f"{self.base_url}/login"
            data = {
                "username": self.username,
                "password": self.password
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        # Токен может быть в cookies или в ответе
                        # В зависимости от реализации панели
                        self.token = result.get("obj", {}).get("token")
                        logger.info("Successfully logged in to 3x-ui panel")
                        return True
                    else:
                        logger.error(f"Login failed: {result.get('msg')}")
                        return False
                else:
                    logger.error(f"Login request failed with status {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False

    async def _make_request(self, method: str, url: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """Выполнение запроса с retry-логикой"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            
        for attempt in range(3):
            try:
                async with self.session.request(method, url, headers=headers, **kwargs) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 401:
                        # Повторная авторизация
                        if await self.login():
                            continue
                        else:
                            return None
                    else:
                        logger.warning(f"Request failed with status {response.status}")
            except aiohttp.ClientError as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка
                continue
            except Exception as e:
                logger.error(f"Unexpected error during request: {e}")
                break
        return None

    async def create_client(self, email: str) -> Optional[Dict[str, Any]]:
        """Создание нового клиента"""
        try:
            url = f"{self.base_url}/panel/api/inbounds/addClient"
            
            # Генерируем уникальный UUID для клиента
            client_uuid = str(uuid.uuid4())
            
            data = {
                "id": self.inbound_id,
                "settings": {
                    "clients": [
                        {
                            "id": client_uuid,
                            "email": email,
                            "enable": True,
                            "tgId": "",
                            "subId": ""
                        }
                    ]
                }
            }
            
            response = await self._make_request("POST", url, json=data)
            if response and response.get("success"):
                logger.info(f"Client created successfully: {email}")
                # Возвращаем UUID и другую информацию
                return {
                    "uuid": client_uuid,
                    "email": email,
                    "success": True
                }
            else:
                error_msg = response.get("msg") if response else "Unknown error"
                logger.error(f"Failed to create client: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating client: {e}")
            return None

    async def delete_client(self, client_uuid: str) -> bool:
        """Удаление клиента"""
        try:
            url = f"{self.base_url}/panel/api/inbounds/{self.inbound_id}/delClient/{client_uuid}"
            
            response = await self._make_request("POST", url)
            if response and response.get("success"):
                logger.info(f"Client deleted successfully: {client_uuid}")
                return True
            else:
                error_msg = response.get("msg") if response else "Unknown error"
                logger.error(f"Failed to delete client: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting client: {e}")
            return False

    async def get_client(self, client_uuid: str) -> Optional[Dict[str, Any]]:
        """Получение информации о клиенте"""
        try:
            # В 3x-ui API информация о клиентах обычно получается через получение inbound
            url = f"{self.base_url}/panel/api/inbounds/get/{self.inbound_id}"
            
            response = await self._make_request("GET", url)
            if response and response.get("success"):
                inbound_data = response.get("obj", {})
                clients = inbound_data.get("clientStats", [])
                
                for client in clients:
                    if client.get("id") == client_uuid:
                        return client
                        
                logger.warning(f"Client not found: {client_uuid}")
                return None
            else:
                error_msg = response.get("msg") if response else "Unknown error"
                logger.error(f"Failed to get client info: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting client info: {e}")
            return None

    async def generate_vless_reality_link(self, client_uuid: str, email: str) -> str:
        """Генерация VLESS Reality ссылки"""
        # В реальной реализации здесь должна быть логика генерации ссылки
        # на основе конфигурации сервера
        # Для примера возвращаем шаблон
        
        # Пример формата VLESS Reality ссылки:
        # vless://uuid@server:port?encryption=none&security=reality&sni=example.com&fp=chrome&pbk=public_key&sid=short_id&type=grpc&serviceName=service_name#email
        
        # В реальной реализации эти параметры должны браться из конфигурации сервера
        server_address = "your-server.com"
        server_port = "443"
        sni = "example.com"
        fp = "chrome"
        pbk = "your_public_key"
        sid = "short_id"
        type = "grpc"
        service_name = "service_name"
        
        link = (
            f"vless://{client_uuid}@{server_address}:{server_port}?"
            f"encryption=none&security=reality&sni={sni}&fp={fp}&pbk={pbk}&sid={sid}"
            f"&type={type}&serviceName={service_name}#{email}"
        )
        
        return link
