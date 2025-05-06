# Potentially Orphaned Files
  
## Overview
This report identifies files in the codebase that are not imported by any other files and may be orphaned.
This enhanced analysis includes barrel file (index.ts) re-exports and route component references.

Total files analyzed: 283
Potentially orphaned files: 64

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

## Note
Some files may be legitimately unused directly (e.g., types, utilities called via dynamic imports, 
files referenced via webpack/vite plugins, etc.). Further investigation may be required.

## Barrel Files Analysis
The following barrel files (index.ts/js) were analyzed for re-exports:


### src/auth/index.ts
- Exports AuthContext from src/auth/contexts/AuthContext.tsx
- Exports AuthProvider from src/auth/contexts/AuthContext.tsx
- Exports useAuth from src/auth/hooks/useAuth.ts
- Exports useHasRole from src/auth/hooks/index.ts
- Exports useIsAdmin from src/auth/hooks/index.ts
- Exports useHasAnyRole from src/auth/hooks/index.ts
- Exports useHasAllRoles from src/auth/hooks/index.ts
- Exports useAuthToken from src/auth/hooks/index.ts
- Exports ProtectedRoute from src/auth/components/index.ts
- Exports RoleBasedAccess from src/auth/components/RoleBasedAccess.tsx
- Exports Can from src/auth/components/RoleBasedAccess.tsx
- Exports AuthProvider as default from src/auth/contexts/AuthContext.tsx


### src/auth/providers/index.ts
- Exports ./BaseAuthProvider from src/auth/providers/BaseAuthProvider.ts
- Exports ./EntraIdProvider from src/auth/providers/EntraIdProvider.ts
- Exports ./OAuthProvider from src/auth/providers/OAuthProvider.ts
- Exports ./SamlProvider from src/auth/providers/SamlProvider.ts


### src/auth/integration/index.tsx



### src/auth/hooks/index.ts
- Exports useAuth from src/auth/hooks/useAuth.ts


### src/auth/components/index.ts
- Exports default as ProtectedRoute from src/auth/components/ProtectedRoute.tsx
- Exports default as RoleBasedAccess from src/auth/components/RoleBasedAccess.tsx
- Exports Can from src/auth/components/RoleBasedAccess.tsx
- Exports default as Login from src/auth/components/Login.tsx
- Exports default as AuthCallback from src/auth/components/AuthCallback.tsx
- Exports default as AdminSettings from src/auth/components/AdminSettings.tsx
- Exports ProtectedRoute from src/auth/components/ProtectedRoute.tsx
- Exports RoleBasedAccess from src/auth/components/RoleBasedAccess.tsx
- Exports Can from src/auth/components/RoleBasedAccess.tsx
- Exports Login from src/auth/components/Login.tsx
- Exports AuthCallback from src/auth/components/AuthCallback.tsx
- Exports AdminSettings from src/auth/components/AdminSettings.tsx
- Exports ./LocalLogin from src/auth/components/LocalLogin.tsx


### shared/index.ts
- Exports ./models from shared/models/index.ts


### shared/models/index.ts
- Exports ./MetricModels from shared/models/MetricModels.ts


### shared/components/auth/index.ts



### client/src/index.tsx



### client/src/routes/index.tsx



### client/src/components/ui/index.ts



### client/src/auth/index.ts
- Exports AuthContext from client/src/auth/contexts/AuthContext.tsx
- Exports AuthProvider from client/src/auth/contexts/AuthContext.tsx
- Exports useAuth from client/src/auth/hooks/useAuth.ts
- Exports useHasRole from client/src/auth/hooks/index.ts
- Exports useIsAdmin from client/src/auth/hooks/index.ts
- Exports useHasAnyRole from client/src/auth/hooks/index.ts
- Exports useHasAllRoles from client/src/auth/hooks/index.ts
- Exports useAuthToken from client/src/auth/hooks/index.ts
- Exports default as ProtectedRoute from client/src/auth/components/ProtectedRoute.tsx
- Exports RoleBasedAccess from client/src/auth/components/RoleBasedAccess.tsx
- Exports Can from client/src/auth/components/RoleBasedAccess.tsx
- Exports AuthProvider as default from client/src/auth/contexts/AuthContext.tsx
- Exports ProtectedRoute from client/src/auth/components/ProtectedRoute.tsx


### client/src/auth/utils/index.ts
- Exports ./auth from client/src/auth/utils/auth.ts
- Exports ./storage from client/src/auth/utils/storage.ts


### client/src/auth/types/index.ts



### client/src/auth/providers/index.ts
- Exports ./BaseAuthProvider from client/src/auth/providers/BaseAuthProvider.ts
- Exports ./EntraIdProvider from client/src/auth/providers/EntraIdProvider.ts
- Exports ./OAuthProvider from client/src/auth/providers/OAuthProvider.ts
- Exports ./SamlProvider from client/src/auth/providers/SamlProvider.ts
- Exports ./LocalProvider from client/src/auth/providers/LocalProvider


### client/src/auth/integration/index.tsx



### client/src/auth/hooks/index.ts
- Exports useAuth from client/src/auth/hooks/useAuth.ts


### client/src/auth/components/index.ts
- Exports default as ProtectedRoute from client/src/auth/components/ProtectedRoute.tsx
- Exports default as RoleBasedAccess from client/src/auth/components/RoleBasedAccess.tsx
- Exports Can from client/src/auth/components/RoleBasedAccess.tsx
- Exports default as Login from client/src/auth/components/Login.tsx
- Exports default as AuthCallback from client/src/auth/components/AuthCallback.tsx
- Exports default as AdminSettings from client/src/auth/components/AdminSettings.tsx
- Exports ProtectedRoute from client/src/auth/components/ProtectedRoute.tsx
- Exports RoleBasedAccess from client/src/auth/components/RoleBasedAccess.tsx
- Exports Can from client/src/auth/components/RoleBasedAccess.tsx
- Exports Login from client/src/auth/components/Login.tsx
- Exports AuthCallback from client/src/auth/components/AuthCallback.tsx
- Exports AdminSettings from client/src/auth/components/AdminSettings.tsx


## Route Component References
The following component references were found in route definitions:


### SrcProtectedRoute
Referenced in: src/App.tsx


### ProtectedRoute
Referenced in: client/src/App.tsx


Generated on: 2025-05-05T22:59:30.221Z
