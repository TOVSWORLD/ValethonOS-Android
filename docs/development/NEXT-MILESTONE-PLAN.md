# Next milestone execution plan

Updated November 17, 2026. Owner correction: documentation and older working
kernel source come first. No technician, equipment purchase or physical
measurement is assumed necessary. This supersedes the earlier selection of a
bench session as the immediate next action.

## Hardware-first implementation basis

Owner requires the complete kernel-facing hardware knowledge base, not only a
UART investigation. The [central contract](DOUGLAS-HARDWARE-CONTRACT.md) now
indexes20 subsystems, source-derived details, resource dependencies and current
evidence. The generated inventory covers430 working-source and152 ACK resource
nodes without identity/boot-argument data. Use it to identify a violated or missing
boot contract and scope the next implementation. Later peripherals stay documented
without becoming prerequisites for the first Linux/PID1 milestone.

## Milestone and evidence

The milestone remains attributable maintained-kernel startup on the tablet,
followed separately by controlled PID1 execution. Recovery, a metadata marker,
a successful compile or an emulator pass cannot close it.

We need an execution trace that distinguishes source shutdown, relocated-image
integrity, actual Linux entry, MMU transition and userspace. Another unchanged
black-screen trial cannot provide that distinction.

## Work now — finish the source/board contract

Continue under existing task #346; keep #348 synchronized. No new micro-issues.

1. **Trace the older working implementations.** Compare the legacy 3.18 tree
   and the exact working 4.9 revision with the tested 6.18 driver/DT. Follow UART0
   register layout, baud clock/divisor setup, RX/TX pin states, initialization,
   suspend/shutdown and console-suppression controls. Match the actual live DT
   compatible and compiled configuration to the driver; a source file merely
   existing in the tree does not establish that it runs. Record source file, revision
   and exact evidence for each claim, rather than rediscovering GPIO numbers.
2. **Connect logical pins to board/electrical documentation.** Reuse the already
   found maintainer image. Determine what contacts it actually labels. Follow
   exact-model board identifiers, any available schematic/net names, SoC package
   and I/O-bank electrical documentation. Treat other MT8163 boards as leads,
   not Douglas wiring proof. Trace a UART supply connection explicitly; a nearby
   VIO18 name is insufficient.
3. **Produce one decision record.** For each needed fact mark source-established,
   inferred, unresolved, or inaccessible, with a citation and its limitation.
   A blocked download is recorded once and is not evidence of absent documentation.
   Identify the smallest truly unresolved question before requesting owner action.
   Do not repeat broad searches without a new source, identifier or concrete lead.

Already advanced November 17: pinned 4.9 Douglas/SoC DTS and pinctrl sources
were retrieved through the GitHub connector. They confirm the legacy UART0,
26 MHz, GPIO79/80 contract. They do not themselves provide a PCB test-pad number
or an explicit UART I/O-supply phandle in the inspected definitions. Continue the
bank-to-board trace; do not declare the source exhausted. Vendor-driver selection
is now corroborated by MTK_SERIAL/CONSOLE=y, linked console/baud/probe functions
and the archived live UART0 compatible fallback. The next unresolved source
question is the pin bank's supply and accessible board contact/net, not which
vendor UART implementation was built.

## Build one decisive test from that contract

After the source/board record, choose the test from evidence:

- If documented UART access and electrical compatibility are established, finish
  the exact connection/console package. Prove readable output on the working
  baseline, then capture the maintained kernel with that same qualified path.
  This is conditional; it does not authorize a guessed pad or voltage.
- If a specific board fact still cannot be resolved from documentation, explain
  the missing link and why a narrowly scoped physical observation would settle it.
  Present the concrete request, rather than insisting the owner buy a toolkit.
- If UART is not practical under the owner's constraints, prepare **one combined**
  software test: post-relocation full-image integrity plus markers inside actual
  Linux entry/MMU stages in the existing retained buffer. Validate the complete
  package before one hardware attempt. Do not substitute another stub-only test
  or USB setting change. This package is not yet implemented.

Before any hardware attempt, state the discriminating outcomes, exact changed
artifacts, what each outcome proves, recovery path and single-attempt limit.
Do not recycle a consumed authorization or repeat the original installation.
After a trial, collect once, verify original state and update the same issue,
receipt, project memory and work queue before proposing a follow-up.

## Immediate acceptance gate

The source/board contract is complete when it either supplies the information
needed for a defensible UART test or identifies a precise remaining fact and
why documentation has not established it. Finding another generic pin list,
adding host tests or rewording the roadmap is not that acceptance result.

No owner input is currently blocking source research. No equipment/route question
is pending. The next progress update must report a resolved technical claim or
specific source obstacle, not repeat a plan or ask the owner to watch another boot.

Source trace receipt: [legacy-uart-source-trace.json](../../evidence/independent-recovery/legacy-uart-source-trace.json).
