# Dependency Analysis Report

## File Dependencies

### tsconfig.node.json
Imports:
- None

Imported by:
- None


### tsconfig.json
Imports:
- None

Imported by:
- None


### tsconfig.app.json
Imports:
- None

Imported by:
- None


### staticwebapp.config.json
Imports:
- None

Imported by:
- None


### package.json
Imports:
- None

Imported by:
- None


### package-lock.json
Imports:
- None

Imported by:
- None


### mock-db-schema.json
Imports:
- None

Imported by:
- None


### eslint.config.js
Imports:
- None

Imported by:
- None


### dependency-graph.json
Imports:
- None

Imported by:
- None


### src/main.tsx
Imports:
- src/App.tsx
- src/services/azureClient.js
- src/auth

Imported by:
- None


### src/App.tsx
Imports:
- src/contexts/AbilityContext.tsx
- src/contexts/DataContext.tsx
- src/components/Dashboard.tsx
- src/components/XLADetailView.tsx
- src/components/SettingsPage.tsx
- src/components/ReleaseNotesPage.tsx
- src/components/Sidebar.tsx
- src/components/modules/IntelliAsset.tsx
- src/components/modules/IntelliCX.tsx
- src/components/modules/IntelliEX.tsx
- src/components/modules/IntelliSpaces.tsx
- src/components/modules/IntelliHealth.tsx
- src/components/modules/IntelliNetwork.tsx
- src/components/AlertTicker.tsx
- src/components/GlobalAdminPage.tsx
- src/components/ErrorBoundary.tsx
- src/pages/ServiceMonitoringPage.tsx
- src/auth
- src/auth/components/ProtectedRoute.tsx
- src/components/AssetErrorFallback.tsx
- src/components/AdminSettingsPage.tsx
- src/routes/XLAConfiguration.tsx
- src/routes/AuthRoutes.tsx
- src/auth/components/Login.tsx
- src/pages/HelpPage.tsx

Imported by:
- src/main.tsx


### src/types/xla.ts
Imports:
- None

Imported by:
- src/routes/XLAConfiguration.tsx
- src/lib/services/ApiXliMappingService.ts
- src/data/xlaData.ts
- src/components/XLADetailView.tsx
- src/components/XLAConfigPanel.tsx
- src/components/Dashboard.tsx
- src/components/configuration/XLAConfigurationPanel.tsx


### src/types/env.d.ts
Imports:
- None

Imported by:
- None


### src/services/mockDataProvider.js
Imports:
- None

Imported by:
- src/services/azureClient.js


### src/services/azureClient.js
Imports:
- src/services/mockDataProvider.js

Imported by:
- src/main.tsx
- src/lib/db.ts
- src/components/Dashboard.tsx


### src/services/apiMetrics.js
Imports:
- None

Imported by:
- None


### src/services/SettingsService.ts
Imports:
- src/lib/db.ts
- src/lib/logger.ts
- src/lib/releaseNotes.ts

Imported by:
- src/components/ReleaseNotesPage.tsx
- src/components/Dashboard.tsx


### src/services/MonitoringService.ts
Imports:
- src/lib/db.ts

Imported by:
- src/pages/ServiceMonitoringPage.tsx


### src/services/GlobalSettingsService.ts
Imports:
- src/lib/db.ts
- src/lib/logger.ts
- src/lib/debug.ts

Imported by:
- src/components/GlobalSettings.tsx


### src/routes/XLAConfiguration.tsx
Imports:
- src/components/configuration/XLAConfigurationPanel.tsx
- src/types/xla.ts

Imported by:
- src/App.tsx


### src/routes/AuthRoutes.tsx
Imports:
- src/auth/components
- src/lib/debug.ts
- src/auth/types

Imported by:
- src/App.tsx


### src/pages/ServiceMonitoringPage.tsx
Imports:
- src/services/MonitoringService.ts

Imported by:
- src/App.tsx


### src/pages/HelpPage.tsx
Imports:
- None

Imported by:
- src/App.tsx


### src/lib/version.ts
Imports:
- src/lib/releaseNotes.ts

Imported by:
- src/components/ReleaseNotesPage.tsx
- src/auth/components/Login.tsx


### src/lib/settings.ts
Imports:
- src/lib/db.ts
- src/lib/logger.ts

Imported by:
- src/components/SettingsPage.tsx
- src/components/settings/DataSourcesSection.tsx
- src/components/settings/DataSourceConfig.tsx


### src/lib/releaseNotes.ts
Imports:
- None

Imported by:
- src/services/SettingsService.ts
- src/lib/version.ts
- src/components/ReleaseNotesPage.tsx


### src/lib/logger.ts
Imports:
- None

Imported by:
- src/services/SettingsService.ts
- src/services/GlobalSettingsService.ts
- src/lib/settings.ts
- src/lib/db.ts
- src/components/XLADetailView.tsx
- src/components/XLAConfigPanel.tsx
- src/components/XLAChart.tsx
- src/components/UserManagement.tsx
- src/components/SettingsPage.tsx
- src/components/ReleaseNotesPage.tsx
- src/components/Dashboard.tsx
- src/auth/components/Login.tsx


### src/lib/debug.ts
Imports:
- None

Imported by:
- src/services/GlobalSettingsService.ts
- src/routes/AuthRoutes.tsx
- src/lib/services/ApiXliMappingService.ts
- src/contexts/DataContext.tsx
- src/components/Sidebar.tsx
- src/components/SettingsPage.tsx
- src/components/GlobalSettings.tsx
- src/components/ErrorBoundary.tsx
- src/components/configuration/XLAConfigurationPanel.tsx
- src/auth/utils/storage.ts
- src/auth/utils/auth.ts
- src/auth/storage/AuthStateManager.ts
- src/auth/services/authApi.ts
- src/auth/routes/AuthRoutes.tsx
- src/auth/providers/index.ts
- src/auth/providers/SamlProvider.ts
- src/auth/providers/OAuthProvider.ts
- src/auth/providers/MsalProvider.ts
- src/auth/providers/LocalProvider.ts
- src/auth/providers/EntraIdProvider.ts
- src/auth/providers/BaseAuthProvider.ts
- src/auth/integration/index.tsx
- src/auth/hooks/useAuth.ts
- src/auth/contexts/AuthContext.tsx
- src/auth/config/msalConfig.ts
- src/auth/components/ProtectedRoute.tsx
- src/auth/components/Login.tsx
- src/auth/components/LocalLogin.tsx
- src/auth/components/AuthCallback.tsx
- src/auth/components/AdminSettings.tsx


### src/lib/db.ts
Imports:
- src/lib/logger.ts
- src/services/azureClient.js

Imported by:
- src/services/SettingsService.ts
- src/services/MonitoringService.ts
- src/services/GlobalSettingsService.ts
- src/lib/settings.ts
- src/lib/services/SettingsService.ts
- src/lib/services/ApiXliMappingService.ts
- src/components/XLADetailView.tsx
- src/components/XLAConfigPanel.tsx
- src/components/XLAChart.tsx
- src/components/UserManagement.tsx
- src/components/GlobalAdminPage.tsx


### src/lib/ability.ts
Imports:
- None

Imported by:
- src/contexts/AbilityContext.tsx


### src/lib/services/SettingsService.ts
Imports:
- src/lib/db.ts

Imported by:
- src/components/settings/DataSourcesSection.tsx


### src/lib/services/ApiXliMappingService.ts
Imports:
- src/lib/db.ts
- src/lib/debug.ts
- src/types/xla.ts

Imported by:
- src/components/configuration/XLAConfigurationPanel.tsx


