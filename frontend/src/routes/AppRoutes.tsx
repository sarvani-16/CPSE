import React from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ProtectedRoute, RoleRoute } from './RouteGuards';
import { MainLayout } from '../layouts/MainLayout';
import { LoadingState } from '../components/common/FeedbackStates';

// Auth Pages
import { LoginPage } from '../components/auth/LoginPage';
import { RegisterPage } from '../pages/auth/RegisterPage';
import { ForgotPasswordPage } from '../pages/auth/ForgotPasswordPage';
import { ForbiddenPage } from '../components/common/ForbiddenPage';

// Dashboards
import { AdminDashboard } from '../components/dashboard/AdminDashboard';
import { ReviewerDashboard } from '../components/dashboard/ReviewerDashboard';
import { OfficerDashboard } from '../components/dashboard/OfficerDashboard';

// Enterprise Views
import { MaterialCatalogView } from '../components/materials/MaterialCatalogView';
import { UploadView } from '../components/upload/UploadView';
import { MatchingView } from '../components/harmonization/MatchingView';
import { DuplicatesView } from '../components/harmonization/DuplicatesView';
import { ReviewView } from '../components/review/ReviewView';
import { CanonicalView } from '../components/canonical/CanonicalView';
import { TaxonomyView } from '../components/taxonomy/TaxonomyView';
import { AnalyticsView } from '../components/analytics/AnalyticsView';
import { AuditView } from '../components/admin/AuditView';
import { ReportsView } from '../components/reports/ReportsView';
import { UserManagementView } from '../components/admin/UserManagementView';
import { DataManagementView } from '../components/admin/DataManagementView';
import { ModelStatusView } from '../components/admin/ModelStatusView';
import { SettingsView } from '../components/admin/SettingsView';

const RootRedirect: React.FC = () => {
  const { isAuthenticated, role, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingState message="Verifying enterprise credentials..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (role === 'ADMIN') {
    return <Navigate to="/admin/dashboard" replace />;
  }
  if (role === 'REVIEWER') {
    return <Navigate to="/reviewer/dashboard" replace />;
  }

  return <Navigate to="/user/dashboard" replace />;
};

export const AppRoutes: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Routes>
      {/* 1. Public Authentication Routes (Real separate pages) */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/403" element={<ForbiddenPage />} />

      {/* 2. Root Role-Based Redirection */}
      <Route path="/" element={<RootRedirect />} />

      {/* 3. Protected Enterprise Routes with Strict RBAC */}
      <Route element={<ProtectedRoute />}>
        <Route element={<MainLayout />}>

          {/* ADMIN SECTION (Strict ADMIN role enforcement) */}
          <Route element={<RoleRoute allowedRoles={['ADMIN']} />}>
            <Route path="/admin/dashboard" element={<AdminDashboard />} />
            <Route path="/admin/users" element={<UserManagementView />} />
            <Route path="/admin/materials" element={<MaterialCatalogView />} />
            <Route path="/admin/cpse-sources" element={<DuplicatesView />} />
            <Route path="/admin/data-management" element={<DataManagementView />} />
            <Route path="/admin/reviews" element={<ReviewView />} />
            <Route path="/admin/canonical-materials" element={<CanonicalView />} />
            <Route path="/admin/taxonomy" element={<TaxonomyView />} />
            <Route path="/admin/model-status" element={<ModelStatusView />} />
            <Route path="/admin/analytics" element={<AnalyticsView />} />
            <Route path="/admin/jobs" element={<DataManagementView />} />
            <Route path="/admin/audit-logs" element={<AuditView />} />
            <Route path="/admin/reports" element={<ReportsView />} />
            <Route path="/admin/settings" element={<SettingsView />} />
          </Route>

          {/* REVIEWER SECTION (Strict REVIEWER & ADMIN role enforcement) */}
          <Route element={<RoleRoute allowedRoles={['REVIEWER', 'ADMIN']} />}>
            <Route
              path="/reviewer/dashboard"
              element={<ReviewerDashboard onNavigateToReview={() => navigate('/reviewer/reviews')} />}
            />
            <Route path="/reviewer/materials" element={<MaterialCatalogView />} />
            <Route path="/reviewer/matching" element={<MatchingView />} />
            <Route path="/reviewer/reviews" element={<ReviewView />} />
            <Route path="/reviewer/duplicates" element={<DuplicatesView />} />
            <Route path="/reviewer/harmonized" element={<CanonicalView />} />
            <Route path="/reviewer/canonical-materials" element={<CanonicalView />} />
            <Route path="/reviewer/analytics" element={<AnalyticsView />} />
            <Route path="/reviewer/audit" element={<AuditView />} />
            <Route path="/reviewer/reports" element={<ReportsView />} />
          </Route>

          {/* OFFICER / USER SECTION (Strict OFFICER & ADMIN role enforcement) */}
          <Route element={<RoleRoute allowedRoles={['OFFICER', 'ADMIN']} />}>
            <Route
              path="/user/dashboard"
              element={<OfficerDashboard onNavigateToUpload={() => navigate('/user/upload')} />}
            />
            <Route path="/user/materials" element={<MaterialCatalogView />} />
            <Route path="/user/upload" element={<UploadView />} />
            <Route path="/user/matching" element={<MatchingView />} />
            <Route path="/user/harmonization" element={<MatchingView />} />
            <Route path="/user/duplicates" element={<DuplicatesView />} />
            <Route path="/user/review-queue" element={<ReviewView />} />
            <Route path="/user/canonical-materials" element={<CanonicalView />} />
            <Route path="/user/taxonomy" element={<TaxonomyView />} />
            <Route path="/user/analytics" element={<AnalyticsView />} />
            <Route path="/user/reports" element={<ReportsView />} />
          </Route>

        </Route>
      </Route>

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
