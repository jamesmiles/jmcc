    .text

    .p2align 2
    .globl _main
_main:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    movz w0, #4
    str x0, [sp, #-16]!
    movz w0, #16
    str x0, [sp, #-16]!
    movz w0, #4
    ldr x1, [sp], #16
    mul w0, w1, w0
    str x0, [sp, #-16]!
    movz w0, #4
    ldr x1, [sp], #16
    mul w0, w1, w0
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse2
    movz w0, #1
    b Lmain_return1
Lelse2:
    movz w0, #42
    str x0, [sp, #-16]!
    adrp x0, _arr@PAGE
    add x0, x0, _arr@PAGEOFF
    str x0, [sp, #-16]!
    movz w0, #63
    sxtw x0, w0
    ldr x1, [sp], #16
    mov x2, #4
    mul x0, x0, x2
    add x0, x1, x0
    ldr x1, [sp], #16
    str w1, [x0]
    mov w0, w1
    adrp x0, _arr@PAGE
    add x0, x0, _arr@PAGEOFF
    str x0, [sp, #-16]!
    movz w0, #63
    sxtw x0, w0
    ldr x1, [sp], #16
    mov x2, #4
    mul x0, x0, x2
    add x0, x1, x0
    ldr w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #42
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse4
    movz w0, #2
    b Lmain_return1
Lelse4:
    adrp x9, _sentinel@PAGE
    add x9, x9, _sentinel@PAGEOFF
    ldr w0, [x9]
    str x0, [sp, #-16]!
    movz w0, #99
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse6
    movz w0, #3
    b Lmain_return1
Lelse6:
    adrp x0, Lstr8@PAGE
    add x0, x0, Lstr8@PAGEOFF
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _printf
    movz w0, #0
    b Lmain_return1
    mov w0, #0
Lmain_return1:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .data
    .p2align 2
    .globl _arr
_arr:
    .zero 4

    .data
    .p2align 2
    .globl _sentinel
_sentinel:
    .long 99

    .data
    .p2align 2
Lstr8:
    .asciz "ok\n"
