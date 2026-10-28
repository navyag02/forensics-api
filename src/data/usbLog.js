// Synthetic USB observations.
//
// Multiple USB devices are intentionally present.
// Some activities are relevant to the reconstructed
// incidents while others are unrelated.

export const usbLog = [

  // -----------------------------
  // RAHUL
  // -----------------------------

  {
    source: "usb_log",
    recordId: "USB-001",
    timestamp: "2026-09-21T02:43:02",
    device: "Laptop-07",
    usb: "USB-003",
    action: "CONNECT"
  },

  {
    source: "usb_log",
    recordId: "USB-002",
    timestamp: "2026-09-21T02:44:03",
    device: "Laptop-07",
    usb: "USB-003",
    action: "FILE_WRITE",
    file: "confidential_report.pdf"
  },

  {
    source: "usb_log",
    recordId: "USB-003",
    timestamp: "2026-09-21T02:44:30",
    device: "Laptop-07",
    usb: "USB-003",
    action: "FILE_WRITE",
    file: "notes.txt"
  },


  // -----------------------------
  // AMIT
  // -----------------------------

  {
    source: "usb_log",
    recordId: "USB-004",
    timestamp: "2026-09-21T02:43:32",
    device: "Laptop-03",
    usb: "USB-005",
    action: "CONNECT"
  },

  {
    source: "usb_log",
    recordId: "USB-005",
    timestamp: "2026-09-21T02:44:06",
    device: "Laptop-03",
    usb: "USB-005",
    action: "FILE_WRITE",
    file: "financial_summary.xlsx"
  },


  // -----------------------------
  // PRIYA / UNRELATED
  // -----------------------------

  {
    source: "usb_log",
    recordId: "USB-006",
    timestamp: "2026-09-21T02:43:45",
    device: "Laptop-11",
    usb: "USB-009",
    action: "CONNECT"
  }
];