"""Media streaming API endpoints."""

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse

from app.models.media import AlbumDetailResponse, AlbumListResponse
from app.services.mapping_service import mapping_service
from app.services.streaming_service import streaming_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["media"])


@router.get("/albums", response_model=AlbumListResponse)
async def list_albums():
    """List all available albums."""
    try:
        albums = mapping_service.get_all_albums()
        return AlbumListResponse(albums=albums)
    except Exception as e:
        logger.error(f"Failed to list albums: {e}")
        raise HTTPException(status_code=500, detail="Failed to list albums")


@router.get("/albums/{album_name}", response_model=AlbumDetailResponse)
async def get_album(album_name: str):
    """Get details of a specific album including all files."""
    try:
        files = mapping_service.get_album_files(album_name)
        
        if not files:
            raise HTTPException(status_code=404, detail=f"Album '{album_name}' not found")
        
        from app.models.media import AlbumInfo
        album_info = AlbumInfo(
            name=album_name,
            file_count=len(files),
            files=files,
        )
        
        return AlbumDetailResponse(album=album_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get album {album_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get album: {e}")


@router.get("/albums/{album_name}/files/{file_id}")
async def get_file_info(
    album_name: str,
    file_id: int,
):
    """Get information about a specific file."""
    try:
        info = await streaming_service.get_file_info(album_name, file_id)
        return info
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"File {file_id} in album '{album_name}' not found",
        )
    except Exception as e:
        logger.error(f"Failed to get file info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get file info: {e}")


@router.get("/albums/{album_name}/files/{file_id}/stream")
async def stream_file(
    album_name: str,
    file_id: int,
    response: Response,
):
    """Stream a media file to the client."""
    try:
        # Get file info to set proper headers
        info = await streaming_service.get_file_info(album_name, file_id)
        
        # Set response headers
        response.headers["Content-Type"] = info["content_type"]
        response.headers["Content-Disposition"] = f'inline; filename="{info["file_name"]}"'
        response.headers["Accept-Ranges"] = "bytes"
        
        # Create streaming response
        return StreamingResponse(
            streaming_service.stream_file(album_name, file_id),
            media_type=info["content_type"],
            headers={
                "Content-Length": str(info["file_size"]),
                "Content-Disposition": f'inline; filename="{info["file_name"]}"',
            },
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"File {file_id} in album '{album_name}' not found",
        )
    except Exception as e:
        logger.error(f"Failed to stream file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stream file: {e}")


@router.get("/albums/{album_name}/files/{file_id}/download")
async def download_file(
    album_name: str,
    file_id: int,
    response: Response,
):
    """Download a media file (forces download instead of streaming)."""
    try:
        info = await streaming_service.get_file_info(album_name, file_id)
        
        return StreamingResponse(
            streaming_service.stream_file(album_name, file_id),
            media_type="application/octet-stream",
            headers={
                "Content-Length": str(info["file_size"]),
                "Content-Disposition": f'attachment; filename="{info["file_name"]}"',
            },
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"File {file_id} in album '{album_name}' not found",
        )
    except Exception as e:
        logger.error(f"Failed to download file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download file: {e}")


@router.get("/stream/{album_name}/{file_id}")
async def stream_file_short(
    album_name: str,
    file_id: int,
    response: Response,
):
    """Short URL for streaming a media file (redirects to full URL)."""
    return await stream_file(album_name, file_id, response)
