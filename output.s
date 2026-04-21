    .text

    .p2align 2
    .globl _main
_main:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    adrp x0, Lstr2@PAGE
    add x0, x0, Lstr2@PAGEOFF
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _printf
    mov w0, #0
Lmain_return1:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .data
    .p2align 2
Lstr2:
    .asciz "Code Golf"
