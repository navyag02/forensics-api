// Synthetic network observations.
//
// Multiple devices and IP addresses are intentionally
// mixed together.

export const networkLog = [

  // -----------------------------
  // RAHUL
  // -----------------------------

  {
    source: "network_log",
    recordId: "NET-001",
    timestamp: "2026-09-21T02:45:32",
    device: "Laptop-07",
    ip: "85.21.44.9",
    action: "CONNECTION"
  },

  {
    source: "network_log",
    recordId: "NET-002",
    timestamp: "2026-09-21T02:46:13",
    device: "Laptop-07",
    ip: "85.21.44.9",
    action: "OUTBOUND_TRANSFER",
    file: "confidential_report.pdf"
  },


  // -----------------------------
  // AMIT
  // -----------------------------

  {
    source: "network_log",
    recordId: "NET-003",
    timestamp: "2026-09-21T02:45:41",
    device: "Laptop-03",
    ip: "172.16.4.22",
    action: "CONNECTION"
  },


  // -----------------------------
  // PRIYA / NORMAL ACTIVITY
  // -----------------------------

  {
    source: "network_log",
    recordId: "NET-004",
    timestamp: "2026-09-21T02:44:20",
    device: "Laptop-11",
    ip: "10.0.0.25",
    action: "CONNECTION"
  },


  // -----------------------------
  // DECOY NETWORK ACTIVITY
  // -----------------------------

  {
    source: "network_log",
    recordId: "NET-005",
    timestamp: "2026-09-21T02:45:33",
    device: "Laptop-07",
    ip: "10.0.0.15",
    action: "CONNECTION"
  },

  {
    source: "network_log",
    recordId: "NET-006",
    timestamp: "2026-09-21T02:46:15",
    device: "Laptop-03",
    ip: "172.16.4.22",
    action: "OUTBOUND_TRANSFER",
    file: "presentation.pptx"
  }
];