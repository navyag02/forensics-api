/**
 * Reconstructs activities from independently observed
 * and correlated forensic evidence.
 *
 * Multiple raw observations describing the same activity
 * are merged into one reconstructed activity.
 */

export function reconstructCase(events, correlations = []) {

  if (!Array.isArray(events)) {
    throw new Error("Events must be provided as an array.");
  }

  const eventMap = new Map(
    events.map((event) => [event.recordId, event])
  );

  const visited = new Set();
  const activities = [];

  // --------------------------------------------------
  // MERGE CORRELATED OBSERVATIONS
  // --------------------------------------------------

  for (const correlation of correlations) {

    const first = eventMap.get(correlation.from);
    const second = eventMap.get(correlation.to);

    if (!first || !second) {
      continue;
    }

    // Avoid processing the same observation twice.
    if (
      visited.has(first.recordId) ||
      visited.has(second.recordId)
    ) {
      continue;
    }

    const observations = [first, second].sort(
      (a, b) =>
        new Date(a.timestamp).getTime() -
        new Date(b.timestamp).getTime()
    );

    observations.forEach((event) => {
      visited.add(event.recordId);
    });

    activities.push(
      buildActivity(observations, correlation)
    );
  }

  // --------------------------------------------------
  // KEEP UNCORRELATED OBSERVATIONS
  // --------------------------------------------------

  for (const event of events) {

    if (visited.has(event.recordId)) {
      continue;
    }

    activities.push(
      buildActivity([event], null)
    );

    visited.add(event.recordId);
  }

  // --------------------------------------------------
  // SORT FINAL ACTIVITIES CHRONOLOGICALLY
  // --------------------------------------------------

  activities.sort(
    (a, b) =>
      new Date(a.timestamp).getTime() -
      new Date(b.timestamp).getTime()
  );

  // Add final sequence numbers.
  return activities.map((activity, index) => ({
    ...activity,
    sequence: index + 1
  }));
}


// ==================================================
// BUILD ONE RECONSTRUCTED ACTIVITY
// ==================================================

function buildActivity(observations, correlation) {

  const primary = observations[0];

  const actions = observations.map(
    (event) => event.action
  );

  let activityType = primary.action;
  let description = primary.action;

  // --------------------------------------------------
  // FILE ACCESS
  // --------------------------------------------------

  if (
    actions.includes("FILE_ACCESS") ||
    actions.includes("READ")
  ) {
    activityType = "FILE_ACCESS";
    description = "File accessed";
  }

  // --------------------------------------------------
  // USB COPY
  // --------------------------------------------------

  if (
    actions.includes("COPY") ||
    actions.includes("FILE_WRITE")
  ) {
    activityType = "USB_COPY";
    description = "File copied to USB device";
  }

  // --------------------------------------------------
  // NETWORK CONNECTION
  // --------------------------------------------------

  if (
    actions.includes("NETWORK_CONNECTION") ||
    actions.includes("CONNECTION")
  ) {
    activityType = "NETWORK_CONNECTION";
    description =
      "External network connection established";
  }

  // --------------------------------------------------
  // FILE TRANSFER
  // --------------------------------------------------

  if (
    actions.includes("TRANSFER") ||
    actions.includes("OUTBOUND_TRANSFER")
  ) {
    activityType = "FILE_TRANSFER";
    description =
      "File transferred to external destination";
  }

  // --------------------------------------------------
  // EXTRACT COMMON ENTITIES
  // --------------------------------------------------

  const user =
    observations.find((event) => event.user)?.user ||
    null;

  const device =
    observations.find((event) => event.device)?.device ||
    null;

  const file =
    observations.find((event) => event.file)?.file ||
    null;

  const usb =
    observations.find((event) => event.usb)?.usb ||
    observations.find(
      (event) =>
        event.destination &&
        event.destination.startsWith("USB-")
    )?.destination ||
    null;

  const ip =
    observations.find((event) => event.ip)?.ip ||
    observations.find(
      (event) =>
        event.destination &&
        /^\d+\.\d+\.\d+\.\d+$/.test(event.destination)
    )?.destination ||
    null;

  // --------------------------------------------------
  // EVIDENCE SUPPORT CLASSIFICATION
  // --------------------------------------------------

  const sources = [
    ...new Set(
      observations.map(
        (event) => event.source
      )
    )
  ];

  const supportLevel =
    observations.length >= 2 && sources.length >= 2
      ? "strong-corroboration"
      : "single-source";

  // --------------------------------------------------
  // FINAL ACTIVITY OBJECT
  // --------------------------------------------------

  return {

    activityId: `ACT-${primary.recordId}`,

    timestamp: primary.timestamp,

    time: primary.timestamp.slice(11, 19),

    type: activityType,

    description,

    user,

    device,

    file,

    usb,

    ip,

    sources,

    supportingRecords:
      observations.map(
        (event) => event.recordId
      ),

    observationCount:
      observations.length,

    correlation:
      correlation?.strength ||
      "single-source",

    supportLevel,

    sharedEntities:
      correlation?.sharedEntities ||
      []
  };
}