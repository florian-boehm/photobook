"""Media-related data models."""

from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class MediaFileInfo(BaseModel):
    """Information about a media file."""
    
    id: int = Field(..., description="Unique file ID within the album (1-based)")
    album: str = Field(..., description="Album name")
    file_path: Path = Field(..., description="Absolute path to the media file")
    file_name: str = Field(..., description="Original file name")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME type of the file")
    
    @property
    def is_video(self) -> bool:
        """Check if the file is a video."""
        return self.content_type.startswith("video/")
    
    @property
    def is_audio(self) -> bool:
        """Check if the file is audio."""
        return self.content_type.startswith("audio/")
    
    @property
    def is_image(self) -> bool:
        """Check if the file is an image."""
        return self.content_type.startswith("image/")


class AlbumInfo(BaseModel):
    """Information about an album."""
    
    name: str = Field(..., description="Album name")
    file_count: int = Field(..., description="Number of files in the album")
    files: List[MediaFileInfo] = Field(
        default_factory=list,
        description="List of media files in the album",
    )


class AlbumListResponse(BaseModel):
    """Response containing list of all albums."""
    
    albums: List[str] = Field(
        default_factory=list,
        description="List of album names",
    )


class AlbumDetailResponse(BaseModel):
    """Response containing details of a specific album."""
    
    album: AlbumInfo = Field(..., description="Album information")


class MediaMapping(BaseModel):
    """Complete mapping of albums to file paths."""
    
    version: str = Field(default="1.0", description="Mapping file version")
    albums: Dict[str, Dict[int, str]] = Field(
        default_factory=dict,
        description="Mapping of album_name -> {file_id -> file_path}",
    )
    
    def get_file_path(self, album: str, file_id: int) -> Optional[str]:
        """Get the file path for a given album and file ID."""
        if album in self.albums:
            return self.albums[album].get(file_id)
        return None
    
    def get_album_files(self, album: str) -> Dict[int, str]:
        """Get all file mappings for an album."""
        return self.albums.get(album, {})
    
    def get_all_albums(self) -> List[str]:
        """Get list of all album names."""
        return list(self.albums.keys())
    
    def add_file(self, album: str, file_id: int, file_path: str) -> None:
        """Add a file mapping to an album."""
        if album not in self.albums:
            self.albums[album] = {}
        self.albums[album][file_id] = file_path
    
    def remove_file(self, album: str, file_id: int) -> bool:
        """Remove a file mapping from an album."""
        if album in self.albums and file_id in self.albums[album]:
            del self.albums[album][file_id]
            # Clean up empty albums
            if not self.albums[album]:
                del self.albums[album]
            return True
        return False
    
    def remove_album(self, album: str) -> bool:
        """Remove an entire album from the mapping."""
        if album in self.albums:
            del self.albums[album]
            return True
        return False
