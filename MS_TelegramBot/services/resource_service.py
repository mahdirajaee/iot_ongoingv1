import logging
import aiohttp
import json
from typing import Dict, Any, Optional

class ResourceService:
    def __init__(self, catalog_url: Optional[str] = None):
        self.catalog_url = catalog_url
        self.logger = logging.getLogger("TelegramBot.ResourceService")
        
    async def register_with_catalog(self, service_data: Dict[str, Any]) -> bool:
        """Register the service with the Resource Catalog"""
        if not self.catalog_url:
            self.logger.warning("Resource Catalog URL not configured, registration skipped")
            return False
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.catalog_url}/api/services",
                    json=service_data
                ) as response:
                    if response.status == 200 or response.status == 201:
                        data = await response.json()
                        self.logger.info(f"Successfully registered with Resource Catalog, ID: {data.get('id')}")
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Failed to register with Resource Catalog: {error_text}")
                        return False
        except Exception as e:
            self.logger.error(f"Exception during registration with Resource Catalog: {str(e)}")
            return False
            
    async def get_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service information from the Resource Catalog"""
        if not self.catalog_url:
            self.logger.warning("Resource Catalog URL not configured, service lookup skipped")
            return None
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.catalog_url}/api/services",
                    params={"name": service_name}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        services = data.get("services", [])
                        if services:
                            self.logger.info(f"Found service: {service_name}")
                            return services[0]
                        else:
                            self.logger.warning(f"Service not found: {service_name}")
                            return None
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Failed to get service from Resource Catalog: {error_text}")
                        return None
        except Exception as e:
            self.logger.error(f"Exception during service lookup from Resource Catalog: {str(e)}")
            return None 