### src/data/xlaData.ts
Imports:
- src/types/xla.ts

Imported by:
- src/components/XLAConfigPanel.tsx
- src/components/Dashboard.tsx


### src/contexts/DataContext.tsx
Imports:
- src/auth
- src/lib/debug.ts

Imported by:
- src/App.tsx


### src/contexts/AbilityContext.tsx
Imports:
- src/lib/ability.ts

Imported by:
- src/App.tsx


### src/components/XLADetailView.tsx
Imports:
- src/types/xla.ts
- src/lib/db.ts
- src/lib/logger.ts

Imported by:
- src/App.tsx


### src/components/XLAConfigPanel.tsx
Imports:
- src/types/xla.ts
- src/data/xlaData.ts
- src/lib/db.ts
- src/lib/logger.ts

Imported by:
- src/components/SettingsPage.tsx


### src/components/XLAChart.tsx
Imports:
- src/components/common/DataSourceInfo.tsx
- src/lib/db.ts
- src/lib/logger.ts

Imported by:
- src/components/Dashboard.tsx


### src/components/UserManagement.tsx
Imports:
- src/lib/db.ts
- src/lib/logger.ts

Imported by:
- src/components/GlobalAdminPage.tsx


### src/components/Sidebar.tsx
Imports:
- src/auth
- src/lib/debug.ts

Imported by:
- src/App.tsx


### src/components/SettingsPage.tsx
Imports:
- src/auth
- src/components/settings/DataSourcesSection.tsx
- src/lib/logger.ts
- src/lib/debug.ts
- src/lib/settings.ts
- src/components/XLAConfigPanel.tsx

Imported by:
- src/App.tsx


### src/components/RoleManagement.tsx
Imports:
- None

Imported by:
- src/components/GlobalAdminPage.tsx


### src/components/ReleaseNotesPage.tsx
Imports:
- src/lib/version.ts
- src/services/SettingsService.ts
- src/lib/logger.ts
- src/lib/releaseNotes.ts

Imported by:
- src/App.tsx


### src/components/OverallScoreCard.tsx
Imports:
- src/components/common/DataSourceInfo.tsx

Imported by:
- src/components/Dashboard.tsx


### src/components/GlobalSettings.tsx
Imports:
- src/services/GlobalSettingsService.ts
- src/lib/debug.ts

Imported by:
- src/components/GlobalAdminPage.tsx
- src/components/AdminSettingsPage.tsx


### src/components/GlobalAdminPage.tsx
Imports:
- src/lib/db.ts
- src/components/RoleManagement.tsx
- src/components/UserManagement.tsx
- src/components/GlobalSettings.tsx

Imported by:
- src/App.tsx


### src/components/ErrorBoundary.tsx
Imports:
- src/lib/debug.ts

Imported by:
- src/App.tsx


### src/components/Dashboard.tsx
Imports:
- src/components/XLAChart.tsx
- src/components/OverallScoreCard.tsx
- src/components/common/DataSourceInfo.tsx
- src/services/azureClient.js
- src/lib/logger.ts
- src/types/xla.ts
- src/data/xlaData.ts
- src/services/SettingsService.ts

Imported by:
- src/App.tsx


### src/components/AssetErrorFallback.tsx
Imports:
- None

Imported by:
- src/App.tsx


### src/components/AlertTicker.tsx
Imports:
- None

Imported by:
- src/App.tsx


### src/components/AdminSettingsPage.tsx
Imports:
- src/components/GlobalSettings.tsx

Imported by:
- src/App.tsx


### src/components/settings/DataSourcesSection.tsx
Imports:
- src/components/settings/DataSourceConfig.tsx
- src/lib/settings.ts
- src/auth
- src/lib/services/SettingsService.ts

Imported by:
- src/components/SettingsPage.tsx


### src/components/settings/DataSourceConfig.tsx
Imports:
- src/lib/settings.ts

Imported by:
- src/components/settings/DataSourcesSection.tsx


### src/components/modules/IntelliSpaces.tsx
Imports:
- None

Imported by:
- src/App.tsx


### src/components/modules/IntelliNetwork.tsx
Imports:
- src/components/common/MetricCard.tsx
- src/components/common/ProgressBar.tsx
- src/components/common/DataSourceInfo.tsx

Imported by:
- src/App.tsx


### src/components/modules/IntelliHealth.tsx
Imports:
- src/components/common/MetricCard.tsx
- src/components/common/ProgressBar.tsx
- src/components/common/DataSourceInfo.tsx

Imported by:
- src/App.tsx


### src/components/modules/IntelliEX.tsx
Imports:
- None

Imported by:
- src/App.tsx


### src/components/modules/IntelliCX.tsx
Imports:
- src/components/common/DataSourceInfo.tsx

Imported by:
- src/App.tsx


### src/components/modules/IntelliAsset.tsx
Imports:
- src/components/common/MetricCard.tsx
- src/components/common/ProgressBar.tsx
- src/components/common/DataSourceInfo.tsx

Imported by:
- src/App.tsx


### src/components/configuration/XLAConfigurationPanel.tsx
Imports:
- src/types/xla.ts
- src/auth
- src/lib/services/ApiXliMappingService.ts
- src/lib/debug.ts

Imported by:
- src/routes/XLAConfiguration.tsx


### src/components/common/ProgressBar.tsx
Imports:
- None

Imported by:
- src/components/modules/IntelliNetwork.tsx
- src/components/modules/IntelliHealth.tsx
- src/components/modules/IntelliAsset.tsx


### src/components/common/MetricCard.tsx
Imports:
- src/components/common/DataSourceInfo.tsx

Imported by:
- src/components/modules/IntelliNetwork.tsx
- src/components/modules/IntelliHealth.tsx
- src/components/modules/IntelliAsset.tsx


### src/components/common/DataSourceInfo.tsx
Imports:
- None

Imported by:
- src/components/XLAChart.tsx
- src/components/OverallScoreCard.tsx
- src/components/Dashboard.tsx
- src/components/modules/IntelliNetwork.tsx
- src/components/modules/IntelliHealth.tsx
- src/components/modules/IntelliCX.tsx
- src/components/modules/IntelliAsset.tsx
- src/components/common/MetricCard.tsx


### src/auth/index.ts
Imports:
- None

Imported by:
- src/auth/integration/index.tsx


### src/auth/utils/storage.ts
Imports:
- src/lib/debug.ts
- src/auth/types

Imported by:
- src/auth/providers/SamlProvider.ts
- src/auth/providers/OAuthProvider.ts
- src/auth/contexts/AuthContext.tsx


### src/auth/utils/auth.ts
Imports:
- src/lib/debug.ts
- src/auth/types

Imported by:
- src/auth/providers/SamlProvider.ts
- src/auth/providers/OAuthProvider.ts
- src/auth/contexts/AuthContext.tsx


### src/auth/storage/AuthStateManager.ts
Imports:
- src/lib/debug.ts
- src/auth/types

Imported by:
- src/auth/providers/EntraIdProvider.ts
- src/auth/providers/BaseAuthProvider.ts


### src/auth/services/authApi.ts
Imports:
- src/lib/debug.ts
- src/auth/types
- src/auth/hooks/useAuth.ts

Imported by:
- None


### src/auth/routes/AuthRoutes.tsx
Imports:
- src/auth/components
- src/lib/debug.ts
- src/auth/types

Imported by:
- None


### src/auth/providers/index.ts
Imports:
- src/lib/debug.ts
- src/auth/types
- src/auth/providers/BaseAuthProvider.ts
- src/auth/providers/EntraIdProvider.ts
- src/auth/providers/OAuthProvider.ts
- src/auth/providers/SamlProvider.ts

