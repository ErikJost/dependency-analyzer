# Build Dependency Analysis

## Overview
This report identifies which potentially orphaned files are actually used during the build process.

Total orphaned files: 71
Files used during build: 21
Files not used during build: 50

## Files Used During Build

- tsconfig.node.json
  - Reason: Configuration file, likely used indirectly

- tsconfig.app.json
  - Reason: Configuration file, likely used indirectly

- package-lock.json
  - Reason: Configuration file, likely used indirectly

- mock-db-schema.json
  - Reason: Configuration file, likely used indirectly

- eslint.config.js
  - Reason: Configuration file, likely used indirectly

- dependency-graph.json
  - Reason: Configuration file, likely used indirectly

- src/types/env.d.ts
  - Reason: TypeScript type definition, used for type checking

- scripts/package-lock.json
  - Reason: Configuration file, likely used indirectly

- public/scripts/env-config.js
  - Reason: Configuration file, likely used indirectly

- functions/package-lock.json
  - Reason: Configuration file, likely used indirectly

- functions/host.json
  - Reason: Configuration file, likely used indirectly

- docs/dependency-analysis/dependency-graph.json
  - Reason: Configuration file, likely used indirectly

- client/tsconfig.node.json
  - Reason: Configuration file, likely used indirectly

- client/tsconfig.check.json
  - Reason: Configuration file, likely used indirectly

- client/tailwind.config.js
  - Reason: Configuration file, likely used indirectly

- client/postcss.config.js
  - Reason: Configuration file, likely used indirectly

- client/azure-app-service.config.json
  - Reason: Configuration file, likely used indirectly

- client/src/environment.d.ts
  - Reason: TypeScript type definition, used for type checking

- client/src/types/env.d.ts
  - Reason: TypeScript type definition, used for type checking

- client/src/types/debug.d.ts
  - Reason: TypeScript type definition, used for type checking

- client/src/services/azureClient.d.ts
  - Reason: TypeScript type definition, used for type checking

## Files Not Used During Build

- src/services/apiMetrics.js

- src/auth/services/authApi.ts

- src/auth/routes/AuthRoutes.tsx

- src/auth/providers/LocalProvider.ts

- src/auth/config/msalConfig.ts

- src/auth/components/RoleBasedAccess.tsx

- src/auth/components/LocalLogin.tsx

- src/auth/components/AuthCallback.tsx

- src/auth/components/AdminSettings.tsx

- shared/models/MetricModels.ts

- server/src/routes/api.ts

- secure_credentials/app_connection_example.js

- scripts/find-cross-deps.js

- scripts/db-seed.js

- scripts/db-init.js

- public/module-loader.js

- functions/src/functions/api-clients.ts

- client/src/services/xliSchedulerService.js

- client/src/services/dbTest.js

- client/src/lib/constants.ts

- client/src/lib/abilityHooks.ts

- client/src/lib/services/MetricAggregationService.ts

- client/src/lib/auth/AuthContext.tsx

- client/src/data/ReleaseNotesData.ts

- client/src/components/XLIManager.tsx

- client/src/components/XLALogTable.tsx

- client/src/components/TenantManagement.tsx

- client/src/components/Settings.tsx

- client/src/components/RoleBasedAccess.tsx

- client/src/components/LoginPage.tsx

- client/src/components/LoadingSpinner.tsx

- client/src/components/DatabaseTest.tsx

- client/src/components/AuthProviderSettings.tsx

- client/src/components/AssetErrorFallback.tsx

- client/src/components/ApiClientManager.tsx

- client/src/components/ui/tooltip.tsx

- client/src/components/ui/label.tsx

- client/src/components/shared/Tabs.tsx

- client/src/components/settings/DebugSettings.tsx

- client/src/components/common/DateRangePicker.tsx

- client/src/components/common/DatabaseErrorDisplay.tsx

- client/src/components/auth/AuthCallback.tsx

- client/src/auth/types.ts

- client/src/auth/utils/state.ts

- client/src/auth/services/authApi.ts

- client/src/auth/routes/AuthRoutes.tsx

- client/src/auth/providers/MsalProvider.tsx

- client/src/auth/hooks/useAuth.tsx

- client/src/auth/components/RoleBasedAccess.tsx

- client/src/auth/components/AdminSettings.tsx

## Recommendation

The files listed in the "Files Not Used During Build" section are good candidates for archiving according to the project's never-delete-files rule. They aren't imported by other files and don't appear to be used during the build process.

Generated on: 2025-05-05T22:50:42.631Z
