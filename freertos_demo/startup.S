/*
 * Startup code for FreeRTOS on RISC-V RV32I
 * Minimal startup with basic initialization
 */

.section .text.init
.global _start
.type _start, @function

_start:
    /* Disable interrupts */
    csrw mie, zero
    csrw mstatus, zero
    
    /* Set up stack pointer */
    la sp, _stack_start
    
    /* Clear BSS section */
    la a0, _bss_start
    la a1, _bss_end
    j 2f
1:
    sw zero, 0(a0)
    addi a0, a0, 4
2:
    blt a0, a1, 1b
    
    /* Set up trap vector */
    la t0, freertos_risc_v_trap_handler
    csrw mtvec, t0
    
    /* Enable interrupts */
    li t0, 0x1800        /* Enable MIE (machine interrupts) */
    csrs mstatus, t0
    
    li t0, 0x80          /* Enable timer interrupt (bit 7) */
    csrs mie, t0
    
    /* Jump to main */
    call main
    
    /* If main returns, loop forever */
_hang:
    j _hang

.size _start, . - _start
