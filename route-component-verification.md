# Route Component Verification

## Overview
This report identifies orphaned components that might be referenced in route definitions
or loaded dynamically, which wouldn't be detected by static import analysis.

## Components Referenced in Routes


### src/auth/routes/AuthRoutes.tsx


- **Referenced in**: src/App.tsx:193
- **Pattern**: element prop
- **Context**: `<Route path="/auth/*" element={<AuthRoutes />} />`

- **Referenced in**: src/App.tsx:223
- **Pattern**: element prop
- **Context**: `<Route path="/auth/*" element={<AuthRoutes />} />`

- **Referenced in**: client/src/App.tsx:229
- **Pattern**: element prop
- **Context**: `<Route path="/auth/*" element={<AuthRoutes defaultRedirectPath="/" />} />`



### src/auth/components/AuthCallback.tsx


- **Referenced in**: client/src/App.tsx:165
- **Pattern**: element prop
- **Context**: `<Route path="/auth/callback" element={<AuthCallback />} />`



### server/src/routes/api.ts


- **Referenced in**: client/src/index.tsx:9
- **Pattern**: string reference
- **Context**: `DEBUG.setVerbosity('api', VerbosityLevel.WARN);       // Only warnings and errors`



### client/src/components/auth/AuthCallback.tsx


- **Referenced in**: client/src/App.tsx:165
- **Pattern**: element prop
- **Context**: `<Route path="/auth/callback" element={<AuthCallback />} />`



### client/src/auth/routes/AuthRoutes.tsx


- **Referenced in**: src/App.tsx:193
- **Pattern**: element prop
- **Context**: `<Route path="/auth/*" element={<AuthRoutes />} />`

- **Referenced in**: src/App.tsx:223
- **Pattern**: element prop
- **Context**: `<Route path="/auth/*" element={<AuthRoutes />} />`

- **Referenced in**: client/src/App.tsx:229
- **Pattern**: element prop
- **Context**: `<Route path="/auth/*" element={<AuthRoutes defaultRedirectPath="/" />} />`




## Components Not Found in Routes

These components were not found in any routing configuration and are more likely to be truly orphaned:

- src/services/apiMetrics.js
- src/auth/services/authApi.ts
- src/auth/providers/LocalProvider.ts
- src/auth/config/msalConfig.ts
- src/auth/components/RoleBasedAccess.tsx
- src/auth/components/LocalLogin.tsx
- src/auth/components/AdminSettings.tsx
- shared/models/MetricModels.ts
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
- client/src/auth/types.ts
- client/src/auth/utils/state.ts
- client/src/auth/services/authApi.ts
- client/src/auth/providers/MsalProvider.tsx
- client/src/auth/hooks/useAuth.tsx
- client/src/auth/components/RoleBasedAccess.tsx
- client/src/auth/components/AdminSettings.tsx

## Recommendation

1. Components referenced in routes should be preserved even if they appear orphaned in static analysis
2. Components not found in routes should be further verified for dynamic imports or consider archiving them
3. Some components might be loaded through a dynamic mechanism not detected by this script (e.g., eval, reflection)

Generated on: 2025-05-05T22:52:34.456Z
