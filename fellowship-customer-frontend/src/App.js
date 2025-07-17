import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Header from './components/header';
import Footer from './components/footer';
import HomePage from './pages/HomePage';
import ReportIssuePage from './pages/ReportIssuePage';
import MyTicketsPage from './pages/MyTicketsPage';
import TicketDetailPage from './pages/TicketDetailPage';
import DataAgreementPage from './pages/DataAgreementPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main style={{ padding: '20px', minHeight: 'calc(100vh - 120px)' }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/report-issue" element={<ReportIssuePage />} />
            <Route path="/my-tickets" element={<MyTicketsPage />} />
            <Route path="/ticket/:ticketId" element={<TicketDetailPage />} />
            <Route path="/ticket/:ticketId/data-agreement" element={<DataAgreementPage />} />
            {/* Add more routes as needed */}
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;