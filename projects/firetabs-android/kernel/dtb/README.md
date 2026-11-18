# Douglas DT-only integration experiment

> Historical source/integration snapshot. Use the [current hardware contract](../../../../docs/development/DOUGLAS-HARDWARE-CONTRACT.md)
> for consolidated implementation status and later boot evidence. Statements below
> about routes/builds not yet established describe their original audit date.

This is a source/compilation step toward a maintained Android 17 / 6.18 kernel port.
It is **not an installable device image**. Kernel compilation and all hardware validation
remain unperformed. Do not pack or flash the output.

## Reproduce

From repository root, with Python 3.12+ and host cc/clang, bison and flex:

```sh
python3 scripts/setup_dtb_tools.py --download
python3 scripts/build_douglas_dtb.py
```

The explicit download builds dtc 1.8.1 and fdtget under ignored work/dtb-tool using
SHA256-locked source and Meson/Ninja wheels. Supported bootstrap hosts are Linux x86_64
and macOS ARM64. With cached archives, omit --download for an offline bootstrap.
This is an input-pinned build, not a fully hermetic host toolchain/container.

`build_douglas_dtb.py --verify-only` checks tracked source and patch integrity without
compiler invocation or network. The normal build preprocesses real inputs, applies two
small source corrections, rejects all compiler diagnostics, compiles a DTB and inspects
its header and properties with fdtget. Outputs stay under work/dtb-compile/repro/.
No force/suppression options are used and a failed command fails the build.

## Inputs and modifications

[evidence/dtb-compile](../../../../evidence/dtb-compile/) contains the exact input lock,
unchanged upstream source and historical experiment records. At the selected pins the
closure is 26 files: 20 donor DTS/bindings and six ACK headers. The extra ACK thermal
binding was selected after a real compile error, not invented as a constant replacement.
Original file authorship/licenses remain in each source header; existing kernel-audit
license/notice files cover the captured terms. First-party licensing choices do not
relicense these files.

The two reviewed patches add the missing thermal include, give memory its existing
unit address, and declare the cooling cells already referenced by CPU cooling maps.
They preserve the donor memory size, power/voltage data and PSCI method. A correct
property declaration does not validate runtime thermal policy or firmware behavior.
This fixture/patch set is not a complete in-kernel board/driver integration patch queue.

## What is measured

[experiment.json](experiment.json) pins the corrected DTB's expected bytes/hash.
[Local result](../../../../evidence/dtb-compile/local-result.json) records actual commands,
exit codes, identity inspection and artifact hash. The Linux CI Android job repeats the
compile and requires the same hash. The binary itself is not committed or released.

The generated tree identifies Amazon Fire HD 8 (2017), amazon,douglas, mediatek,mt8163.
It retains **512 MiB** in its memory reg and **PSCI** on all CPU nodes. These are known
unvalidated donor assumptions for the user's 1.5 GB board; neither has been reconciled
with actual bootloader/secure-memory behavior. The panel/touch paths and all driver
bindings still need board integration. A successful parse cannot establish those facts.

## Binding-validation boundary

A separate local dtschema 2026.9 attempt ran only its built-in core schemas; the complete
matching ACK/donor kernel binding corpus was not supplied. It emitted raw-byte/property
context diagnostics despite returning zero. The report explicitly marks that validation
**not passed**. Do not classify those missing-context messages as confirmed device bugs.
Full kernel/donor schemas and board-specific reconciliation are separate work.

See [DT experiment details](../../../../docs/development/DOUGLAS-DTB-EXPERIMENT.md)
for failures, changes, tool setup, source origins and the next kernel integration steps.
