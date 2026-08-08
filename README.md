# Photobook - Media Streaming Service

A web application for serving video, audio, and image files through unique links with album organization.

## Features

- **Media Streaming**: Stream video, audio, and image files directly to the client without requiring download
- **Album Organization**: Organize files into named albums
- **Simple ID System**: Each file in an album has a unique numeric ID (1-based, incrementing)
- **Mapping System**: JSON-based mapping of album/file IDs to file paths
- **Docker Support**: Run the application in a Docker container
- **Dev Container**: Full VS Code devcontainer support for development

## Project Structure

```
photobook/
├── backend/                    # Python backend application
│   ├── app/                    # FastAPI application
│   │   ├── api/                # API endpoints
│   │   │   └── endpoints/      # API endpoint modules
│   │   ├── core/               # Core utilities and configuration
│   │   ├── models/             # Data models
│   │   └── services/           # Service layer
│   │       └── main.py         # Main application entry point
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # Frontend files (future GUI)
│   └── index.html             # Basic HTML frontend
│
├── .devcontainer/             # VS Code devcontainer configuration
│   ├── devcontainer.json
│   └── docker-compose.devcontainer.yml
│
├── data/                      # Data directory
│   ├── mapping.json           # Media file mapping
│   └── .gitkeep
│
├── media/                     # Media files directory
│   └── .gitkeep
│
├── Dockerfile                 # Docker build configuration
├── docker-compose.yml         # Docker Compose configuration
├── .env.example               # Example environment configuration
├── .gitignore                 # Git ignore patterns
└── README.md                  # This file
```

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/florian-boehm/photobook.git
cd photobook

# Copy environment file
cp .env.example .env

# Edit .env to configure your media root path
# MEDIA_ROOT_PATH=/path/to/your/media
```

### 2. Add Media Files

1. Create subdirectories in the `media/` folder for your albums
2. Add your media files to these subdirectories
3. Update the `data/mapping.json` file to map album names and file IDs to paths

Example mapping:
```json
{
  "version": "1.0",
  "albums": {
    "vacation": {
      "1": "vacation/video1.mp4",
      "2": "vacation/photo1.jpg",
      "3": "vacation/audio1.mp3"
    }
  }
}
```

### 3. Run with Docker

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

The application will be available at `http://localhost:8000`

### 4. Run Locally (without Docker)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run the application
python -m uvicorn backend.app.main:app --reload
```

## API Endpoints

### Albums

- `GET /api/v1/albums` - List all available albums
- `GET /api/v1/albums/{album_name}` - Get details of a specific album

### Files

- `GET /api/v1/albums/{album_name}/files/{file_id}` - Get file information
- `GET /api/v1/albums/{album_name}/files/{file_id}/stream` - Stream the file
- `GET /api/v1/albums/{album_name}/files/{file_id}/download` - Download the file

### Short URLs

- `GET /stream/{album_name}/{file_id}` - Short URL for streaming

### Health Check

- `GET /health` - Health check endpoint

## Development

### Using VS Code Dev Container

1. Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension
2. Open the project in VS Code
3. Click "Reopen in Container" or press `F1` and select "Remote-Containers: Reopen in Container"

The dev container includes:
- Python 3.11
- All required dependencies
- Development tools (linters, formatters)
- Git and GitHub CLI

### Running Tests

```bash
# Run tests
python -m pytest backend/tests/

# Run with coverage
python -m pytest --cov=backend/app backend/tests/
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | Photobook | Application name |
| `APP_VERSION` | 0.1.0 | Application version |
| `DEBUG` | False | Enable debug mode |
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `MEDIA_ROOT_PATH` | /media | Root directory for media files |
| `MAPPING_FILE_PATH` | /data/mapping.json | Path to mapping file |
| `CHUNK_SIZE` | 8192 | Chunk size for streaming (bytes) |
| `CORS_ORIGINS` | * | CORS allowed origins |

### Mapping File Format

The mapping file (`data/mapping.json`) uses the following format:

```json
{
  "version": "1.0",
  "albums": {
    "album_name_1": {
      "1": "relative/path/to/file1.ext",
      "2": "relative/path/to/file2.ext"
    },
    "album_name_2": {
      "1": "relative/path/to/file3.ext"
    }
  }
}
```

- Album names are strings
- File IDs are integers starting from 1
- File paths are relative to `MEDIA_ROOT_PATH`

## Streaming

The application supports streaming for:

- **Video**: MP4, WebM, MOV, AVI, MKV, FLV, WMV, MPEG, OGV
- **Audio**: MP3, WAV, OGG, M4A, FLAC, AAC
- **Images**: JPG, JPEG, PNG, GIF, WebP, SVG, BMP, TIFF

Files are streamed in chunks (default 8KB) to ensure efficient memory usage and support for large files.

## Future Enhancements

- [ ] Admin interface for managing mappings
- [ ] User authentication and authorization
- [ ] File upload through the web interface
- [ ] Thumbnail generation for videos and images
- [ ] Playlist support
- [ ] Search and filtering
- [ ] Caching for frequently accessed files
- [ ] CDN integration

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request