Imported by:
- None


### src/auth/providers/SamlProvider.ts
Imports:
- src/lib/debug.ts
- src/auth/types
- src/auth/providers/BaseAuthProvider.ts
- src/auth/utils/auth.ts
- src/auth/utils/storage.ts

Imported by:
- src/auth/providers/index.ts


### src/auth/providers/OAuthProvider.ts
Imports:
- src/lib/debug.ts
- src/auth/types
- src/auth/providers/BaseAuthProvider.ts
- src/auth/utils/auth.ts
- src/auth/utils/storage.ts

Imported by:
- src/auth/providers/index.ts


### src/auth/providers/MsalProvider.ts
Imports:
- src/lib/debug.ts

Imported by:
- src/auth/providers/EntraIdProvider.ts


### src/auth/providers/LocalProvider.ts
Imports:
- src/lib/debug.ts
- src/auth/types
- src/auth/providers/BaseAuthProvider.ts

Imported by:
- None


### src/auth/providers/EntraIdProvider.ts
Imports:
- src/lib/debug.ts
- src/auth/types
- src/auth/providers/BaseAuthProvider.ts
- src/auth/providers/MsalProvider.ts
- src/auth/storage/AuthStateManager.ts

Imported by:
- src/auth/providers/index.ts


### src/auth/providers/BaseAuthProvider.ts
Imports:
- src/lib/debug.ts
- src/auth/types
- src/auth/storage/AuthStateManager.ts

Imported by:
- src/auth/providers/index.ts
- src/auth/providers/SamlProvider.ts
- src/auth/providers/OAuthProvider.ts
- src/auth/providers/LocalProvider.ts
- src/auth/providers/EntraIdProvider.ts


### src/auth/integration/index.tsx
Imports:
- src/auth/index.ts
- src/auth/types
- src/lib/debug.ts

Imported by:
- None


### src/auth/hooks/useAuth.ts
Imports:
- src/auth/contexts/AuthContext.tsx
- src/auth/types
- src/lib/debug.ts

Imported by:
- src/auth/services/authApi.ts
- src/auth/hooks/index.ts
- src/auth/components/Login.tsx
- src/auth/components/LocalLogin.tsx
- src/auth/components/AdminSettings.tsx


### src/auth/hooks/index.ts
Imports:
- src/auth/types
- src/auth/hooks/useAuth.ts

Imported by:
- None


### src/auth/contexts/AuthContext.tsx
Imports:
- src/lib/debug.ts
- src/auth/types
- src/auth/providers
- src/auth/utils/storage.ts
- src/auth/utils/auth.ts

Imported by:
- src/auth/hooks/useAuth.ts
- src/auth/components/Login.tsx
- src/auth/components/AuthCallback.tsx


### src/auth/config/msalConfig.ts
Imports:
- src/lib/debug.ts

Imported by:
- None


### src/auth/components/index.ts
Imports:
- None

Imported by:
- None


### src/auth/components/RoleBasedAccess.tsx
Imports:
- src/auth/hooks
- src/auth/types

Imported by:
- None


### src/auth/components/ProtectedRoute.tsx
Imports:
- src/lib/debug.ts
- src/auth/hooks
- src/auth/types

Imported by:
- src/App.tsx


### src/auth/components/Login.tsx
Imports:
- src/auth/hooks/useAuth.ts
- src/auth/types
- src/lib/logger.ts
- src/lib/version.ts
- src/auth/contexts/AuthContext.tsx
- src/lib/debug.ts

Imported by:
- src/App.tsx


### src/auth/components/LocalLogin.tsx
Imports:
- src/auth/hooks/useAuth.ts
- src/lib/debug.ts

Imported by:
- None


### src/auth/components/AuthCallback.tsx
Imports:
- src/auth/contexts/AuthContext.tsx
- src/lib/debug.ts

Imported by:
- None


### src/auth/components/AdminSettings.tsx
Imports:
- src/auth/types
- src/auth/hooks/useAuth.ts
- src/lib/debug.ts

Imported by:
- None


### shared/tsconfig.json
Imports:
- None

Imported by:
- None


### shared/package.json
Imports:
- None

Imported by:
- None


### shared/index.ts
Imports:
- None

Imported by:
- None


### shared/models/index.ts
Imports:
- None

Imported by:
- None


### shared/models/MetricModels.ts
Imports:
- None

Imported by:
- None


### shared/components/auth/index.ts
Imports:
- None

Imported by:
- None


### server/package.json
Imports:
- None

Imported by:
- None


### server/src/services/azureClient.ts
Imports:
- None

Imported by:
- server/src/routes/api.ts


### server/src/routes/api.ts
Imports:
- server/src/services/azureClient.ts

Imported by:
- None


### secure_credentials/app_connection_example.js
Imports:
- None

Imported by:
- None


### scripts/package.json
Imports:
- None

Imported by:
- None


### scripts/package-lock.json
Imports:
- None

Imported by:
- None


### scripts/find-cross-deps.js
Imports:
- None

Imported by:
- None


### scripts/db-seed.js
Imports:
- None

Imported by:
- None


### scripts/db-init.js
Imports:
- None

Imported by:
- None


### public/module-loader.js
Imports:
- None

Imported by:
- None


### public/scripts/env-config.js
Imports:
- None

Imported by:
- None


### functions/tsconfig.json
Imports:
- None

Imported by:
- None


### functions/package.json
Imports:
- None

Imported by:
- None


### functions/package-lock.json
Imports:
- None

Imported by:
- None


### functions/host.json
Imports:
- None

Imported by:
- None


### functions/src/functions/api-clients.ts
Imports:
- None

Imported by:
- None


### docs/dependency-analysis/dependency-graph.json
Imports:
- None

Imported by:
- None


### client/vite.config.ts
Imports:
- None

Imported by:
- None


### client/tsconfig.node.json
Imports:
- None

Imported by:
- None


### client/tsconfig.json
Imports:
- None

Imported by:
- None


### client/tsconfig.check.json
Imports:
- None

Imported by:
- None


### client/tailwind.config.js
Imports:
- None

Imported by:
- None


### client/postcss.config.js
Imports:
- None

Imported by:
- None


### client/package.json
Imports:
- None

Imported by:
- None


### client/azure-app-service.config.json
Imports:
- None

Imported by:
- None


### client/src/vite-env.d.ts
Imports:
- None

Imported by:
- None


### client/src/main.tsx
Imports:
- client/src/index.css
- client/src/App.tsx
- client/src/services/azureClient.js
- client/src/auth

Imported by:
- None


### client/src/main.ts
Imports:
- None

Imported by:
- None


### client/src/index.tsx
Imports:
- client/src/lib/debug.ts

Imported by:
- None


### client/src/index.css
Imports:
- None

Imported by:
- client/src/main.tsx


### client/src/environment.d.ts
Imports:
- None

Imported by:
- None


