# Potentially Orphaned Files
  
## Overview
This report identifies files in the codebase that are not imported by any other files and may be orphaned.

Total files analyzed: 283
Potentially orphaned files: 71

## Files that may be orphaned

- tsconfig.node.json

- tsconfig.app.json

- package-lock.json

- mock-db-schema.json

- eslint.config.js

- dependency-graph.json

- src/types/env.d.ts

- src/services/apiMetrics.js

- src/auth/services/authApi.ts
  - Imports: src/lib/debug.ts, src/auth/types, src/auth/hooks/useAuth.ts

- src/auth/routes/AuthRoutes.tsx
  - Imports: src/auth/components, src/lib/debug.ts, src/auth/types

- src/auth/providers/LocalProvider.ts
  - Imports: src/lib/debug.ts, src/auth/types, src/auth/providers/BaseAuthProvider.ts

- src/auth/config/msalConfig.ts
  - Imports: src/lib/debug.ts

- src/auth/components/RoleBasedAccess.tsx
  - Imports: src/auth/hooks, src/auth/types

- src/auth/components/LocalLogin.tsx
  - Imports: src/auth/hooks/useAuth.ts, src/lib/debug.ts

- src/auth/components/AuthCallback.tsx
  - Imports: src/auth/contexts/AuthContext.tsx, src/lib/debug.ts

- src/auth/components/AdminSettings.tsx
  - Imports: src/auth/types, src/auth/hooks/useAuth.ts, src/lib/debug.ts

- shared/models/MetricModels.ts

- server/src/routes/api.ts
  - Imports: server/src/services/azureClient.ts

- secure_credentials/app_connection_example.js

- scripts/package-lock.json

- scripts/find-cross-deps.js

- scripts/db-seed.js

- scripts/db-init.js

- public/module-loader.js

- public/scripts/env-config.js

- functions/package-lock.json

- functions/host.json

- functions/src/functions/api-clients.ts

- docs/dependency-analysis/dependency-graph.json

- client/tsconfig.node.json

- client/tsconfig.check.json

- client/tailwind.config.js

- client/postcss.config.js

- client/azure-app-service.config.json

- client/src/environment.d.ts

- client/src/types/env.d.ts

- client/src/types/debug.d.ts

- client/src/services/xliSchedulerService.js
  - Imports: client/src/services/azureClient.js, client/src/services/xlaApiService.js

- client/src/services/dbTest.js

- client/src/services/azureClient.d.ts

- client/src/lib/constants.ts
  - Imports: client/src/constants/text.ts

- client/src/lib/abilityHooks.ts
  - Imports: client/src/lib/abilityUtils.ts

- client/src/lib/services/MetricAggregationService.ts

- client/src/lib/auth/AuthContext.tsx
  - Imports: client/src/lib/auth/errors.ts

- client/src/data/ReleaseNotesData.ts

- client/src/components/XLIManager.tsx
  - Imports: client/src/lib/debug.ts

- client/src/components/XLALogTable.tsx

- client/src/components/TenantManagement.tsx
  - Imports: client/src/lib/db.ts, client/src/lib/utils.ts, client/src/lib/logger.ts, client/src/lib/services/SettingsService.ts, client/src/types/settings.ts, client/src/components/ui/button.tsx, client/src/components/ui/input.tsx, client/src/components/ui/card.tsx, client/src/auth/hooks/useAuth.ts

- client/src/components/Settings.tsx
  - Imports: client/src/components/SettingsPage.tsx

- client/src/components/RoleBasedAccess.tsx
  - Imports: client/src/auth, client/src/auth/types

- client/src/components/LoginPage.tsx
  - Imports: client/src/auth, client/src/lib/version.ts, client/src/lib/logger.ts, client/src/components/AuthDebugger.tsx

- client/src/components/LoadingSpinner.tsx

- client/src/components/DatabaseTest.tsx
  - Imports: client/src/lib/db.ts

- client/src/components/AuthProviderSettings.tsx

- client/src/components/AssetErrorFallback.tsx

- client/src/components/ApiClientManager.tsx
  - Imports: client/src/lib/debug.ts

- client/src/components/ui/tooltip.tsx
  - Imports: client/src/lib/utils.ts

- client/src/components/ui/label.tsx

- client/src/components/shared/Tabs.tsx
  - Imports: client/src/lib/utils.ts

- client/src/components/settings/DebugSettings.tsx
  - Imports: client/src/lib/debug.ts, client/src/lib/logger.ts, client/src/lib/utils.ts, client/src/components/shared/CollapsibleSection.tsx

- client/src/components/common/DateRangePicker.tsx
  - Imports: client/src/components/ui/button.tsx, client/src/lib/utils.ts

- client/src/components/common/DatabaseErrorDisplay.tsx

- client/src/components/auth/AuthCallback.tsx

- client/src/auth/types.ts

- client/src/auth/utils/state.ts
  - Imports: client/src/lib/debug.ts, client/src/auth/types

- client/src/auth/services/authApi.ts
  - Imports: client/src/lib/debug.ts, client/src/auth/types, client/src/auth/hooks/useAuth.ts

- client/src/auth/routes/AuthRoutes.tsx
  - Imports: client/src/auth/components, client/src/lib/debug.ts, client/src/auth/types, client/src/pages/auth/LoginTroubleshooting.tsx

- client/src/auth/providers/MsalProvider.tsx
  - Imports: client/src/auth/config/msalConfig.ts

- client/src/auth/hooks/useAuth.tsx
  - Imports: client/src/lib/debug.ts, client/src/auth/contexts/AuthContext.tsx, client/src/auth/types

- client/src/auth/components/RoleBasedAccess.tsx
  - Imports: client/src/auth/hooks, client/src/auth/types

- client/src/auth/components/AdminSettings.tsx
  - Imports: client/src/auth/types, client/src/auth/hooks/useAuth.ts, client/src/lib/debug.ts, client/src/auth/components/AdminSettings.css

## Note
Some files may be legitimately unused directly (e.g., types, utilities called via dynamic imports, 
files referenced via webpack/vite plugins, etc.). Further investigation may be required.

Generated on: 2025-05-05T22:52:34.146Z
