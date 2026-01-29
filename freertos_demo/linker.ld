/*
 * Linker script for FreeRTOS on RISC-V RV32I Simulator
 * 
 * Memory layout:
 * - RAM starts at 0x00000000
 * - Total RAM: 1MB (adjustable)
 */

OUTPUT_ARCH("riscv")
ENTRY(_start)

MEMORY
{
    RAM (rwx) : ORIGIN = 0x00000000, LENGTH = 1M
}

SECTIONS
{
    /* Code section */
    .text : ALIGN(4)
    {
        _text_start = .;
        *(.text.init)
        *(.text.startup)
        *(.text .text.*)
        *(.gnu.linkonce.t.*)
        _text_end = .;
    } > RAM

    /* Read-only data */
    .rodata : ALIGN(4)
    {
        _rodata_start = .;
        *(.rodata .rodata.*)
        *(.gnu.linkonce.r.*)
        _rodata_end = .;
    } > RAM

    /* Data section (initialized) */
    .data : ALIGN(4)
    {
        _data_start = .;
        *(.data .data.*)
        *(.gnu.linkonce.d.*)
        _data_end = .;
    } > RAM

    /* BSS section (uninitialized) */
    .bss : ALIGN(4)
    {
        _bss_start = .;
        *(.bss .bss.*)
        *(.gnu.linkonce.b.*)
        *(COMMON)
        _bss_end = .;
    } > RAM

    /* Heap and stack */
    . = ALIGN(8);
    _heap_start = .;
    _heap_end = ORIGIN(RAM) + LENGTH(RAM) - 0x10000; /* Reserve 64KB for stack */
    
    _stack_end = _heap_end;
    _stack_start = ORIGIN(RAM) + LENGTH(RAM);
    
    /* FreeRTOS IRQ stack (separate from main stack) */
    __freertos_irq_stack_top = _stack_start;

    /* Discard unnecessary sections */
    /DISCARD/ :
    {
        *(.note .note.*)
        *(.comment)
        *(.eh_frame)
    }
}
