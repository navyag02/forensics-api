/**
 * Finds meaningful relationships between independently
 * observed forensic events.
 *
 * Correlation requires:
 * - different evidence sources
 * - close timestamps
 * - compatible actions
 * - meaningful shared entities
 *
 * A shared device alone is NOT sufficient.
 */

const TIME_WINDOW_MS = 5 * 1000;


// ==================================================
// FIND SHARED ENTITIES
// ==================================================

function getSharedEntities(a, b) {
  const shared = [];

  if (
    a.user &&
    b.user &&
    a.user === b.user
  ) {
    shared.push(`user:${a.user}`);
  }

  if (
    a.device &&
    b.device &&
    a.device === b.device
  ) {
    shared.push(`device:${a.device}`);
  }

  if (
    a.file &&
    b.file &&
    a.file === b.file
  ) {
    shared.push(`file:${a.file}`);
  }

  if (
    a.usb &&
    b.usb &&
    a.usb === b.usb
  ) {
    shared.push(`usb:${a.usb}`);
  }

  if (
    a.ip &&
    b.ip &&
    a.ip === b.ip
  ) {
    shared.push(`ip:${a.ip}`);
  }


  // Example:
  // FILE-002 destination = USB-003
  // USB-002 usb = USB-003

  if (
    a.destination &&
    b.usb &&
    a.destination === b.usb
  ) {
    shared.push(`target:${a.destination}`);
  }

  if (
    b.destination &&
    a.usb &&
    b.destination === a.usb
  ) {
    shared.push(`target:${b.destination}`);
  }


  // Example:
  // FILE-003 destination = 85.21.44.9
  // NET-002 ip = 85.21.44.9

  if (
    a.destination &&
    b.ip &&
    a.destination === b.ip
  ) {
    shared.push(`target:${a.destination}`);
  }

  if (
    b.destination &&
    a.ip &&
    b.destination === a.ip
  ) {
    shared.push(`target:${b.destination}`);
  }

  return shared;
}


// ==================================================
// ACTION COMPATIBILITY
// ==================================================

function areCompatibleActions(actionA, actionB) {
  const pair = new Set([actionA, actionB]);

  return (

    // File access observed by two sources
    (
      pair.has("FILE_ACCESS") &&
      pair.has("READ")
    )

    ||

    // File copied to USB
    (
      pair.has("COPY") &&
      pair.has("FILE_WRITE")
    )

    ||

    // Network connection
    (
      pair.has("NETWORK_CONNECTION") &&
      pair.has("CONNECTION")
    )

    ||

    // File transfer
    (
      pair.has("TRANSFER") &&
      pair.has("OUTBOUND_TRANSFER")
    )
  );
}


// ==================================================
// CORRELATION ENGINE
// ==================================================

export function correlateEvents(events) {

  if (!Array.isArray(events)) {
    throw new Error(
      "Events must be provided as an array."
    );
  }

  const correlations = [];

  for (
    let i = 0;
    i < events.length;
    i++
  ) {

    for (
      let j = i + 1;
      j < events.length;
      j++
    ) {

      const first = events[i];
      const second = events[j];


      // --------------------------------------------------
      // DIFFERENT SOURCES REQUIRED
      // --------------------------------------------------

      if (
        first.source === second.source
      ) {
        continue;
      }


      // --------------------------------------------------
      // TIME PROXIMITY
      // --------------------------------------------------

      const timeDifference =
        Math.abs(
          new Date(second.timestamp).getTime() -
          new Date(first.timestamp).getTime()
        );

      if (
        timeDifference > TIME_WINDOW_MS
      ) {
        continue;
      }


      // --------------------------------------------------
      // ACTION COMPATIBILITY
      // --------------------------------------------------

      if (
        !areCompatibleActions(
          first.action,
          second.action
        )
      ) {
        continue;
      }


      // --------------------------------------------------
      // SHARED ENTITIES
      // --------------------------------------------------

      const sharedEntities =
        getSharedEntities(
          first,
          second
        );

      if (
        sharedEntities.length === 0
      ) {
        continue;
      }


      // --------------------------------------------------
      // STRONG ENTITY MATCH
      // --------------------------------------------------

      const sameFile =
        first.file &&
        second.file &&
        first.file === second.file;

      const sameUser =
        first.user &&
        second.user &&
        first.user === second.user;

      const sameDevice =
        first.device &&
        second.device &&
        first.device === second.device;

      const sameUSB =
        first.usb &&
        second.usb &&
        first.usb === second.usb;

      const sameIP =
        first.ip &&
        second.ip &&
        first.ip === second.ip;

      const targetMatch =
        sharedEntities.some(
          (entity) =>
            entity.startsWith("target:")
        );


      /*
       * A device alone is NOT enough.
       *
       * Strong evidence requires something more specific:
       * file, USB, IP, target, or user+device.
       */

      const strongEntityMatch =
        sameFile ||
        sameUSB ||
        sameIP ||
        targetMatch ||
        (
          sameUser &&
          sameDevice
        );

      if (!strongEntityMatch) {
        continue;
      }


      // --------------------------------------------------
      // RECORD CORRELATION
      // --------------------------------------------------

      correlations.push({

        from: first.recordId,

        to: second.recordId,

        relation:
          "CROSS_SOURCE_CORROBORATION",

        timeDifferenceSeconds:
          Math.round(
            timeDifference / 1000
          ),

        sharedEntities,

        strength: "strong"
      });
    }
  }

  return correlations;
}