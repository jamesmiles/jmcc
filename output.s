    .text

    .p2align 2
    .globl _f_1
_f_1:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #16
    stur x0, [x29, #-8]
    movz w0, #1
    neg w0, w0
    b Lf_1_return1
    mov w0, #0
Lf_1_return1:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .p2align 2
    .globl _f0
_f0:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #16
    stur x0, [x29, #-8]
    movz w0, #0
    b Lf0_return2
    mov w0, #0
Lf0_return2:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .p2align 2
    .globl _f1
_f1:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #16
    stur x0, [x29, #-8]
    movz w0, #1
    b Lf1_return3
    mov w0, #0
Lf1_return3:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .p2align 2
    .globl _eval
_eval:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #16
    stur x0, [x29, #-8]
    ldur x0, [x29, #-8]
    add x0, x0, #0
    ldr x0, [x0]
    str x0, [sp, #-16]!
    ldur x0, [x29, #-8]
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    ldr x16, [sp], #16
    blr x16
    b Leval_return4
    mov w0, #0
Leval_return4:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .p2align 2
    .globl _B
_B:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #16
    stur x0, [x29, #-8]
    ldur x0, [x29, #-8]
    add x0, x0, #8
    ldr x0, [x0]
    ldr w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #1
    ldr x1, [sp], #16
    sub w0, w1, w0
    str x0, [sp, #-16]!
    ldur x0, [x29, #-8]
    add x0, x0, #8
    ldr x0, [x0]
    ldr x1, [sp], #16
    str w1, [x0]
    mov x0, x1
    stur w0, [x29, #-16]
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _B@PAGE
    add x0, x0, _B@PAGEOFF
    str x0, [x9, #0]
    ldur w0, [x29, #-16]
    sub x0, x29, #16
    str x0, [x9, #8]
    ldur x0, [x29, #-8]
    str x0, [x9, #16]
    ldur x0, [x29, #-8]
    add x0, x0, #16
    ldr x0, [x0]
    str x0, [x9, #24]
    ldur x0, [x29, #-8]
    add x0, x0, #24
    ldr x0, [x0]
    str x0, [x9, #32]
    ldur x0, [x29, #-8]
    add x0, x0, #32
    ldr x0, [x0]
    str x0, [x9, #40]
    ldur x0, [x29, #-8]
    add x0, x0, #40
    ldr x0, [x0]
    str x0, [x9, #48]
    add sp, sp, #64
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _B@PAGE
    add x0, x0, _B@PAGEOFF
    str x0, [x9, #0]
    ldur w0, [x29, #-16]
    sub x0, x29, #16
    str x0, [x9, #8]
    ldur x0, [x29, #-8]
    str x0, [x9, #16]
    ldur x0, [x29, #-8]
    add x0, x0, #16
    ldr x0, [x0]
    str x0, [x9, #24]
    ldur x0, [x29, #-8]
    add x0, x0, #24
    ldr x0, [x0]
    str x0, [x9, #32]
    ldur x0, [x29, #-8]
    add x0, x0, #32
    ldr x0, [x0]
    str x0, [x9, #40]
    ldur x0, [x29, #-8]
    add x0, x0, #40
    ldr x0, [x0]
    str x0, [x9, #48]
    mov x0, x9
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _A
    b LB_return5
    mov w0, #0
LB_return5:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .p2align 2
    .globl _A
_A:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #16
    stur x0, [x29, #-8]
    ldur x0, [x29, #-8]
    add x0, x0, #8
    ldr x0, [x0]
    ldr w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #0
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, le
    cbz w0, Lternfalse7
    ldur x0, [x29, #-8]
    add x0, x0, #40
    ldr x0, [x0]
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _eval
    str x0, [sp, #-16]!
    ldur x0, [x29, #-8]
    add x0, x0, #48
    ldr x0, [x0]
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _eval
    ldr x1, [sp], #16
    add w0, w1, w0
    b Lternend8
Lternfalse7:
    ldur x0, [x29, #-8]
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _B
Lternend8:
    b LA_return6
    mov w0, #0
LA_return6:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .p2align 2
    .globl _main
_main:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #32
    stur w0, [x29, #-8]
    stur x1, [x29, #-16]
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    movz w0, #2
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, eq
    cbz w0, Lternfalse10
    ldur x0, [x29, #-16]
    str x0, [sp, #-16]!
    movz w0, #1
    sxtw x0, w0
    ldr x1, [sp], #16
    mov x2, #8
    mul x0, x0, x2
    add x0, x1, x0
    ldr x0, [x0]
    str x0, [sp, #-16]!
    movz w0, #0
    str x0, [sp, #-16]!
    movz w0, #0
    str x0, [sp, #-16]!
    ldr x2, [sp], #16
    ldr x1, [sp], #16
    ldr x0, [sp], #16
    bl _strtol
    b Lternend11
Lternfalse10:
    movz w0, #10
Lternend11:
    stur w0, [x29, #-24]
    adrp x0, Lstr12@PAGE
    add x0, x0, Lstr12@PAGEOFF
    str x0, [sp, #-16]!
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _B@PAGE
    add x0, x0, _B@PAGEOFF
    str x0, [x9, #0]
    ldur w0, [x29, #-24]
    sub x0, x29, #24
    str x0, [x9, #8]
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f1@PAGE
    add x0, x0, _f1@PAGEOFF
    str x0, [x9, #0]
    add sp, sp, #64
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f1@PAGE
    add x0, x0, _f1@PAGEOFF
    str x0, [x9, #0]
    mov x0, x9
    str x0, [x9, #16]
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f_1@PAGE
    add x0, x0, _f_1@PAGEOFF
    str x0, [x9, #0]
    add sp, sp, #64
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f_1@PAGE
    add x0, x0, _f_1@PAGEOFF
    str x0, [x9, #0]
    mov x0, x9
    str x0, [x9, #24]
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f_1@PAGE
    add x0, x0, _f_1@PAGEOFF
    str x0, [x9, #0]
    add sp, sp, #64
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f_1@PAGE
    add x0, x0, _f_1@PAGEOFF
    str x0, [x9, #0]
    mov x0, x9
    str x0, [x9, #32]
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f1@PAGE
    add x0, x0, _f1@PAGEOFF
    str x0, [x9, #0]
    add sp, sp, #64
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f1@PAGE
    add x0, x0, _f1@PAGEOFF
    str x0, [x9, #0]
    mov x0, x9
    str x0, [x9, #40]
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f0@PAGE
    add x0, x0, _f0@PAGEOFF
    str x0, [x9, #0]
    add sp, sp, #64
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f0@PAGE
    add x0, x0, _f0@PAGEOFF
    str x0, [x9, #0]
    mov x0, x9
    str x0, [x9, #48]
    add sp, sp, #64
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _B@PAGE
    add x0, x0, _B@PAGEOFF
    str x0, [x9, #0]
    ldur w0, [x29, #-24]
    sub x0, x29, #24
    str x0, [x9, #8]
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f1@PAGE
    add x0, x0, _f1@PAGEOFF
    str x0, [x9, #0]
    add sp, sp, #64
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f1@PAGE
    add x0, x0, _f1@PAGEOFF
    str x0, [x9, #0]
    mov x0, x9
    str x0, [x9, #16]
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f_1@PAGE
    add x0, x0, _f_1@PAGEOFF
    str x0, [x9, #0]
    add sp, sp, #64
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f_1@PAGE
    add x0, x0, _f_1@PAGEOFF
    str x0, [x9, #0]
    mov x0, x9
    str x0, [x9, #24]
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f_1@PAGE
    add x0, x0, _f_1@PAGEOFF
    str x0, [x9, #0]
    add sp, sp, #64
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f_1@PAGE
    add x0, x0, _f_1@PAGEOFF
    str x0, [x9, #0]
    mov x0, x9
    str x0, [x9, #32]
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f1@PAGE
    add x0, x0, _f1@PAGEOFF
    str x0, [x9, #0]
    add sp, sp, #64
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f1@PAGE
    add x0, x0, _f1@PAGEOFF
    str x0, [x9, #0]
    mov x0, x9
    str x0, [x9, #40]
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f0@PAGE
    add x0, x0, _f0@PAGEOFF
    str x0, [x9, #0]
    add sp, sp, #64
    sub sp, sp, #64
    mov x9, sp
    str xzr, [x9, #0]
    str xzr, [x9, #8]
    str xzr, [x9, #16]
    str xzr, [x9, #24]
    str xzr, [x9, #32]
    str xzr, [x9, #40]
    str xzr, [x9, #48]
    adrp x0, _f0@PAGE
    add x0, x0, _f0@PAGEOFF
    str x0, [x9, #0]
    mov x0, x9
    str x0, [x9, #48]
    mov x0, x9
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _A
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    b Lmain_return9
    mov w0, #0
Lmain_return9:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .data
    .p2align 2
Lstr12:
    .asciz "%d\n"
