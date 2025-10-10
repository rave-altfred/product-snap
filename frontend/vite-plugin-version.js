const { generateVersionInfo } = require('../scripts/generate-version');
const fs = require('fs');
const path = require('path');

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
