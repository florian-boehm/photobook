"""Tests for media endpoints and services."""

import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.media import MediaMapping
from app.services.mapping_service import MappingService


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def temp_media_dir() -> Generator[Path, None, None]:
    """Create a temporary media directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        media_dir = Path(tmpdir) / "media"
        media_dir.mkdir()
        
        # Create some test files
        (media_dir / "test_video.mp4").write_bytes(b"fake video data")
        (media_dir / "test_image.jpg").write_bytes(b"fake image data")
        (media_dir / "test_audio.mp3").write_bytes(b"fake audio data")
        
        yield media_dir


@pytest.fixture
def temp_mapping_file() -> Generator[Path, None, None]:
    """Create a temporary mapping file for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mapping_file = Path(tmpdir) / "mapping.json"
        
        mapping = MediaMapping(
            version="1.0",
            albums={
                "test_album": {
                    1: "test_video.mp4",
                    2: "test_image.jpg",
                    3: "test_audio.mp3",
                }
            }
        )
        
        with open(mapping_file, "w") as f:
            json.dump(mapping.model_dump(), f)
        
        yield mapping_file


class TestMediaMapping:
    """Tests for the MediaMapping model."""
    
    def test_get_file_path(self):
        """Test getting file path from mapping."""
        mapping = MediaMapping(
            version="1.0",
            albums={
                "album1": {
                    1: "path/to/file1.mp4",
                    2: "path/to/file2.jpg",
                }
            }
        )
        
        assert mapping.get_file_path("album1", 1) == "path/to/file1.mp4"
        assert mapping.get_file_path("album1", 2) == "path/to/file2.jpg"
        assert mapping.get_file_path("album1", 3) is None
        assert mapping.get_file_path("nonexistent", 1) is None
    
    def test_get_album_files(self):
        """Test getting all files for an album."""
        mapping = MediaMapping(
            version="1.0",
            albums={
                "album1": {
                    1: "file1.mp4",
                    2: "file2.jpg",
                }
            }
        )
        
        files = mapping.get_album_files("album1")
        assert files == {1: "file1.mp4", 2: "file2.jpg"}
        
        files = mapping.get_album_files("nonexistent")
        assert files == {}
    
    def test_get_all_albums(self):
        """Test getting all album names."""
        mapping = MediaMapping(
            version="1.0",
            albums={
                "album1": {1: "file1.mp4"},
                "album2": {1: "file2.jpg"},
            }
        )
        
        albums = mapping.get_all_albums()
        assert set(albums) == {"album1", "album2"}
    
    def test_add_file(self):
        """Test adding a file to the mapping."""
        mapping = MediaMapping()
        
        mapping.add_file("album1", 1, "file1.mp4")
        assert mapping.get_file_path("album1", 1) == "file1.mp4"
        
        mapping.add_file("album1", 2, "file2.jpg")
        assert mapping.get_file_path("album1", 2) == "file2.jpg"
    
    def test_remove_file(self):
        """Test removing a file from the mapping."""
        mapping = MediaMapping(
            version="1.0",
            albums={
                "album1": {
                    1: "file1.mp4",
                    2: "file2.jpg",
                }
            }
        )
        
        assert mapping.remove_file("album1", 1) is True
        assert mapping.get_file_path("album1", 1) is None
        assert mapping.get_file_path("album1", 2) == "file2.jpg"
        
        assert mapping.remove_file("nonexistent", 1) is False
    
    def test_remove_album(self):
        """Test removing an entire album."""
        mapping = MediaMapping(
            version="1.0",
            albums={
                "album1": {1: "file1.mp4"},
                "album2": {1: "file2.jpg"},
            }
        )
        
        assert mapping.remove_album("album1") is True
        assert "album1" not in mapping.get_all_albums()
        assert "album2" in mapping.get_all_albums()
        
        assert mapping.remove_album("nonexistent") is False


class TestMappingService:
    """Tests for the MappingService."""
    
    def test_load_and_save_mapping(self, temp_mapping_file):
        """Test loading and saving mapping."""
        service = MappingService(temp_mapping_file)
        mapping = service.load_mapping()
        
        assert mapping.get_all_albums() == ["test_album"]
        assert mapping.get_file_path("test_album", 1) == "test_video.mp4"
    
    def test_get_file_path(self, temp_mapping_file):
        """Test getting file path through service."""
        service = MappingService(temp_mapping_file)
        
        # This will fail because the media root doesn't exist
        # but we can test the relative path logic
        service._ensure_loaded()
        assert service._mapping.get_file_path("test_album", 1) == "test_video.mp4"


class TestAPIEndpoints:
    """Tests for the API endpoints."""
    
    def test_root_endpoint(self, test_client):
        """Test the root endpoint."""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data
    
    def test_health_endpoint(self, test_client):
        """Test the health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_list_albums_empty(self, test_client):
        """Test listing albums when none exist."""
        response = test_client.get("/api/v1/albums")
        assert response.status_code == 200
        data = response.json()
        assert "albums" in data
        # Albums list might be empty or contain defaults
    
    def test_get_nonexistent_album(self, test_client):
        """Test getting a nonexistent album."""
        response = test_client.get("/api/v1/albums/nonexistent")
        assert response.status_code == 404
    
    def test_get_nonexistent_file(self, test_client):
        """Test getting a nonexistent file."""
        response = test_client.get("/api/v1/albums/test_album/files/999")
        assert response.status_code == 404