### client/src/App.tsx
Imports:
- client/src/auth
- client/src/auth/components/ProtectedRoute.tsx
- client/src/lib/debug.ts
- client/src/types/auth.ts
- client/src/contexts/AbilityContext.tsx
- client/src/contexts/TickerContext.tsx
- client/src/contexts/DataContext.tsx
- client/src/components/Dashboard.tsx
- client/src/components/XLADetailView.tsx
- client/src/components/SettingsPage.tsx
- client/src/components/ReleaseNotesPage.tsx
- client/src/components/Sidebar.tsx
- client/src/components/modules/IntelliAsset.tsx
- client/src/components/modules/IntelliCX.tsx
- client/src/components/modules/IntelliEX.tsx
- client/src/components/modules/IntelliSpaces.tsx
- client/src/components/modules/IntelliHealth.tsx
- client/src/components/modules/IntelliNetwork.tsx
- client/src/components/AlertTicker.tsx
- client/src/components/GlobalAdminPage.tsx
- client/src/components/TenantAdminPage.tsx
- client/src/components/ErrorBoundary.tsx
- client/src/pages/ServiceMonitoringPage.tsx
- client/src/components/AdminSettingsPage.tsx
- client/src/routes/XLAConfiguration.tsx
- client/src/routes/AuthRoutes.tsx
- client/src/pages/AuthDocumentation.tsx
- client/src/auth/components/Login.tsx
- client/src/auth/components/AuthCallback.tsx
- client/src/pages/HelpPage.tsx
- client/src/pages/api/ApiConfigPage.tsx
- client/src/auth/components/AccessDenied.tsx
- client/src/components/Profile.tsx
- client/src/components/Settings
- client/src/components/AdminRoutes.tsx

Imported by:
- client/src/main.tsx


### client/src/types/xla.ts
Imports:
- None

Imported by:
- client/src/routes/XLAConfiguration.tsx
- client/src/lib/validation/xlaValidation.ts
- client/src/lib/services/XLAService.ts
- client/src/lib/services/ExternalAPIService.ts
- client/src/lib/services/ApiXliMappingService.ts
- client/src/data/xlaData.ts
- client/src/components/XLADetailView.tsx
- client/src/components/XLAConfigPanel.tsx
- client/src/components/Dashboard.tsx
- client/src/components/configuration/XLAConfigurationPanel.tsx


### client/src/types/settings.ts
Imports:
- None

Imported by:
- client/src/lib/services/SettingsService.ts
- client/src/components/TenantManagement.tsx
- client/src/components/settings/DataSourcesSection.tsx


### client/src/types/env.d.ts
Imports:
- None

Imported by:
- None


### client/src/types/debug.d.ts
Imports:
- None

Imported by:
- None


### client/src/types/database.ts
Imports:
- None

Imported by:
- client/src/services/GlobalSettingsService.ts
- client/src/lib/services/SettingsService.ts


### client/src/types/auth.ts
Imports:
- None

Imported by:
- client/src/App.tsx
- client/src/lib/abilityUtils.ts
- client/src/lib/ability.ts
- client/src/contexts/AbilityContext.tsx


### client/src/services/xliSchedulerService.js
Imports:
- client/src/services/azureClient.js
- client/src/services/xlaApiService.js

Imported by:
- None


### client/src/services/xlaApiService.js
Imports:
- client/src/services/azureClient.js
- client/src/services/apiResilience.js
- client/src/services/dataValidation.js
- client/src/services/apiMetrics.js

Imported by:
- client/src/services/xliSchedulerService.js


### client/src/services/mockMetricsApi.js
Imports:
- None

Imported by:
- client/src/services/apiMetrics.js


### client/src/services/mockDataProvider.js
Imports:
- None

Imported by:
- client/src/services/azureClient.js


### client/src/services/dbTest.js
Imports:
- None

Imported by:
- None


### client/src/services/dataValidation.js
Imports:
- None

Imported by:
- client/src/services/xlaApiService.js


### client/src/services/azureClient.js
Imports:
- client/src/services/mockDataProvider.js

Imported by:
- client/src/main.tsx
- client/src/services/xliSchedulerService.js
- client/src/services/xlaApiService.js
- client/src/lib/db.ts


### client/src/services/azureClient.d.ts
Imports:
- None

Imported by:
- None


### client/src/services/apiResilience.js
Imports:
- None

Imported by:
- client/src/services/xlaApiService.js


### client/src/services/apiMetrics.js
Imports:
- client/src/services/mockMetricsApi.js

Imported by:
- client/src/services/xlaApiService.js


### client/src/services/SettingsService.ts
Imports:
- client/src/lib/db.ts
- client/src/lib/logger.ts
- client/src/lib/releaseNotes.ts

Imported by:
- client/src/components/ReleaseNotesPage.tsx


### client/src/services/MonitoringService.ts
Imports:
- client/src/lib/db.ts

Imported by:
- client/src/pages/ServiceMonitoringPage.tsx


### client/src/services/GlobalSettingsService.ts
Imports:
- client/src/lib/db.ts
- client/src/types/database.ts
- client/src/lib/debug.ts

Imported by:
- client/src/components/GlobalSettings.tsx


### client/src/routes/index.tsx
Imports:
- client/src/auth/components
- client/src/components/Dashboard.tsx
- client/src/routes/XLAConfiguration.tsx
- client/src/pages/api/ApiConfigPage.tsx
- client/src/pages/charts/ChartDashboardPage.tsx
- client/src/routes/ChartRoutes.tsx

Imported by:
- None


### client/src/routes/XLAConfiguration.tsx
Imports:
- client/src/components/configuration/XLAConfigurationPanel.tsx
- client/src/lib/services/ExternalAPIService.ts
- client/src/lib/services/XLAService.ts
- client/src/types/xla.ts

Imported by:
- client/src/App.tsx
- client/src/routes/index.tsx


### client/src/routes/ChartRoutes.tsx
Imports:
- client/src/auth/components
- client/src/pages/charts/ChartDashboardPage.tsx

Imported by:
- client/src/routes/index.tsx


### client/src/routes/AuthRoutes.tsx
Imports:
- client/src/auth/components
- client/src/lib/debug.ts
- client/src/auth/types

Imported by:
- client/src/App.tsx


### client/src/pages/ServiceMonitoringPage.tsx
Imports:
- client/src/components/ui/button.tsx
- client/src/components/ui/card.tsx
- client/src/services/MonitoringService.ts
- client/src/components/ui/tabs.tsx
- client/src/components/ui/table.tsx
- client/src/components/ui/badge.tsx
- client/src/components/ui/use-toast.ts
- client/src/components/ui/input.tsx

Imported by:
- client/src/App.tsx


### client/src/pages/HelpPage.tsx
Imports:
- client/src/components/ui/button.tsx
- client/src/components/ui/input.tsx
- client/src/components/ui/card.tsx
- client/src/components/ui/tabs.tsx

Imported by:
- client/src/App.tsx


### client/src/pages/AuthDocumentation.tsx
Imports:
- client/src/pages/AuthDocumentation.css
- client/src/pages/auth

Imported by:
- client/src/App.tsx


### client/src/pages/AuthDocumentation.css
Imports:
- None

Imported by:
- client/src/pages/AuthDocumentation.tsx


### client/src/pages/charts/ChartDashboardPage.tsx
Imports:
- client/src/auth
- client/src/pages/charts/ChartDashboardPage.css

Imported by:
- client/src/routes/index.tsx
- client/src/routes/ChartRoutes.tsx


### client/src/pages/charts/ChartDashboardPage.css
Imports:
- None

Imported by:
- client/src/pages/charts/ChartDashboardPage.tsx


### client/src/pages/auth/LoginTroubleshooting.tsx
Imports:
- None

Imported by:
- client/src/auth/routes/AuthRoutes.tsx


### client/src/pages/api/ApiConfigPage.tsx
Imports:
- client/src/auth/hooks/useAuth.ts
- client/src/auth/types
- client/src/components/api/ApiConfigWizard.tsx
- client/src/lib/debug.ts
- client/src/pages/api/ApiConfigPage.css

Imported by:
- client/src/App.tsx
- client/src/routes/index.tsx


### client/src/pages/api/ApiConfigPage.css
Imports:
- None

