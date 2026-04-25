    .text

    .p2align 2
    .globl _main
_main:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    movz w0, #0
    b Lmain_return1
    mov w0, #0
Lmain_return1:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret
