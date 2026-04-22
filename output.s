    .text

    .p2align 2
    .globl _main
_main:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #16
    adrp x0, Lstr2@PAGE
    add x0, x0, Lstr2@PAGEOFF
    stur w0, [x29, #-8]
    mov w0, #0
    stur x0, [x29, #-16]
    ldur x0, [x29, #-8]
    stur x0, [x29, #-16]
Lfor3:
    ldur x0, [x29, #-16]
    ldr w0, [x0]
    cbz w0, Lforend5
    adrp x0, Lstr6@PAGE
    add x0, x0, Lstr6@PAGEOFF
    str x0, [sp, #-16]!
    ldur x0, [x29, #-16]
    ldr w0, [x0]
    mov w0, w0
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
Lforupd4:
    ldur x0, [x29, #-16]
    mov x1, x0
    add x1, x1, #4
    stur x1, [x29, #-16]
    b Lfor3
Lforend5:
    adrp x0, Lstr7@PAGE
    add x0, x0, Lstr7@PAGEOFF
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
Lstr2:
    .asciz "hello$$你好¢¢世界€€world"
    .p2align 2
Lstr6:
    .asciz "%04X "
    .p2align 2
Lstr7:
    .asciz "\n"