Imported by:
- client/src/pages/api/ApiConfigPage.tsx


### client/src/lib/version.ts
Imports:
- client/src/lib/releaseNotes.ts

Imported by:
- client/src/components/ReleaseNotesPage.tsx
- client/src/components/LoginPage.tsx
- client/src/auth/components/Login.tsx


### client/src/lib/utils.ts
Imports:
- None

Imported by:
- client/src/components/XLADetailView.tsx
- client/src/components/XLAConfigPanel.tsx
- client/src/components/UserManagement.tsx
- client/src/components/TenantManagement.tsx
- client/src/components/Sidebar.tsx
- client/src/components/SettingsPage.tsx
- client/src/components/ScoreCard.tsx
- client/src/components/OverallScoreCard.tsx
- client/src/components/AlertTicker.tsx
- client/src/components/ui/tooltip.tsx
- client/src/components/ui/tabs.tsx
- client/src/components/ui/table.tsx
- client/src/components/ui/input.tsx
- client/src/components/ui/card.tsx
- client/src/components/ui/button.tsx
- client/src/components/ui/badge.tsx
- client/src/components/shared/Tabs.tsx
- client/src/components/settings/DebugSettings.tsx
- client/src/components/settings/DataSourcesSection.tsx
- client/src/components/settings/DataSourceConfig.tsx
- client/src/components/common/MetricCard.tsx
- client/src/components/common/DateRangePicker.tsx
- client/src/components/common/DataSourceInfo.tsx
- client/src/components/common/CollapsibleCard.tsx


### client/src/lib/tickerUtils.ts
Imports:
- None

Imported by:
- client/src/contexts/TickerContext.tsx


### client/src/lib/sidebarModules.ts
Imports:
- None

Imported by:
- client/src/components/Sidebar.tsx


### client/src/lib/settings.ts
Imports:
- client/src/lib/db.ts
- client/src/lib/logger.ts

Imported by:
- client/src/components/SettingsPage.tsx
- client/src/components/settings/DataSourcesSection.tsx
- client/src/components/settings/DataSourceConfig.tsx


### client/src/lib/releaseNotes.ts
Imports:
- None

Imported by:
- client/src/services/SettingsService.ts
- client/src/lib/version.ts
- client/src/components/ReleaseNotesPage.tsx


### client/src/lib/logger.ts
Imports:
- None

Imported by:
- client/src/services/SettingsService.ts
- client/src/lib/settings.ts
- client/src/lib/db.ts
- client/src/components/XLADetailView.tsx
- client/src/components/XLAConfigPanel.tsx
- client/src/components/XLAChart.tsx
- client/src/components/UserManagement.tsx
- client/src/components/TenantManagement.tsx
- client/src/components/TenantAdminPage.tsx
- client/src/components/SettingsPage.tsx
- client/src/components/ReleaseNotesPage.tsx
- client/src/components/LoginPage.tsx
- client/src/components/Dashboard.tsx
- client/src/components/settings/DebugSettings.tsx
- client/src/auth/components/Login.tsx


### client/src/lib/debug.ts
Imports:
- None

Imported by:
- client/src/index.tsx
- client/src/App.tsx
- client/src/services/GlobalSettingsService.ts
- client/src/routes/AuthRoutes.tsx
- client/src/pages/api/ApiConfigPage.tsx
- client/src/lib/services/ApiXliMappingService.ts
- client/src/contexts/DataContext.tsx
- client/src/components/XLIManager.tsx
- client/src/components/Sidebar.tsx
- client/src/components/SettingsPage.tsx
- client/src/components/GlobalSettings.tsx
- client/src/components/ErrorBoundary.tsx
- client/src/components/ApiClientManager.tsx
- client/src/components/settings/DebugSettings.tsx
- client/src/components/configuration/XLAConfigurationPanel.tsx
- client/src/components/api/ApiConfigWizard.tsx
- client/src/auth/utils/storage.ts
- client/src/auth/utils/state.ts
- client/src/auth/utils/auth.ts
- client/src/auth/services/authApi.ts
- client/src/auth/routes/AuthRoutes.tsx
- client/src/auth/providers/index.ts
- client/src/auth/providers/SamlProvider.ts
- client/src/auth/providers/OAuthProvider.ts
- client/src/auth/providers/MsalProvider.ts
- client/src/auth/providers/EntraIdProvider.ts
- client/src/auth/providers/BaseAuthProvider.ts
- client/src/auth/integration/index.tsx
- client/src/auth/hooks/useAuth.tsx
- client/src/auth/hooks/useAuth.ts
- client/src/auth/contexts/AuthContext.tsx
- client/src/auth/config/msalConfig.ts
- client/src/auth/components/Login.tsx
- client/src/auth/components/AuthCallback.tsx
- client/src/auth/components/AdminSettings.tsx


### client/src/lib/db.ts
Imports:
- client/src/lib/logger.ts
- client/src/services/azureClient.js

Imported by:
- client/src/services/SettingsService.ts
- client/src/services/MonitoringService.ts
- client/src/services/GlobalSettingsService.ts
- client/src/lib/settings.ts
- client/src/lib/services/SettingsService.ts
- client/src/components/XLADetailView.tsx
- client/src/components/XLAConfigPanel.tsx
- client/src/components/UserManagement.tsx
- client/src/components/TenantManagement.tsx
- client/src/components/TenantAdminPage.tsx
- client/src/components/GlobalAdminPage.tsx
- client/src/components/DatabaseTest.tsx
- client/src/components/Dashboard.tsx


### client/src/lib/constants.ts
Imports:
- client/src/constants/text.ts

Imported by:
- None


### client/src/lib/abilityUtils.ts
Imports:
- client/src/lib/ability.ts
- client/src/types/auth.ts

Imported by:
- client/src/lib/abilityHooks.ts
- client/src/contexts/AbilityContext.tsx


### client/src/lib/abilityHooks.ts
Imports:
- client/src/lib/abilityUtils.ts

Imported by:
- None


### client/src/lib/ability.ts
Imports:
- client/src/types/auth.ts

Imported by:
- client/src/lib/abilityUtils.ts
- client/src/contexts/AbilityContext.tsx


### client/src/lib/FallbackData.ts
Imports:
- None

Imported by:
- client/src/components/GlobalAdminPage.tsx


### client/src/lib/validation/xlaValidation.ts
Imports:
- client/src/types/xla.ts

Imported by:
- client/src/components/configuration/XLAConfigurationPanel.tsx


### client/src/lib/services/XLAService.ts
Imports:
- client/src/types/xla.ts
- client/src/lib/services/ExternalAPIService.ts

Imported by:
- client/src/routes/XLAConfiguration.tsx


### client/src/lib/services/SettingsService.ts
Imports:
- client/src/types/settings.ts
- client/src/lib/db.ts
- client/src/types/database.ts

Imported by:
- client/src/components/TenantManagement.tsx
- client/src/components/Dashboard.tsx
- client/src/components/settings/DataSourcesSection.tsx


### client/src/lib/services/MetricAggregationService.ts
Imports:
- None

Imported by:
- None


### client/src/lib/services/ExternalAPIService.ts
Imports:
- client/src/types/xla.ts

Imported by:
- client/src/routes/XLAConfiguration.tsx
- client/src/lib/services/XLAService.ts


### client/src/lib/services/ApiXliMappingService.ts
Imports:
- client/src/lib/debug.ts
- client/src/types/xla.ts

Imported by:
- client/src/components/configuration/XLAConfigurationPanel.tsx


### client/src/lib/auth/errors.ts
Imports:
- None

Imported by:
- client/src/lib/auth/AuthContext.tsx


