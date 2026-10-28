// Synthetic system-log observations.
//
// IMPORTANT:
// The observations are intentionally mixed together.
// The final incident timeline must be reconstructed
// by correlating multiple evidence sources.

export const systemLog = [

  // -----------------------------
  // RAHUL / LAPTOP-07
  // -----------------------------

  {
    source: "system_log",
    recordId: "SYS-001",
    timestamp: "2026-09-21T02:41:03",
    user: "Rahul",
    device: "Laptop-07",
    action: "LOGIN"
  },

  {
    source: "system_log",
    recordId: "SYS-002",
    timestamp: "2026-09-21T02:42:17",
    user: "Rahul",
    device: "Laptop-07",
    action: "FILE_ACCESS",
    file: "confidential_report.pdf"
  },

  {
    source: "system_log",
    recordId: "SYS-003",
    timestamp: "2026-09-21T02:45:31",
    user: "Rahul",
    device: "Laptop-07",
    action: "NETWORK_CONNECTION",
    ip: "85.21.44.9"
  },


  // -----------------------------
  // AMIT / LAPTOP-03
  // -----------------------------

  {
    source: "system_log",
    recordId: "SYS-004",
    timestamp: "2026-09-21T02:41:20",
    user: "Amit",
    device: "Laptop-03",
    action: "LOGIN"
  },

  {
    source: "system_log",
    recordId: "SYS-005",
    timestamp: "2026-09-21T02:42:41",
    user: "Amit",
    device: "Laptop-03",
    action: "FILE_ACCESS",
    file: "financial_summary.xlsx"
  },

  {
    source: "system_log",
    recordId: "SYS-006",
    timestamp: "2026-09-21T02:45:40",
    user: "Amit",
    device: "Laptop-03",
    action: "NETWORK_CONNECTION",
    ip: "172.16.4.22"
  },


  // -----------------------------
  // PRIYA / LAPTOP-11
  // -----------------------------

  {
    source: "system_log",
    recordId: "SYS-007",
    timestamp: "2026-09-21T02:42:05",
    user: "Priya",
    device: "Laptop-11",
    action: "LOGIN"
  },

  {
    source: "system_log",
    recordId: "SYS-008",
    timestamp: "2026-09-21T02:43:14",
    user: "Priya",
    device: "Laptop-11",
    action: "FILE_ACCESS",
    file: "meeting_notes.docx"
  },


  // -----------------------------
  // UNRELATED SYSTEM ACTIVITY
  // -----------------------------

  {
    source: "system_log",
    recordId: "SYS-009",
    timestamp: "2026-09-21T02:44:10",
    user: "Rahul",
    device: "Laptop-07",
    action: "FILE_ACCESS",
    file: "notes.txt"
  },

  {
    source: "system_log",
    recordId: "SYS-010",
    timestamp: "2026-09-21T02:44:12",
    user: "Amit",
    device: "Laptop-03",
    action: "FILE_ACCESS",
    file: "presentation.pptx"
  }
];