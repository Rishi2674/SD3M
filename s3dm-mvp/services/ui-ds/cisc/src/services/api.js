// This is a conceptual API service. In a real application, you'd replace
// these with actual fetch/axios calls to your backend endpoints.

const API_BASE_URL = 'http://localhost:8000/submit/tickets'; // Replace with your actual backend URL

export const reportNewIssue = async (issueData) => {
  console.log('Reporting issue to backend:', issueData);
  // Example dummy response
  return new Promise(resolve => setTimeout(() => resolve({
    ticketId: `TKT-${Math.floor(Math.random() * 1000000)}`,
    status: 'Received',
    message: 'Issue successfully reported.'
  }), 1000));
  
  const response = await fetch(`${API_BASE_URL}/issues`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(issueData),
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
  
};

export const getMyTickets = async () => {
  console.log('Fetching my tickets...');
  // Example dummy response
  return new Promise(resolve => setTimeout(() => resolve([
    {
      id: 'TKT-123456',
      user_message: "My smart light keeps flickering and won't turn off.",
      device_type: "smart_light",
      issue_type: "functionality",
      location: "living_room",
      brand: "Philips",
      status: "In Progress",
      lastUpdate: new Date().toISOString(),
      fellowshipAssembledAt: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
      reportedAt: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
    },
    {
      id: 'TKT-789012',
      user_message: "The Nest thermostat in my hall is showing error E73 after a power cut.",
      device_type: "thermostat",
      issue_type: "connectivity",
      location: "hallway",
      brand: "Nest",
      status: "Diagnosis In Progress",
      lastUpdate: new Date().toISOString(),
      reportedAt: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
      fellowshipAssembledAt: new Date(Date.now() - 80000000).toISOString(),
      diagnosisStartedAt: new Date(Date.now() - 70000000).toISOString(),
    },
    {
      id: 'TKT-345678',
      user_message: "My Ring doorbell camera stopped recording motion events last week.",
      device_type: "camera",
      issue_type: "security",
      location: "outdoor",
      brand: "Ring",
      status: "Resolved",
      lastUpdate: new Date().toISOString(),
      reportedAt: new Date(Date.now() - (7 * 86400000)).toISOString(), // 7 days ago
      fellowshipAssembledAt: new Date(Date.now() - (6 * 86400000)).toISOString(),
      diagnosisStartedAt: new Date(Date.now() - (5 * 86400000)).toISOString(),
      partsOrderedAt: new Date(Date.now() - (3 * 86400000)).toISOString(),
      repairScheduledAt: new Date(Date.now() - (2 * 86400000)).toISOString(),
      resolvedAt: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
    }
  ]), 1500));
  /*
  const response = await fetch(`${API_BASE_URL}/tickets`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
  */
};

export const getTicketDetails = async (ticketId) => {
  console.log(`Fetching details for ticket: ${ticketId}`);
  // Example dummy response - you'd replace with actual backend data
  const dummyTickets = await getMyTickets(); // Re-use dummy tickets
  const ticket = dummyTickets.find(t => t.id === ticketId);
  return new Promise((resolve, reject) => setTimeout(() => {
    if (ticket) {
      resolve({
        ...ticket,
        severity: ticket.id === 'TKT-123456' ? 'high' : 'medium',
        last_working_time: ticket.id === 'TKT-123456' ? 'just_now' : (ticket.id === 'TKT-789012' ? 'hours_ago' : 'weeks_ago'),
        user_action_taken: ticket.id === 'TKT-123456' ? 'none' : 'power_cycle, app_reinstall',
        error_code: ticket.id === 'TKT-789012' ? 'E73' : null,
        firmware_version: ticket.id === 'TKT-789012' ? '3.5.1' : null,
        involvedAgents: [
          { companyName: 'SmartHome Corp.', role: 'Manufacturer', country: 'Germany' },
          { companyName: 'CompFix Solutions', role: 'Repair Franchise', country: 'India' },
          ...(ticket.id === 'TKT-789012' ? [{ companyName: 'PowerConnect Logistics', role: 'Logistics Partner', country: 'Brazil' }] : []),
          ...(ticket.id === 'TKT-345678' ? [{ companyName: 'SecureLens Inc.', role: 'Component Vendor', country: 'Japan' }] : []),
        ]
      });
    } else {
      reject(new Error('Ticket not found'));
    }
  }, 800));
  /*
  const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
  */
};

export const getDataAgreements = async (ticketId) => {
  console.log(`Fetching data agreements for ticket: ${ticketId}`);
  // Example dummy response
  return new Promise(resolve => setTimeout(() => resolve([
    {
      partnerName: "SmartHome Corp. (Manufacturer)",
      partnerCountry: "Germany",
      purpose: "Diagnose device malfunction",
      dataCategories: ["Device ID", "Error Logs", "Firmware Version"],
      complianceRules: ["GDPR"],
      duration: "Until issue resolution + 30 days",
      expiryDate: new Date(Date.now() + (30 * 24 * 60 * 60 * 1000)).toISOString(), // 30 days from now
      status: "Active",
      canRevoke: false
    },
    {
      partnerName: "CompFix Solutions (Repair Franchise)",
      partnerCountry: "India",
      purpose: "Schedule and perform repair",
      dataCategories: ["Customer Contact Info", "Device ID", "Location (approximate)", "Repair History"],
      complianceRules: ["PDPB", "GDPR (for EU customers)"],
      duration: "Until repair completion",
      expiryDate: new Date(Date.now() + (7 * 24 * 60 * 60 * 1000)).toISOString(), // 7 days from now
      status: "Active",
      canRevoke: true // Customer might be able to revoke contact sharing for future marketing
    },
    ...(ticketId === 'TKT-789012' ? [{
      partnerName: "PowerConnect Logistics (Logistics Partner)",
      partnerCountry: "Brazil",
      purpose: "Ship replacement parts",
      dataCategories: ["Customer Shipping Address", "Part Number"],
      complianceRules: ["LGPD"],
      duration: "Until delivery confirmation",
      expiryDate: new Date(Date.now() + (14 * 24 * 60 * 60 * 1000)).toISOString(), // 14 days from now
      status: "Active",
      canRevoke: false
    }] : []),
  ]), 1000));
  /*
  const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}/data-agreements`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
  */
};

export async function sendChatMessage(messageText) {
  const response = await fetch('/tickets/submit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_message: messageText,
      device_type: 'chatbot',
      issue_type: 'general',
      location: 'chat',
      brand: 'n/a',
      model: 'n/a',
    }),
  });

  if (!response.ok) {
    throw new Error(`Server error: ${response.statusText}`);
  }

  return await response.json();
}
