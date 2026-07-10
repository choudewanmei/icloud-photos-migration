# iCloud Photos Migration Assistant

[中文](README.md) | English

A tool to safely migrate iCloud photos and videos to your NAS without Docker.

## Features

- ✅ **Complete Migration**: Download all photos and videos from iCloud
- ✅ **Incremental Sync**: Only download new files, skip existing ones
- ✅ **Smart Organization**: Auto-create directory structure by `Year/Year-Month/Year-Month-Day`
- ✅ **Resume Support**: Continue from where you left off after interruption
- ✅ **Deduplication**: Automatically identify duplicate files
- ✅ **GUI Interface**: Intuitive progress display and operation interface
- ✅ **Error Logging**: Failed files are logged without interrupting the overall process

## System Requirements

- **OS**: macOS 10.15 or later
- **Python**: 3.8 or later
- **NAS**: SMB protocol support, mounted to macOS

## Installation

### 1. Install Python (if not installed)

```bash
# Using Homebrew
brew install python

# Or download from: https://www.python.org/downloads/
```

### 2. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/icloud-photos-migration.git
cd icloud-photos-migration

# Install dependencies
pip3 install -r requirements.txt
```

### 3. Mount NAS

In Finder:
1. Press `Cmd + K` to open "Connect to Server"
2. Enter NAS address: `smb://YOUR_NAS_ADDRESS`
3. Select shared folder
4. After mounting, it will appear in `/Volumes/`

Or using command line:
```bash
# Create mount point
sudo mkdir -p /Volumes/MyNAS

# Mount SMB
mount_smbfs //username:password@NAS_IP/share /Volumes/MyNAS
```

## Usage

### First Run

1. **Double-click `run.command`** to start the application

2. **Step 1: Connect to iCloud**
   - Enter your Apple ID
   - Click "Connect iCloud"
   - Enter password and verification code in the terminal window
   - Wait for authentication to succeed

3. **Step 2: Set NAS Path**
   - Enter or browse to select NAS mount path (e.g., `/Volumes/MyNAS/iCloud-Photos`)
   - Click "Detect NAS Connection"
   - Wait for "✅ NAS Connected"

4. **Start Migration**
   - Click "Start Migration" button
   - During migration, you can:
     - View real-time progress
     - Pause/Resume download
     - View detailed logs

5. **Completion Report**
   - After migration completes, a statistics report is displayed
   - Can export report file
   - Can view failed file list (if any)

### Daily Use

If migration is interrupted, run again:
1. Double-click `run.command`
2. The app will automatically detect unfinished migration
3. Select "Continue Migration" to resume from the breakpoint

## Configuration

Configuration file `config.yaml` will be auto-generated on first run:

```yaml
apple_id: "your@apple.id"
nas_path: "/Volumes/MyNAS/iCloud-Photos"
cookie_dir: "./cookies"
folder_format: "%Y/%Y-%m/%Y-%d"
threads_num: 5
only_new: true
download_photos: true
download_videos: true
skip_live_photos: false
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `apple_id` | Apple ID email | - |
| `nas_path` | NAS mount path | - |
| `cookie_dir` | Authentication cookie directory | `./cookies` |
| `folder_format` | Directory structure format | `%Y/%Y-%m/%Y-%d` |
| `threads_num` | Download concurrency | `5` |
| `only_new` | Only download new files | `true` |
| `download_photos` | Download photos | `true` |
| `download_videos` | Download videos | `true` |
| `skip_live_photos` | Skip Live Photos | `false` |

## Directory Structure

After migration, files will be organized as:

```
iCloud-Photos/
├── 2023/
│   ├── 2023-01/
│   │   ├── 2023-01-01/
│   │   │   ├── IMG_0001.HEIC
│   │   │   ├── IMG_0002.JPG
│   │   │   └── VID_0001.MOV
│   │   ├── 2023-01-15/
│   │   │   └── ...
│   │   └── ...
│   ├── 2023-02/
│   │   └── ...
│   └── ...
├── 2024/
│   └── ...
└── _duplicates/  # Duplicate files after deduplication (optional)
    └── ...
```

## FAQ

### Q: Authentication failed?

A:
1. Confirm Apple ID and password are correct
2. Confirm two-factor authentication is enabled
3. Check network connection
4. Try deleting `cookies` directory and re-authenticate

### Q: NAS connection detection failed?

A:
1. Confirm NAS is correctly mounted to `/Volumes/`
2. Confirm you can access NAS in Finder
3. Check if NAS path is correct
4. Confirm you have write permissions

### Q: Download speed is very slow?

A:
1. Check network bandwidth
2. Reduce `threads_num` concurrency (for unstable networks)
3. Avoid other high-bandwidth operations

### Q: How to view detailed logs?

A:
- In app: Click "View Full Log" button
- File: View log files in `logs/` directory

### Q: Migration interrupted?

A:
1. Run the application again
2. The app will automatically detect unfinished migration
3. Select "Continue Migration"

### Q: How to restart migration?

A:
1. Delete `migration_state.db` file
2. Delete `cookies` directory
3. Run the application again

## File Description

| File/Directory | Description |
|----------------|-------------|
| `run.command` | Startup script (double-click to run) |
| `main.py` | Python entry file |
| `config.yaml` | Configuration file |
| `migration_state.db` | State database |
| `cookies/` | iCloud authentication cookies |
| `logs/` | Running logs |
| `core/` | Core functionality modules |
| `gui/` | Graphical interface modules |

## Tech Stack

- **PySide6**: Qt for Python, GUI framework
- **icloudpd**: iCloud photo download tool
- **SQLite**: State database
- **PyYAML**: Configuration file parsing

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter issues, please provide:
1. macOS version
2. Python version (`python3 --version`)
3. Error message or logs
4. Steps to reproduce

## QR Code Login

This tool supports two iCloud login methods:

### 1. QR Code Login (Recommended)

QR code login is more secure and convenient:

1. Select "QR Code Login (Recommended)"
2. Click "Generate QR Code"
3. Scan QR Code with iPhone camera
4. Complete authentication on iPhone
5. Wait for authentication to succeed

**Advantages**:
- ✅ No need to enter password, more secure
- ✅ Scan to login, more convenient
- ✅ Automatic two-factor authentication handling

### 2. Password Login

Traditional login method:

1. Select "Password Login"
2. Enter Apple ID
3. Click "Connect iCloud"
4. Enter password and verification code in terminal
