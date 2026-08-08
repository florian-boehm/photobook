"""Service for streaming media files."""

import logging
from pathlib import Path
from typing import AsyncGenerator, Optional

from app.core.config import settings
from app.services.mapping_service import mapping_service

logger = logging.getLogger(__name__)


class StreamingService:
    """Service for streaming media files to clients."""
    
    def __init__(self, chunk_size: Optional[int] = None):
        """Initialize the streaming service."""
        self.chunk_size = chunk_size or settings.chunk_size
    
    async def stream_file(
        self,
        album: str,
        file_id: int,
    ) -> AsyncGenerator[bytes, None]:
        """Stream a media file in chunks."""
        file_path = mapping_service.get_file_path(album, file_id)
        
        if file_path is None or not file_path.exists():
            logger.error(f"File not found: album={album}, file_id={file_id}")
            raise FileNotFoundError(f"Media file not found: {album}/{file_id}")
        
        if not file_path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            raise ValueError(f"Path is not a file: {file_path}")
        
        logger.info(f"Streaming file: {file_path} (album={album}, file_id={file_id})")
        
        try:
            with open(file_path, "rb") as file:
                while True:
                    chunk = file.read(self.chunk_size)
                    if not chunk:
                        break
                    yield chunk
        
        except Exception as e:
            logger.error(f"Error streaming file {file_path}: {e}")
            raise
    
    async def get_file_info(
        self,
        album: str,
        file_id: int,
    ) -> dict:
        """Get information about a media file."""
        file_path = mapping_service.get_file_path(album, file_id)
        
        if file_path is None or not file_path.exists():
            raise FileNotFoundError(f"Media file not found: {album}/{file_id}")
        
        stat = file_path.stat()
        
        # Determine content type
        content_type = self._get_content_type(file_path)
        
        return {
            "album": album,
            "file_id": file_id,
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": stat.st_size,
            "content_type": content_type,
            "is_video": content_type.startswith("video/"),
            "is_audio": content_type.startswith("audio/"),
            "is_image": content_type.startswith("image/"),
        }
    
    def _get_content_type(self, file_path: Path) -> str:
        """Determine the MIME type based on file extension."""
        from app.services.mapping_service import MappingService
        
        # Reuse the logic from MappingService
        service = MappingService()
        return service._get_content_type(file_path)
    
    async def get_range(
        self,
        album: str,
        file_id: int,
        start: int = 0,
        end: Optional[int] = None,
    ) -> AsyncGenerator[bytes, None]:
        """Stream a specific range of bytes from a file (for HTTP range requests)."""
        file_path = mapping_service.get_file_path(album, file_id)
        
        if file_path is None or not file_path.exists():
            raise FileNotFoundError(f"Media file not found: {album}/{file_id}")
        
        file_size = file_path.stat().st_size
        
        # Handle end range
        if end is None or end >= file_size:
            end = file_size - 1
        
        # Validate range
        if start < 0 or start >= file_size:
            raise ValueError(f"Invalid start range: {start}")
        if end < start:
            raise ValueError(f"Invalid end range: {end}")
        
        logger.info(f"Streaming range {start}-{end} from {file_path}")
        
        try:
            with open(file_path, "rb") as file:
                file.seek(start)
                remaining = end - start + 1
                
                while remaining > 0:
                    chunk_size = min(self.chunk_size, remaining)
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
                    remaining -= len(chunk)
        
        except Exception as e:
            logger.error(f"Error streaming range from {file_path}: {e}")
            raise


# Global streaming service instance
streaming_service = StreamingService()
