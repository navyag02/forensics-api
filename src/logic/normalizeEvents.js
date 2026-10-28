/**
 * Converts raw observations from different evidence sources
 * into a common event structure.
 */

export function normalizeEvents(rawRecords) {
  if (!Array.isArray(rawRecords)) {
    throw new Error("Raw records must be provided as an array.");
  }

  return rawRecords
    .filter((record) => record.timestamp && record.action)
    .map((record) => ({
      recordId: record.recordId,
      source: record.source,

      timestamp: record.timestamp,

      user: record.user || null,
      device: record.device || null,
      file: record.file || null,
      usb: record.usb || null,
      ip: record.ip || null,

      action: record.action,

      destination: record.destination || null
    }));
}