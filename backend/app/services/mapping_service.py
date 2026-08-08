"""Service for managing media file mappings."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.core.config import settings
from app.models.media import MediaFileInfo, MediaMapping

logger = logging.getLogger(__name__)


class MappingService:
    """Service for loading, saving, and querying media file mappings."""
    
    def __init__(self, mapping_file_path: Optional[Path] = None):
        """Initialize the mapping service."""
        self.mapping_file_path = mapping_file_path or settings.mapping_file_path
        self._mapping: Optional[MediaMapping] = None
        self._loaded = False
    
    def _ensure_loaded(self) -> None:
        """Ensure the mapping is loaded from disk."""
        if not self._loaded:
            self.load_mapping()
    
    def load_mapping(self) -> MediaMapping:
        """Load the mapping from the JSON file."""
        try:
            if self.mapping_file_path.exists():
                with open(self.mapping_file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._mapping = MediaMapping(**data)
            else:
                # Create empty mapping
                self._mapping = MediaMapping()
                self.save_mapping()
            
            self._loaded = True
            logger.info(f"Loaded mapping from {self.mapping_file_path}")
            return self._mapping
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse mapping file: {e}")
            self._mapping = MediaMapping()
            self._loaded = True
            return self._mapping
        except Exception as e:
            logger.error(f"Failed to load mapping: {e}")
            self._mapping = MediaMapping()
            self._loaded = True
            return self._mapping
    
    def save_mapping(self) -> bool:
        """Save the current mapping to disk."""
        if self._mapping is None:
            self._mapping = MediaMapping()
        
        try:
            # Ensure parent directory exists
            self.mapping_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.mapping_file_path, "w", encoding="utf-8") as f:
                json.dump(self._mapping.model_dump(), f, indent=2)
            
            logger.info(f"Saved mapping to {self.mapping_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save mapping: {e}")
            return False
    
    def get_mapping(self) -> MediaMapping:
        """Get the current mapping."""
        self._ensure_loaded()
        return self._mapping
    
    def get_file_path(self, album: str, file_id: int) -> Optional[Path]:
        """Get the absolute file path for a given album and file ID."""
        self._ensure_loaded()
        
        if self._mapping is None:
            return None
        
        relative_path = self._mapping.get_file_path(album, file_id)
        if relative_path is None:
            return None
        
        # Convert to absolute path
        full_path = Path(relative_path)
        if not full_path.is_absolute():
            full_path = settings.media_root_path / full_path
        
        return full_path
    
    def get_album_files(self, album: str) -> List[MediaFileInfo]:
        """Get all files for a specific album with metadata."""
        self._ensure_loaded()
        
        if self._mapping is None:
            return []
        
        album_files = self._mapping.get_album_files(album)
        if not album_files:
            return []
        
        result = []
        for file_id, relative_path in album_files.items():
            full_path = Path(relative_path)
            if not full_path.is_absolute():
                full_path = settings.media_root_path / full_path
            
            if full_path.exists():
                file_info = MediaFileInfo(
                    id=file_id,
                    album=album,
                    file_path=full_path,
                    file_name=full_path.name,
                    file_size=full_path.stat().st_size,
                    content_type=self._get_content_type(full_path),
                )
                result.append(file_info)
        
        # Sort by file ID
        result.sort(key=lambda x: x.id)
        return result
    
    def get_all_albums(self) -> List[str]:
        """Get list of all album names."""
        self._ensure_loaded()
        
        if self._mapping is None:
            return []
        
        return self._mapping.get_all_albums()
    
    def add_file(self, album: str, file_id: int, file_path: Path) -> bool:
        """Add a file to the mapping."""
        self._ensure_loaded()
        
        if self._mapping is None:
            return False
        
        # Convert to relative path if needed
        relative_path = self._make_relative(file_path)
        
        self._mapping.add_file(album, file_id, str(relative_path))
        return self.save_mapping()
    
    def remove_file(self, album: str, file_id: int) -> bool:
        """Remove a file from the mapping."""
        self._ensure_loaded()
        
        if self._mapping is None:
            return False
        
        result = self._mapping.remove_file(album, file_id)
        if result:
            return self.save_mapping()
        return False
    
    def remove_album(self, album: str) -> bool:
        """Remove an entire album from the mapping."""
        self._ensure_loaded()
        
        if self._mapping is None:
            return False
        
        result = self._mapping.remove_album(album)
        if result:
            return self.save_mapping()
        return False
    
    def _make_relative(self, file_path: Path) -> Path:
        """Convert an absolute path to a relative path from media root."""
        if not file_path.is_absolute():
            return file_path
        
        try:
            return file_path.relative_to(settings.media_root_path)
        except ValueError:
            # Path is not under media root, keep as absolute
            return file_path
    
    def _get_content_type(self, file_path: Path) -> str:
        """Determine the MIME type based on file extension."""
        extension = file_path.suffix.lower()
        
        # Video types
        video_extensions = {
            ".mp4": "video/mp4",
            ".webm": "video/webm",
            ".mov": "video/quicktime",
            ".avi": "video/x-msvideo",
            ".mkv": "video/x-matroska",
            ".flv": "video/x-flv",
            ".wmv": "video/x-ms-wmv",
            ".mpeg": "video/mpeg",
            ".ogv": "video/ogg",
        }
        
        # Audio types
        audio_extensions = {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".m4a": "audio/mp4",
            ".flac": "audio/flac",
            ".aac": "audio/aac",
        }
        
        # Image types
        image_extensions = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".svg": "image/svg+xml",
            ".bmp": "image/bmp",
            ".tiff": "image/tiff",
        }
        
        if extension in video_extensions:
            return video_extensions[extension]
        elif extension in audio_extensions:
            return audio_extensions[extension]
        elif extension in image_extensions:
            return image_extensions[extension]
        
        # Default to binary
        return "application/octet-stream"


# Global mapping service instance
mapping_service = MappingService()