### client/src/lib/auth/AuthContext.tsx
Imports:
- client/src/lib/auth/errors.ts

Imported by:
- None


### client/src/data/xlaData.ts
Imports:
- client/src/types/xla.ts

Imported by:
- client/src/components/XLADetailView.tsx
- client/src/components/XLAConfigPanel.tsx
- client/src/components/Dashboard.tsx


### client/src/data/ReleaseNotesData.ts
Imports:
- None

Imported by:
- None


### client/src/contexts/TickerContext.tsx
Imports:
- client/src/lib/tickerUtils.ts

Imported by:
- client/src/App.tsx
- client/src/components/SettingsPage.tsx


### client/src/contexts/DataContext.tsx
Imports:
- client/src/auth
- client/src/lib/debug.ts

Imported by:
- client/src/App.tsx


### client/src/contexts/AbilityContext.tsx
Imports:
- client/src/lib/ability.ts
- client/src/lib/abilityUtils.ts
- client/src/types/auth.ts

Imported by:
- client/src/App.tsx


### client/src/constants/text.ts
Imports:
- None

Imported by:
- client/src/lib/constants.ts


### client/src/constants/text.js
Imports:
- None

Imported by:
- client/src/components/configuration/XLAConfigurationPanel.tsx
- client/src/components/api/ApiConfigWizard.tsx


### client/src/components/XLIManager.tsx
Imports:
- client/src/lib/debug.ts

Imported by:
- None


### client/src/components/XLALogTable.tsx
Imports:
- None

Imported by:
- None


### client/src/components/XLADetailView.tsx
Imports:
- client/src/types/xla.ts
- client/src/lib/utils.ts
- client/src/lib/db.ts
- client/src/lib/logger.ts
- client/src/data/xlaData.ts

Imported by:
- client/src/App.tsx


### client/src/components/XLAConfigPanel.tsx
Imports:
- client/src/lib/utils.ts
- client/src/types/xla.ts
- client/src/data/xlaData.ts
- client/src/lib/db.ts
- client/src/lib/logger.ts

Imported by:
- client/src/components/SettingsPage.tsx


### client/src/components/XLAChart.tsx
Imports:
- client/src/components/common/DataSourceInfo.tsx
- client/src/lib/logger.ts

Imported by:
- client/src/components/Dashboard.tsx


### client/src/components/UserManagement.tsx
Imports:
- client/src/lib/utils.ts
- client/src/lib/db.ts
- client/src/lib/logger.ts

Imported by:
- client/src/components/GlobalAdminPage.tsx


### client/src/components/TenantManagement.tsx
Imports:
- client/src/lib/db.ts
- client/src/lib/utils.ts
- client/src/lib/logger.ts
- client/src/lib/services/SettingsService.ts
- client/src/types/settings.ts
- client/src/components/ui/button.tsx
- client/src/components/ui/input.tsx
- client/src/components/ui/card.tsx
- client/src/auth/hooks/useAuth.ts

Imported by:
- None


### client/src/components/TenantAdminPage.tsx
Imports:
- client/src/lib/logger.ts
- client/src/components/RoleManagement.tsx
- client/src/lib/db.ts

Imported by:
- client/src/App.tsx
- client/src/components/AdminRoutes.tsx


### client/src/components/Sidebar.tsx
Imports:
- client/src/auth
- client/src/lib/utils.ts
- client/src/lib/sidebarModules.ts
- client/src/lib/debug.ts

Imported by:
- client/src/App.tsx


### client/src/components/SettingsPage.tsx
Imports:
- client/src/auth
- client/src/contexts/TickerContext.tsx
- client/src/components/settings/DataSourcesSection.tsx
- client/src/lib/logger.ts
- client/src/lib/debug.ts
- client/src/lib/settings.ts
- client/src/components/shared/CollapsibleSection.tsx
- client/src/lib/utils.ts
- client/src/components/XLAConfigPanel.tsx

Imported by:
- client/src/App.tsx
- client/src/components/Settings.tsx
- client/src/components/Profile.tsx


### client/src/components/Settings.tsx
Imports:
- client/src/components/SettingsPage.tsx

Imported by:
- None


### client/src/components/ScoreCard.tsx
Imports:
- client/src/lib/utils.ts
- client/src/components/common/DataSourceInfo.tsx

Imported by:
- client/src/components/Dashboard.tsx


### client/src/components/RoleManagement.tsx
Imports:
- None

Imported by:
- client/src/components/TenantAdminPage.tsx
- client/src/components/GlobalAdminPage.tsx


### client/src/components/RoleBasedAccess.tsx
Imports:
- client/src/auth
- client/src/auth/types

Imported by:
- None


### client/src/components/ReleaseNotesPage.tsx
Imports:
- client/src/lib/version.ts
- client/src/services/SettingsService.ts
- client/src/lib/logger.ts
- client/src/lib/releaseNotes.ts

Imported by:
- client/src/App.tsx


### client/src/components/Profile.tsx
Imports:
- client/src/components/SettingsPage.tsx

Imported by:
- client/src/App.tsx


### client/src/components/OverallScoreCard.tsx
Imports:
- client/src/lib/utils.ts
- client/src/components/common/DataSourceInfo.tsx

Imported by:
- client/src/components/Dashboard.tsx


### client/src/components/LoginPage.tsx
Imports:
- client/src/auth
- client/src/lib/version.ts
- client/src/lib/logger.ts
- client/src/components/AuthDebugger.tsx

Imported by:
- None


### client/src/components/LoadingSpinner.tsx
Imports:
- None

Imported by:
- None


### client/src/components/GlobalSettings.tsx
Imports:
- client/src/components/ui/use-toast.ts
- client/src/services/GlobalSettingsService.ts
- client/src/lib/debug.ts

Imported by:
- client/src/components/GlobalAdminPage.tsx


### client/src/components/GlobalAdminPage.tsx
Imports:
- client/src/lib/db.ts
- client/src/components/RoleManagement.tsx
- client/src/components/UserManagement.tsx
- client/src/components/GlobalSettings.tsx
- client/src/components/shared/CollapsibleSection.tsx
- client/src/lib/FallbackData.ts

Imported by:
- client/src/App.tsx


### client/src/components/ErrorBoundary.tsx
Imports:
- client/src/lib/debug.ts

Imported by:
- client/src/App.tsx


### client/src/components/DatabaseTest.tsx
Imports:
- client/src/lib/db.ts

Imported by:
- None


### client/src/components/Dashboard.tsx
Imports:
- client/src/components/ScoreCard.tsx
- client/src/components/XLAChart.tsx
- client/src/components/OverallScoreCard.tsx
- client/src/components/common/DataSourceInfo.tsx
- client/src/lib/db.ts
- client/src/lib/logger.ts
- client/src/types/xla.ts
- client/src/data/xlaData.ts
- client/src/lib/services/SettingsService.ts

Imported by:
- client/src/App.tsx
- client/src/routes/index.tsx


### client/src/components/AuthProviderSettings.tsx
Imports:
- None

Imported by:
- None


### client/src/components/AuthDebugger.tsx
Imports:
- client/src/auth

Imported by:
- client/src/components/LoginPage.tsx


### client/src/components/AssetErrorFallback.tsx
Imports:
- None

Imported by:
- None


### client/src/components/ApiClientManager.tsx
Imports:
- client/src/lib/debug.ts

Imported by:
- None


### client/src/components/AlertTicker.tsx
Imports:
- client/src/lib/utils.ts

Imported by:
- client/src/App.tsx


### client/src/components/AdminSettingsPage.tsx
Imports:
- None

