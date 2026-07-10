# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release preparation

## [1.0.0] - 2026-07-10

### Added
- Complete iCloud photo and video migration
- GUI interface with PySide6
- QR code login support
- Multi-threaded download (configurable 1-20 threads)
- Resume support after interruption
- Automatic deduplication
- Progress tracking with real-time updates
- Detailed logging system
- NAS connection detection
- Disk space checking
- Smart folder organization (Year/Year-Month/Year-Month-Day)
- Export migration reports
- Failed file tracking

### Features
- **Authentication**: QR code login (recommended) or password login
- **Download**: Multi-threaded, resumable, with retry mechanism
- **Organization**: Automatic directory structure by date
- **Deduplication**: SHA-256 based duplicate detection
- **Progress**: Real-time progress bar and statistics
- **Logging**: Comprehensive logging with file rotation

### Technical
- Built with PySide6 for cross-platform GUI
- SQLite for state management
- icloudpd as the download engine
- YAML configuration file
- Comprehensive error handling

## [0.1.0] - 2026-07-09

### Added
- Initial project structure
- Core module implementation
- Basic GUI framework

---

## Release Notes

### v1.0.0
First stable release with complete iCloud to NAS migration functionality.

**Key Features:**
- One-click migration of all iCloud photos/videos
- Smart folder organization
- Resume interrupted downloads
- Multi-threaded for speed

**Requirements:**
- macOS 10.15+
- Python 3.8+
- NAS with SMB support
