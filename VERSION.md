# Version Management

This document describes the versioning system for ProductSnap.

## Overview

ProductSnap uses semantic versioning (MAJOR.MINOR.PATCH) for both frontend and backend components. The version is automatically displayed in the UI and available via the backend API.

## Version Display

- **Frontend UI**: Version is displayed at the bottom of the sidebar (both desktop and mobile) in a subtle, non-intrusive way
- **Backend API**: Version information is available at `/version` endpoint

## Automatic Version Generation

The version system automatically includes:
- Version number from `package.json`
- Git commit hash
- Git branch name
- Git tag (if available)
- Build timestamp

### Frontend Build

During the frontend build process:
1. The Vite plugin reads version info from `package.json` and git
2. Generates `src/version.ts` with version information
3. The Layout component imports and displays the version

### Backend API

The `/version` endpoint returns:
```json
{
  "version": "1.0.0",
  "app_name": "ProductSnap",
  "timestamp": "2025-10-10T10:58:20Z",
  "git_commit": "abc1234",
  "git_branch": "main"
}
```

## Bumping Versions

### Using the Automated Script (Recommended)

The easiest way to bump versions is using the provided script:

```bash
# Bump patch version (1.0.0 -> 1.0.1)
./scripts/bump-version.sh patch

# Bump minor version (1.0.0 -> 1.1.0)
./scripts/bump-version.sh minor

# Bump major version (1.0.0 -> 2.0.0)
./scripts/bump-version.sh major
```

This script will:
1. Update `frontend/package.json` version
2. Update `backend/app/core/config.py` APP_VERSION
3. Commit the changes
4. Create a git tag (e.g., `v1.0.1`)
5. Show instructions to push changes

After running the script, push your changes:
```bash
git push && git push --tags
```

### Manual Version Management

If you need to manually manage versions:

1. **Frontend**: Update version in `frontend/package.json`
   ```bash
   cd frontend
   npm version patch  # or minor, major
   ```

2. **Backend**: Update `APP_VERSION` in `backend/app/core/config.py`
   ```python
   APP_VERSION: str = "1.0.1"
   ```

3. **Create Git Tag**:
   ```bash
   git tag -a v1.0.1 -m "Release version 1.0.1"
   git push --tags
   ```

## Version Information Script

To view current version information:

```bash
# From root directory
node scripts/generate-version.js

# From frontend directory
npm run version:show
```

This will output:
```json
{
  "version": "1.0.0",
  "gitCommit": "abc1234",
  "gitBranch": "main",
  "gitTag": "v1.0.0",
  "buildDate": "2025-10-10T10:58:20.000Z",
  "fullVersion": "v1.0.0"
}
```

## Development vs Production

- **Development**: Version shows as `1.0.0-dev` or `1.0.0-{commit-hash}`
- **Production**: Version shows as `v1.0.0` (if built from a tagged commit)

## Files

- `scripts/generate-version.js` - Core version generation logic
- `scripts/bump-version.sh` - Automated version bumping script
- `frontend/vite-plugin-version.js` - Vite plugin for generating version.ts
- `frontend/src/version.ts` - Generated version file (auto-generated, do not edit)
- `frontend/src/components/Layout.tsx` - UI component displaying version
- `backend/app/routers/health.py` - Backend `/version` endpoint
- `backend/app/core/config.py` - Backend version configuration

## Best Practices

1. **Use the bump script** for consistency across frontend and backend
2. **Tag releases** to get cleaner version strings in production
3. **Follow semantic versioning**:
   - PATCH: Bug fixes and minor changes
   - MINOR: New features (backwards compatible)
   - MAJOR: Breaking changes
4. **Always commit before bumping** to ensure clean version tags
5. **Document changes** in release notes when creating tags

## Troubleshooting

**Version not updating in UI?**
- Rebuild the frontend: `cd frontend && npm run build`
- The version is generated at build time

**Different versions in frontend and backend?**
- Run the bump script to sync both versions
- Or manually update both `package.json` and `config.py`

**Git information not showing?**
- Ensure you're in a git repository
- Ensure git is installed and accessible
- Check that the working directory is clean