Imported by:
- client/src/App.tsx
- client/src/components/AdminRoutes.tsx


### client/src/components/AdminRoutes.tsx
Imports:
- client/src/components/TenantAdminPage.tsx
- client/src/components/AdminSettingsPage.tsx

Imported by:
- client/src/App.tsx


### client/src/components/ui/use-toast.ts
Imports:
- None

Imported by:
- client/src/pages/ServiceMonitoringPage.tsx
- client/src/components/GlobalSettings.tsx


### client/src/components/ui/tooltip.tsx
Imports:
- client/src/lib/utils.ts

Imported by:
- None


### client/src/components/ui/tabs.tsx
Imports:
- client/src/lib/utils.ts

Imported by:
- client/src/pages/ServiceMonitoringPage.tsx
- client/src/pages/HelpPage.tsx


### client/src/components/ui/table.tsx
Imports:
- client/src/lib/utils.ts

Imported by:
- client/src/pages/ServiceMonitoringPage.tsx


### client/src/components/ui/label.tsx
Imports:
- None

Imported by:
- None


### client/src/components/ui/input.tsx
Imports:
- client/src/lib/utils.ts

Imported by:
- client/src/pages/ServiceMonitoringPage.tsx
- client/src/pages/HelpPage.tsx
- client/src/components/TenantManagement.tsx


### client/src/components/ui/index.ts
Imports:
- None

Imported by:
- None


### client/src/components/ui/card.tsx
Imports:
- client/src/lib/utils.ts

Imported by:
- client/src/pages/ServiceMonitoringPage.tsx
- client/src/pages/HelpPage.tsx
- client/src/components/TenantManagement.tsx


### client/src/components/ui/button.tsx
Imports:
- client/src/lib/utils.ts

Imported by:
- client/src/pages/ServiceMonitoringPage.tsx
- client/src/pages/HelpPage.tsx
- client/src/components/TenantManagement.tsx
- client/src/components/common/DateRangePicker.tsx
- client/src/auth/components/Login.tsx


### client/src/components/ui/badge.tsx
Imports:
- client/src/lib/utils.ts

Imported by:
- client/src/pages/ServiceMonitoringPage.tsx


### client/src/components/shared/Tabs.tsx
Imports:
- client/src/lib/utils.ts

Imported by:
- None


### client/src/components/shared/CollapsibleSection.tsx
Imports:
- None

Imported by:
- client/src/components/SettingsPage.tsx
- client/src/components/GlobalAdminPage.tsx
- client/src/components/settings/DebugSettings.tsx


### client/src/components/settings/DebugSettings.tsx
Imports:
- client/src/lib/debug.ts
- client/src/lib/logger.ts
- client/src/lib/utils.ts
- client/src/components/shared/CollapsibleSection.tsx

Imported by:
- None


### client/src/components/settings/DataSourcesSection.tsx
Imports:
- client/src/components/settings/DataSourceConfig.tsx
- client/src/lib/settings.ts
- client/src/auth
- client/src/lib/utils.ts
- client/src/lib/services/SettingsService.ts
- client/src/types/settings.ts

Imported by:
- client/src/components/SettingsPage.tsx


### client/src/components/settings/DataSourceConfig.tsx
Imports:
- client/src/lib/utils.ts
- client/src/lib/settings.ts

Imported by:
- client/src/components/settings/DataSourcesSection.tsx


### client/src/components/modules/IntelliSpaces.tsx
Imports:
- None

Imported by:
- client/src/App.tsx


### client/src/components/modules/IntelliNetwork.tsx
Imports:
- client/src/components/common/MetricCard.tsx
- client/src/components/common/CollapsibleCard.tsx
- client/src/components/common/DataSourceInfo.tsx

Imported by:
- client/src/App.tsx


### client/src/components/modules/IntelliHealth.tsx
Imports:
- client/src/components/common/MetricCard.tsx
- client/src/components/common/ProgressBar.tsx
- client/src/components/common/CollapsibleCard.tsx
- client/src/components/common/DataSourceInfo.tsx

Imported by:
- client/src/App.tsx


### client/src/components/modules/IntelliEX.tsx
Imports:
- None

Imported by:
- client/src/App.tsx


### client/src/components/modules/IntelliCX.tsx
Imports:
- client/src/components/common/CollapsibleCard.tsx
- client/src/components/common/DataSourceInfo.tsx

Imported by:
- client/src/App.tsx


### client/src/components/modules/IntelliAsset.tsx
Imports:
- client/src/components/common/MetricCard.tsx
- client/src/components/common/ProgressBar.tsx
- client/src/components/common/CollapsibleCard.tsx
- client/src/components/common/DataSourceInfo.tsx

Imported by:
- client/src/App.tsx


### client/src/components/configuration/XLAConfigurationPanel.tsx
Imports:
- client/src/types/xla.ts
- client/src/lib/validation/xlaValidation.ts
- client/src/auth
- client/src/lib/debug.ts
- client/src/constants/text.js
- client/src/components/api/ApiConfigWizard.css
- client/src/components/configuration/XLAConfigurationPanel.css
- client/src/lib/services/ApiXliMappingService.ts

Imported by:
- client/src/routes/XLAConfiguration.tsx


### client/src/components/configuration/XLAConfigurationPanel.css
Imports:
- None

Imported by:
- client/src/components/configuration/XLAConfigurationPanel.tsx


### client/src/components/common/ProgressBar.tsx
Imports:
- None

Imported by:
- client/src/components/modules/IntelliHealth.tsx
- client/src/components/modules/IntelliAsset.tsx


### client/src/components/common/MetricCard.tsx
Imports:
- client/src/lib/utils.ts
- client/src/components/common/DataSourceInfo.tsx

Imported by:
- client/src/components/modules/IntelliNetwork.tsx
- client/src/components/modules/IntelliHealth.tsx
- client/src/components/modules/IntelliAsset.tsx


### client/src/components/common/DateRangePicker.tsx
Imports:
- client/src/components/ui/button.tsx
- client/src/lib/utils.ts

Imported by:
- None


### client/src/components/common/DatabaseErrorDisplay.tsx
Imports:
- None

Imported by:
- None


### client/src/components/common/DataSourceInfo.tsx
Imports:
- client/src/lib/utils.ts

Imported by:
- client/src/components/XLAChart.tsx
- client/src/components/ScoreCard.tsx
- client/src/components/OverallScoreCard.tsx
- client/src/components/Dashboard.tsx
- client/src/components/modules/IntelliNetwork.tsx
- client/src/components/modules/IntelliHealth.tsx
- client/src/components/modules/IntelliCX.tsx
- client/src/components/modules/IntelliAsset.tsx
- client/src/components/common/MetricCard.tsx


### client/src/components/common/CollapsibleCard.tsx
Imports:
- client/src/lib/utils.ts

Imported by:
- client/src/components/modules/IntelliNetwork.tsx
- client/src/components/modules/IntelliHealth.tsx
- client/src/components/modules/IntelliCX.tsx
- client/src/components/modules/IntelliAsset.tsx


### client/src/components/auth/AuthCallback.tsx
Imports:
- None

Imported by:
- None


### client/src/components/api/ApiConfigWizard.tsx
Imports:
- client/src/auth
- client/src/lib/debug.ts
- client/src/constants/text.js
- client/src/components/api/ApiConfigWizard.css

Imported by:
- client/src/pages/api/ApiConfigPage.tsx


### client/src/components/api/ApiConfigWizard.css
Imports:
- None

Imported by:
- client/src/components/configuration/XLAConfigurationPanel.tsx
- client/src/components/api/ApiConfigWizard.tsx


