/* Minimal freestanding x86-64 startup for QEMU */
/* Links with compiled C code that provides main() */
/* Output via serial port 0x3f8, exit via isa-debug-exit port 0x501 */

.section .text
.global _start
.global _serial_putchar
.global _exit_qemu

_start:
    /* Set up a small stack */
    mov $0x7c00, %rsp

    /* Call main */
    call main

    /* Exit with return value from main */
    mov %eax, %edi
    call _exit_qemu

    /* Should not reach here */
    hlt

/* void _serial_putchar(int c) */
/* Write a character to serial port COM1 (0x3f8) */
_serial_putchar:
    mov %edi, %eax
    mov $0x3f8, %dx
.Lwait:
    /* Wait for transmit buffer empty (LSR bit 5) */
    push %rax
    mov $0x3fd, %dx
    in %dx, %al
    test $0x20, %al
    pop %rax
    jz .Lwait
    mov $0x3f8, %dx
    out %al, %dx
    ret

/* void _exit_qemu(int code) */
/* Exit QEMU via isa-debug-exit device (port 0x501) */
/* QEMU exit code = (value << 1) | 1, so we pre-shift */
_exit_qemu:
    mov %edi, %eax
    mov $0x501, %dx
    out %al, %dx
    hlt
    ret
