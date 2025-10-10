const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * Generate version information from git and package.json
 * Self-contained version for Docker builds
 */
function generateVersionInfo() {
  try {
    // Read version from package.json
    const packageJsonPath = path.join(__dirname, 'package.json');
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const version = packageJson.version;

    // Get git information
    let gitCommit = 'unknown';
    let gitBranch = 'unknown';
    let gitTag = null;
    let buildDate = new Date().toISOString();

    try {
      gitCommit = execSync('git rev-parse --short HEAD', { encoding: 'utf8' }).trim();
      gitBranch = execSync('git rev-parse --abbrev-ref HEAD', { encoding: 'utf8' }).trim();
      
      // Try to get the most recent tag
      try {
        gitTag = execSync('git describe --tags --exact-match 2>/dev/null', { encoding: 'utf8' }).trim();
      } catch (e) {
        // No exact tag match, try to get the nearest tag
        try {
          gitTag = execSync('git describe --tags --abbrev=0 2>/dev/null', { encoding: 'utf8' }).trim();
        } catch (e) {
          gitTag = null;
        }
      }
    } catch (error) {
      console.warn('Warning: Could not retrieve git information:', error.message);
    }

    return {
      version,
      gitCommit,
      gitBranch,
      gitTag,
      buildDate,
      fullVersion: gitTag || `${version}-${gitCommit}`,
    };
  } catch (error) {
    console.error('Error generating version info:', error);
    return {
      version: '0.0.0',
      gitCommit: 'unknown',
      gitBranch: 'unknown',
      gitTag: null,
      buildDate: new Date().toISOString(),
      fullVersion: '0.0.0-unknown',
    };
  }
}

/**
 * Vite plugin to generate version.ts file during build
 */
export default function vitePluginVersion() {
  return {
    name: 'vite-plugin-version',
    
    // Generate version file before build starts
    buildStart() {
      const versionInfo = generateVersionInfo();
      const versionFilePath = path.join(__dirname, 'src/version.ts');
      
      const content = `// Auto-generated file. Do not edit manually.
// Generated at build time by vite-plugin-version

export interface VersionInfo {
  version: string;
  gitCommit: string;
  gitBranch: string;
  gitTag: string | null;
  buildDate: string;
  fullVersion: string;
}

export const versionInfo: VersionInfo = ${JSON.stringify(versionInfo, null, 2)};

export const version = versionInfo.fullVersion;
`;

      fs.writeFileSync(versionFilePath, content, 'utf8');
      console.log(`✓ Generated version.ts: ${versionInfo.fullVersion}`);
    },
  };
}
