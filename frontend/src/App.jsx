import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import Overview from "./pages/Overview";
import ClientLeads from "./pages/ClientLeads";
import PhdOpportunities from "./pages/PhdOpportunities";
import JobApplications from "./pages/JobApplications";
import RemoteJobs from "./pages/RemoteJobs";
import OpportunityDetail from "./pages/OpportunityDetail";
import Sources from "./pages/Sources";
import ProfileKnowledge from "./pages/ProfileKnowledge";
import ReviewQueue from "./pages/ReviewQueue";
import LogsHealth from "./pages/LogsHealth";
import Settings from "./pages/Settings";
import Login from "./pages/Login";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route index element={<Overview />} />
            <Route path="client-leads" element={<ClientLeads />} />
            <Route path="phd" element={<PhdOpportunities />} />
            <Route path="jobs" element={<JobApplications />} />
            <Route path="remote" element={<RemoteJobs />} />
            <Route path="opportunity/:id" element={<OpportunityDetail />} />
            <Route path="sources" element={<Sources />} />
            <Route path="profile" element={<ProfileKnowledge />} />
            <Route path="review" element={<ReviewQueue />} />
            <Route path="logs" element={<LogsHealth />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
