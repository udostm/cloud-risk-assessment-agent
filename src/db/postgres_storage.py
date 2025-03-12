import os
import asyncio
from typing import Any, Dict, Union

import psycopg2
from psycopg2.extras import execute_values

from chainlit import make_async
from chainlit.data.storage_clients.base import BaseStorageClient
from chainlit.logger import logger

service_host = os.getenv("SERVICE_HOST", "http://localhost:8000")

class PostgreSQLStorageClient(BaseStorageClient):
    """
    Class to enable PostgreSQL blob file storage
    """

    def __init__(self, database_url: str):
        try:
            self.conn = psycopg2.connect(database_url)
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            logger.info("PostgreSQLStorageClient initialized")
        except Exception as e:
            logger.warn(f"PostgreSQLStorageClient initialization error: {e}")

    def sync_upload_file(self, object_key: str, data: Union[bytes, str], mime: str = "application/octet-stream") -> Dict[str, Any]:
        try:
            uuid = object_key.split('/')[0]
            sql = "INSERT INTO blob_storage (object_key, data, mime_type) VALUES (%s, %s, %s) ON CONFLICT (object_key) DO UPDATE SET data = EXCLUDED.data, mime_type = EXCLUDED.mime_type"
            self.cursor.execute(sql, (uuid, psycopg2.Binary(data), mime))
            url = f"{service_host}/blob/{uuid}"
            return {"object_key": object_key, "url": url}
        except Exception as e:
            logger.warn(f"PostgreSQLStorageClient, upload_file error: {e}")
            return {}

    async def upload_file(self, object_key: str, data: Union[bytes, str], mime: str = "application/octet-stream", overwrite: bool = True) -> Dict[str, Any]:
        return await make_async(self.sync_upload_file)(object_key, data.encode('utf-8'), mime)

    def sync_download_file(self, object_key: str) -> str:
        try:
            self.cursor.execute("SELECT data FROM blob_storage WHERE object_key = %s", (object_key,))
            blob = self.cursor.fetchone()
            if blob:
                return blob[0].tobytes()  # Return bytes directly
            return ""
        except Exception as e:
            logger.warn(f"PostgreSQLStorageClient, get_read_url error: {e}")
            return object_key

    async def download_file(self, object_key: str) -> str:
        return await make_async(self.sync_download_file)(object_key)

    async def get_read_url(self, object_key: str) -> str:
        uuid = object_key.split('/')[0]
        return f"{service_host}/blob/{uuid}"

    def sync_delete_file(self, object_key: str) -> bool:
        try:
            uuid = object_key.split('/')[0]
            self.cursor.execute("DELETE FROM blob_storage WHERE object_key = %s", (uuid,))
            return True
        except Exception as e:
            logger.warn(f"PostgreSQLStorageClient, delete_file error: {e}")
            return False

    async def delete_file(self, object_key: str) -> bool:
        return await make_async(self.sync_delete_file)(object_key)

