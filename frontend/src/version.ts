// Auto-generated file. Do not edit manually.
// Generated at build time by vite-plugin-version

export interface VersionInfo {
  version: string;
  gitCommit: string;
  gitBranch: string;
  gitTag: string | null;
  buildDate: string;
  fullVersion: string;
}

export const versionInfo: VersionInfo = {
  version: "1.0.0",
  gitCommit: "dev",
  gitBranch: "main",
  gitTag: null,
  buildDate: new Date().toISOString(),
  fullVersion: "1.0.0-dev"
};

export const version = versionInfo.fullVersion;
