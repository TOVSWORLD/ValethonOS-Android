/* Emulator-only addresses. No physical placement is admitted. */
ENTRY(lc_init)
SECTIONS {
 . = 0x41000000;
 .text : { *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
}
