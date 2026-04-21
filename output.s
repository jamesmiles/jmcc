    .text

    .p2align 2
    .globl _memoizeIsPrime
_memoizeIsPrime:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #64
    cmp w0, #0
    cset w0, ne
    stur w0, [x29, #-8]
    stur w1, [x29, #-16]
    movz w0, #1
    str x0, [sp, #-16]!
    ldur x0, [x29, #-8]
    str x0, [sp, #-16]!
    movz w0, #2
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldr x1, [sp], #16
    strb w1, [x0]
    and w0, w1, #0xff
    movz w0, #1
    str x0, [sp, #-16]!
    ldur x0, [x29, #-8]
    str x0, [sp, #-16]!
    movz w0, #3
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldr x1, [sp], #16
    strb w1, [x0]
    and w0, w1, #0xff
    mov x0, #4
    str x0, [sp, #-16]!
    ldur w0, [x29, #-16]
    sxtw x0, w0
    ldr x1, [sp], #16
    mul x0, x1, x0
    add x0, x0, #15
    bic x0, x0, #15
    sub sp, sp, x0
    mov x0, sp
    stur x0, [x29, #-24]
    movz w0, #3
    str x0, [sp, #-16]!
    ldur x0, [x29, #-24]
    str x0, [sp, #-16]!
    movz w0, #0
    sxtw x0, w0
    ldr x1, [sp], #16
    mov x2, #4
    mul x0, x0, x2
    add x0, x1, x0
    ldr x1, [sp], #16
    str w1, [x0]
    mov w0, w1
    movz w0, #1
    stur w0, [x29, #-32]
    movz w0, #5
    stur w0, [x29, #-40]
Lfor2:
    ldur w0, [x29, #-40]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-16]
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, lt
    cbz w0, Lforend4
    movz w0, #1
    cmp w0, #0
    cset w0, ne
    sturb w0, [x29, #-48]
    movz w0, #0
    stur w0, [x29, #-56]
Lfor5:
    ldur w0, [x29, #-56]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-32]
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, lt
    cbz w0, Lforend7
    ldur x0, [x29, #-24]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-56]
    sxtw x0, w0
    ldr x1, [sp], #16
    mov x2, #4
    mul x0, x0, x2
    add x0, x1, x0
    ldr w0, [x0]
    stur w0, [x29, #-64]
    ldur w0, [x29, #-40]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-64]
    ldr x1, [sp], #16
    sdiv w2, w1, w0
    msub w0, w2, w0, w1
    str x0, [sp, #-16]!
    movz w0, #0
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, eq
    cbz w0, Lelse8
    movz w0, #0
    cmp w0, #0
    cset w0, ne
    sturb w0, [x29, #-48]
    b Lforend7
Lelse8:
    ldur w0, [x29, #-64]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-64]
    ldr x1, [sp], #16
    mul w0, w1, w0
    str x0, [sp, #-16]!
    ldur w0, [x29, #-40]
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, gt
    cbz w0, Lelse10
    b Lforend7
Lelse10:
Lforupd6:
    ldur w0, [x29, #-56]
    add w0, w0, #1
    stur w0, [x29, #-56]
    b Lfor5
Lforend7:
    ldurb w0, [x29, #-48]
    cbz w0, Lelse12
    ldur w0, [x29, #-40]
    str x0, [sp, #-16]!
    ldur x0, [x29, #-24]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-32]
    mov w1, w0
    add w1, w1, #1
    stur w1, [x29, #-32]
    sxtw x0, w0
    ldr x1, [sp], #16
    mov x2, #4
    mul x0, x0, x2
    add x0, x1, x0
    ldr x1, [sp], #16
    str w1, [x0]
    mov w0, w1
    movz w0, #1
    str x0, [sp, #-16]!
    ldur x0, [x29, #-8]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-40]
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldr x1, [sp], #16
    strb w1, [x0]
    and w0, w1, #0xff
Lelse12:
Lforupd3:
    ldur w0, [x29, #-40]
    str x0, [sp, #-16]!
    movz w0, #2
    ldr x1, [sp], #16
    add w0, w1, w0
    stur w0, [x29, #-40]
    b Lfor2
Lforend4:
    mov w0, #0
LmemoizeIsPrime_return1:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .p2align 2
    .globl _sumOfDecimalDigits
_sumOfDecimalDigits:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #16
    stur w0, [x29, #-8]
    movz w0, #0
    stur w0, [x29, #-16]
Lwhile15:
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    movz w0, #0
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, gt
    cbz w0, Lwhileend16
    ldur w0, [x29, #-16]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    movz w0, #10
    ldr x1, [sp], #16
    sdiv w2, w1, w0
    msub w0, w2, w0, w1
    ldr x1, [sp], #16
    add w0, w1, w0
    stur w0, [x29, #-16]
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    movz w0, #10
    ldr x1, [sp], #16
    sdiv w0, w1, w0
    stur w0, [x29, #-8]
    b Lwhile15
Lwhileend16:
    ldur w0, [x29, #-16]
    b LsumOfDecimalDigits_return14
    mov w0, #0
LsumOfDecimalDigits_return14:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .p2align 2
    .globl _main
_main:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #32
    movz w0, #500
    stur w0, [x29, #-8]
    adrp x0, Lstr18@PAGE
    add x0, x0, Lstr18@PAGEOFF
    str x0, [sp, #-16]!
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    mov x0, #1
    str x0, [sp, #-16]!
    ldur w0, [x29, #-8]
    sxtw x0, w0
    ldr x1, [sp], #16
    mul x0, x1, x0
    add x0, x0, #15
    bic x0, x0, #15
    sub sp, sp, x0
    mov x0, sp
    stur x0, [x29, #-16]
    ldur x0, [x29, #-16]
    str x0, [sp, #-16]!
    movz w0, #0
    str x0, [sp, #-16]!
    movz w0, #1
    str x0, [sp, #-16]!
    ldr x2, [sp], #16
    ldr x1, [sp], #16
    ldr x0, [sp], #16
    bl _memset
    ldur x0, [x29, #-16]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldr x1, [sp], #16
    ldr x0, [sp], #16
    bl _memoizeIsPrime
    adrp x0, Lstr19@PAGE
    add x0, x0, Lstr19@PAGEOFF
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _printf
    movz w0, #1
    stur w0, [x29, #-24]
    movz w0, #3
    stur w0, [x29, #-32]
Lfor20:
    ldur w0, [x29, #-32]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-8]
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, lt
    cbz w0, Lforend22
    ldur x0, [x29, #-16]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-32]
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    cbz w0, Landfalse25
    ldur x0, [x29, #-16]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-32]
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _sumOfDecimalDigits
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    cbz w0, Landfalse25
    mov w0, #1
    b Landend26
Landfalse25:
    mov w0, #0
Landend26:
    cbz w0, Lelse23
    adrp x0, Lstr27@PAGE
    add x0, x0, Lstr27@PAGEOFF
    str x0, [sp, #-16]!
    ldur w0, [x29, #-32]
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    ldur w0, [x29, #-24]
    add w0, w0, #1
    stur w0, [x29, #-24]
    ldur w0, [x29, #-24]
    str x0, [sp, #-16]!
    movz w0, #10
    ldr x1, [sp], #16
    sdiv w2, w1, w0
    msub w0, w2, w0, w1
    str x0, [sp, #-16]!
    movz w0, #0
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, eq
    cbz w0, Lelse28
    adrp x0, Lstr30@PAGE
    add x0, x0, Lstr30@PAGEOFF
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _printf
Lelse28:
Lelse23:
Lforupd21:
    ldur w0, [x29, #-32]
    str x0, [sp, #-16]!
    movz w0, #2
    ldr x1, [sp], #16
    add w0, w1, w0
    stur w0, [x29, #-32]
    b Lfor20
Lforend22:
    adrp x0, Lstr31@PAGE
    add x0, x0, Lstr31@PAGEOFF
    str x0, [sp, #-16]!
    ldur w0, [x29, #-24]
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    b Lmain_return17
    mov w0, #0
Lmain_return17:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .data
    .p2align 2
Lstr18:
    .asciz "Rosetta Code: additive primes less than %d:\n"
    .p2align 2
Lstr19:
    .asciz "   2"
    .p2align 2
Lstr27:
    .asciz "%4d"
    .p2align 2
Lstr30:
    .asciz "\n"
    .p2align 2
Lstr31:
    .asciz "\nThose were %d additive primes.\n"
