// Synthetic file-access observations.
//
// This source intentionally contains observations from
// multiple users and multiple incidents.

export const fileAccessLog = [

  // -----------------------------
  // RAHUL
  // -----------------------------

  {
    source: "file_access_log",
    recordId: "FILE-001",
    timestamp: "2026-09-21T02:42:19",
    user: "Rahul",
    device: "Laptop-07",
    action: "READ",
    file: "confidential_report.pdf"
  },

  {
    source: "file_access_log",
    recordId: "FILE-002",
    timestamp: "2026-09-21T02:44:02",
    user: "Rahul",
    device: "Laptop-07",
    action: "COPY",
    file: "confidential_report.pdf",
    destination: "USB-003"
  },

  {
    source: "file_access_log",
    recordId: "FILE-003",
    timestamp: "2026-09-21T02:46:12",
    user: "Rahul",
    device: "Laptop-07",
    action: "TRANSFER",
    file: "confidential_report.pdf",
    destination: "85.21.44.9"
  },


  // -----------------------------
  // AMIT
  // -----------------------------

  {
    source: "file_access_log",
    recordId: "FILE-004",
    timestamp: "2026-09-21T02:42:43",
    user: "Amit",
    device: "Laptop-03",
    action: "READ",
    file: "financial_summary.xlsx"
  },

  {
    source: "file_access_log",
    recordId: "FILE-005",
    timestamp: "2026-09-21T02:44:04",
    user: "Amit",
    device: "Laptop-03",
    action: "COPY",
    file: "financial_summary.xlsx",
    destination: "USB-005"
  },


  // -----------------------------
  // PRIYA
  // -----------------------------

  {
    source: "file_access_log",
    recordId: "FILE-006",
    timestamp: "2026-09-21T02:43:17",
    user: "Priya",
    device: "Laptop-11",
    action: "READ",
    file: "meeting_notes.docx"
  },


  // -----------------------------
  // DECOY / NORMAL ACTIVITY
  // -----------------------------

  {
    source: "file_access_log",
    recordId: "FILE-007",
    timestamp: "2026-09-21T02:44:11",
    user: "Rahul",
    device: "Laptop-07",
    action: "READ",
    file: "notes.txt"
  },

  {
    source: "file_access_log",
    recordId: "FILE-008",
    timestamp: "2026-09-21T02:44:14",
    user: "Amit",
    device: "Laptop-03",
    action: "READ",
    file: "presentation.pptx"
  },


  // -----------------------------
  // PARTIAL / INCOMPLETE RECORD
  // -----------------------------

  {
    source: "file_access_log",
    recordId: "FILE-009",
    timestamp: "2026-09-21T02:45:05",
    device: "Laptop-07",
    action: "READ",
    file: "browser_cache.db"
  }
];