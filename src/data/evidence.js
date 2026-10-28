// Synthetic evidence dataset for the prototype.
// These are mock forensic artifacts used to demonstrate
// evidence registration and case reconstruction.

export const evidence = [
  {
    id: "EV-001",
    fileName: "system_log.txt",
    type: "System Log",
    source: "Laptop-07",
    collectedAt: "2026-09-21T02:50:00",
    integrityStatus: "verified",
    hash: "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"
  },

  {
    id: "EV-002",
    fileName: "chat_export.txt",
    type: "Chat Export",
    source: "Messaging Application",
    collectedAt: "2026-09-21T02:51:00",
    integrityStatus: "verified",
    hash: "7b52009b64fd0a2d2e6d7f5e4e7c8a1b"
  },

  {
    id: "EV-003",
    fileName: "usb_log.txt",
    type: "USB Activity Log",
    source: "Laptop-07",
    collectedAt: "2026-09-21T02:52:00",
    integrityStatus: "verified",
    hash: "4f8c2e91a7d5b3c6e8f1029384756abc"
  },

  {
    id: "EV-004",
    fileName: "network_log.csv",
    type: "Network Log",
    source: "Network Monitor",
    collectedAt: "2026-09-21T02:53:00",
    integrityStatus: "verified",
    hash: "9d72c1f4e8a6b3c5029174abcdef1234"
  }
];