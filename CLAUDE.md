# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python 3.12 application that automatically synchronizes content from Notion to GitHub as Markdown files. It runs daily via GitHub Actions and converts Notion pages (including nested pages) to a structured directory of Markdown files.

## Development Commands

### Running the Application
```bash
# Set required environment variables
export NOTION_TOKEN="your-notion-token"
export GITHUB_TOKEN="your-github-token"
export NOTION_PAGE_ID="your-notion-page-id"

# Run the sync
python main.py
```

### Dependencies
```bash
# Install dependencies
pip install -r requirements.txt
```

### Testing
No test framework is currently configured. When implementing tests, consider adding pytest and creating test files for:
- `ContentConvert` - Block conversion logic
- `NotionGitSync` - Sync orchestration
- API mocking for Notion and GitHub clients

## Architecture

### Core Components

1. **main.py** - Single-file application with these key classes:
   - `Config`: Loads configuration from environment variables or `config.yaml`
   - `NotionDebugger`: Saves raw API responses to `notion_debug/` for troubleshooting
   - `ContentConvert`: Converts Notion blocks to Markdown format
   - `SyncLogger`: Manages logging to file and console
   - `NotionGitSync`: Main orchestrator that fetches from Notion and pushes to GitHub

2. **GitHub Actions Workflow** (`.github/workflows/notion-sync.yml`):
   - Runs daily at 00:00 Asia/Shanghai time
   - Uses secrets: `NOTION_TOKEN`, `ACTIONS_TOKEN`, `NOTION_PAGE_ID`
   - Repository name is hardcoded in the workflow

### Data Flow
1. Fetches page structure from Notion API starting from `NOTION_PAGE_ID`
2. Recursively processes child pages
3. Converts Notion blocks to Markdown (paragraphs, headings, lists, code blocks, tables, images)
4. Saves files to `notion_sync/` directory maintaining Notion's hierarchy
5. Commits and pushes changes to GitHub
6. Updates `notion_sync/README.md` with sync log

### Key Implementation Details

- **Retry Logic**: Uses `retrying` library for API calls with exponential backoff
- **Change Detection**: Only updates files if content has changed
- **Debug Mode**: Set `DEBUG=true` to save raw Notion responses
- **Image Handling**: Downloads images and saves them locally
- **Error Handling**: Comprehensive try-catch blocks with detailed logging

## Common Development Tasks

### Adding New Block Type Support
1. Add handler method in `ContentConvert` class (e.g., `convert_new_block_type`)
2. Add case in `convert_blocks()` method
3. Test with sample Notion page containing the new block type

### Debugging Sync Issues
1. Enable debug mode: `export DEBUG=true`
2. Check `notion_sync.log` for detailed logs
3. Examine raw API responses in `notion_debug/` directory

### Modifying Sync Behavior
- Change sync frequency: Edit cron schedule in `.github/workflows/notion-sync.yml`
- Add filters: Modify `fetch_all_pages()` or `should_update_file()` methods
- Change output format: Modify methods in `ContentConvert` class

### Using Hexo Blog Sync Feature
The repository now includes `notion_to_hexo.py` for syncing Notion content to a Hexo blog:

1. **Setup**: Configure environment variables:
   - `NOTION_TOKEN`, `GITHUB_TOKEN`, `NOTION_PAGE_ID`
   - `HEXO_REPO` (e.g., "HyxiaoGe/blog")

2. **Run**: `python notion_to_hexo.py`

3. **Features**:
   - Converts Notion pages to Hexo posts with Front Matter
   - Downloads and saves images to Hexo repository
   - Intelligent tag extraction from titles
   - GitHub Actions workflow for automated deployment

4. **Key Classes**:
   - `HexoContentConvert`: Handles Notion to Hexo format conversion
   - `NotionToHexoSync`: Manages the sync process and GitHub integration

## Important Notes

- The sync is one-way only (Notion → GitHub)
- File names are sanitized to be filesystem-friendly
- Deleted Notion pages are NOT automatically deleted from GitHub
- The `schedule` library is imported but unused (manual runs or cron-based execution only)
- Hexo sync creates posts with date-prefixed filenames (e.g., `2025-01-23-title.md`)