### client/src/auth/types.ts
Imports:
- None

Imported by:
- None


### client/src/auth/index.ts
Imports:
- None

Imported by:
- client/src/auth/integration/index.tsx


### client/src/auth/utils/storage.ts
Imports:
- client/src/lib/debug.ts
- client/src/auth/types

Imported by:
- client/src/auth/providers/SamlProvider.ts
- client/src/auth/providers/OAuthProvider.ts
- client/src/auth/contexts/AuthContext.tsx


### client/src/auth/utils/state.ts
Imports:
- client/src/lib/debug.ts
- client/src/auth/types

Imported by:
- None


### client/src/auth/utils/index.ts
Imports:
- None

Imported by:
- None


### client/src/auth/utils/auth.ts
Imports:
- client/src/lib/debug.ts
- client/src/auth/types

Imported by:
- client/src/auth/providers/SamlProvider.ts
- client/src/auth/providers/OAuthProvider.ts
- client/src/auth/contexts/AuthContext.tsx


### client/src/auth/types/index.ts
Imports:
- None

Imported by:
- None


### client/src/auth/services/authApi.ts
Imports:
- client/src/lib/debug.ts
- client/src/auth/types
- client/src/auth/hooks/useAuth.ts

Imported by:
- None


### client/src/auth/routes/AuthRoutes.tsx
Imports:
- client/src/auth/components
- client/src/lib/debug.ts
- client/src/auth/types
- client/src/pages/auth/LoginTroubleshooting.tsx

Imported by:
- None


### client/src/auth/providers/index.ts
Imports:
- client/src/lib/debug.ts
- client/src/auth/types
- client/src/auth/providers/BaseAuthProvider.ts
- client/src/auth/providers/EntraIdProvider.ts
- client/src/auth/providers/OAuthProvider.ts
- client/src/auth/providers/SamlProvider.ts

Imported by:
- None


### client/src/auth/providers/SamlProvider.ts
Imports:
- client/src/lib/debug.ts
- client/src/auth/types
- client/src/auth/providers/BaseAuthProvider.ts
- client/src/auth/utils/auth.ts
- client/src/auth/utils/storage.ts
- client/src/auth/providers/AuthProviderStrategy.ts

Imported by:
- client/src/auth/providers/index.ts


### client/src/auth/providers/OAuthProvider.ts
Imports:
- client/src/lib/debug.ts
- client/src/auth/types
- client/src/auth/providers/BaseAuthProvider.ts
- client/src/auth/providers/AuthProviderStrategy.ts
- client/src/auth/utils/auth.ts
- client/src/auth/utils/storage.ts

Imported by:
- client/src/auth/providers/index.ts


### client/src/auth/providers/MsalProvider.tsx
Imports:
- client/src/auth/config/msalConfig.ts

Imported by:
- None


### client/src/auth/providers/MsalProvider.ts
Imports:
- client/src/lib/debug.ts

Imported by:
- client/src/auth/providers/EntraIdProvider.ts


### client/src/auth/providers/EntraIdProvider.ts
Imports:
- client/src/lib/debug.ts
- client/src/auth/types
- client/src/auth/providers/BaseAuthProvider.ts
- client/src/auth/providers/AuthProviderStrategy.ts
- client/src/auth/providers/MsalProvider.ts

Imported by:
- client/src/auth/providers/index.ts


### client/src/auth/providers/BaseAuthProvider.ts
Imports:
- client/src/lib/debug.ts
- client/src/auth/types
- client/src/auth/providers/AuthProviderStrategy.ts

Imported by:
- client/src/auth/providers/index.ts
- client/src/auth/providers/SamlProvider.ts
- client/src/auth/providers/OAuthProvider.ts
- client/src/auth/providers/EntraIdProvider.ts


### client/src/auth/providers/AuthProviderStrategy.ts
Imports:
- client/src/auth/types

Imported by:
- client/src/auth/providers/SamlProvider.ts
- client/src/auth/providers/OAuthProvider.ts
- client/src/auth/providers/EntraIdProvider.ts
- client/src/auth/providers/BaseAuthProvider.ts


### client/src/auth/integration/index.tsx
Imports:
- client/src/auth/index.ts
- client/src/auth/types
- client/src/lib/debug.ts

Imported by:
- None


### client/src/auth/hooks/useAuth.tsx
Imports:
- client/src/lib/debug.ts
- client/src/auth/contexts/AuthContext.tsx
- client/src/auth/types

Imported by:
- None


### client/src/auth/hooks/useAuth.ts
Imports:
- client/src/auth/contexts/AuthContext.tsx
- client/src/auth/types
- client/src/lib/debug.ts

Imported by:
- client/src/pages/api/ApiConfigPage.tsx
- client/src/components/TenantManagement.tsx
- client/src/auth/services/authApi.ts
- client/src/auth/hooks/index.ts
- client/src/auth/components/ProtectedRoute.tsx
- client/src/auth/components/Login.tsx
- client/src/auth/components/AdminSettings.tsx


### client/src/auth/hooks/index.ts
Imports:
- client/src/auth/types
- client/src/auth/hooks/useAuth.ts

Imported by:
- None


### client/src/auth/contexts/AuthContext.tsx
Imports:
- client/src/lib/debug.ts
- client/src/auth/types
- client/src/auth/providers
- client/src/auth/utils/storage.ts
- client/src/auth/utils/auth.ts

Imported by:
- client/src/auth/hooks/useAuth.tsx
- client/src/auth/hooks/useAuth.ts
- client/src/auth/components/Login.tsx
- client/src/auth/components/AuthCallback.tsx


### client/src/auth/config/msalConfig.ts
Imports:
- client/src/lib/debug.ts

Imported by:
- client/src/auth/providers/MsalProvider.tsx


### client/src/auth/components/index.ts
Imports:
- None

Imported by:
- None


### client/src/auth/components/RoleBasedAccess.tsx
Imports:
- client/src/auth/hooks
- client/src/auth/types

Imported by:
- None


### client/src/auth/components/ProtectedRoute.tsx
Imports:
- client/src/auth/hooks/useAuth.ts
- client/src/auth/types

Imported by:
- client/src/App.tsx


### client/src/auth/components/Login.tsx
Imports:
- client/src/auth/hooks/useAuth.ts
- client/src/auth/types
- client/src/lib/logger.ts
- client/src/lib/version.ts
- client/src/auth/contexts/AuthContext.tsx
- client/src/components/ui/button.tsx
- client/src/lib/debug.ts
- client/src/auth/components/Login.css

Imported by:
- client/src/App.tsx


### client/src/auth/components/Login.css
Imports:
- None

Imported by:
- client/src/auth/components/Login.tsx


### client/src/auth/components/AuthCallback.tsx
Imports:
- client/src/auth/contexts/AuthContext.tsx
- client/src/lib/debug.ts
- client/src/auth/components/AuthCallback.css

Imported by:
- client/src/App.tsx


### client/src/auth/components/AuthCallback.css
Imports:
- None

Imported by:
- client/src/auth/components/AuthCallback.tsx


### client/src/auth/components/AdminSettings.tsx
Imports:
- client/src/auth/types
- client/src/auth/hooks/useAuth.ts
- client/src/lib/debug.ts
- client/src/auth/components/AdminSettings.css

Imported by:
- None


### client/src/auth/components/AdminSettings.css
Imports:
- None

Imported by:
- client/src/auth/components/AdminSettings.tsx


### client/src/auth/components/AccessDenied.tsx
Imports:
- client/src/auth/types

Imported by:
- client/src/App.tsx


Generated on: 2025-05-05T22:52:34.148Z
