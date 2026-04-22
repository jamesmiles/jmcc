    .text

    .p2align 2
    .globl _process
_process:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #16
    stur w0, [x29, #-8]
    adrp x9, _sum@PAGE
    add x9, x9, _sum@PAGEOFF
    ldr x0, [x9]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _abs
    ldr x1, [sp], #16
    add x0, x1, x0
    adrp x9, _sum@PAGE
    add x9, x9, _sum@PAGEOFF
    str x0, [x9]
    adrp x9, _prod@PAGE
    add x9, x9, _prod@PAGEOFF
    ldr x0, [x9]
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _labs
    str x0, [sp, #-16]!
    movz w0, #1
    str x0, [sp, #-16]!
    movz w0, #27
    ldr x1, [sp], #16
    lslv w0, w1, w0
    ldr x1, [sp], #16
    sxtw x0, w0
    cmp x1, x0
    cset w0, lt
    cbz w0, Landfalse4
    ldur w0, [x29, #-8]
    cbz w0, Landfalse4
    mov w0, #1
    b Landend5
Landfalse4:
    mov w0, #0
Landend5:
    cbz w0, Lelse2
    adrp x9, _prod@PAGE
    add x9, x9, _prod@PAGEOFF
    ldr x0, [x9]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-8]
    ldr x1, [sp], #16
    mul x0, x1, x0
    adrp x9, _prod@PAGE
    add x9, x9, _prod@PAGEOFF
    str x0, [x9]
Lelse2:
    mov w0, #0
Lprocess_return1:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .p2align 2
    .globl _ipow
_ipow:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #32
    stur w0, [x29, #-8]
    stur w1, [x29, #-16]
    ldur w0, [x29, #-8]
    sxtw x0, w0
    stur x0, [x29, #-24]
    mov w0, #0
    stur w0, [x29, #-32]
    ldur w0, [x29, #-16]
    str x0, [sp, #-16]!
    movz w0, #0
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, eq
    cbz w0, Lelse7
    movz x0, #1
    b Lipow_return6
Lelse7:
    movz w0, #2
    stur w0, [x29, #-32]
Lfor9:
    ldur w0, [x29, #-32]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-16]
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ls
    cbz w0, Lforend11
    ldur x0, [x29, #-24]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-8]
    ldr x1, [sp], #16
    mul x0, x1, x0
    stur x0, [x29, #-24]
Lforupd10:
    ldur w0, [x29, #-32]
    add w0, w0, #1
    stur w0, [x29, #-32]
    b Lfor9
Lforend11:
    ldur x0, [x29, #-24]
    b Lipow_return6
    mov w0, #0
Lipow_return6:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .p2align 2
    .globl _main
_main:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #64
    mov w0, #0
    stur w0, [x29, #-8]
    movz w0, #5
    stur w0, [x29, #-16]
    movz w0, #5
    neg w0, w0
    stur w0, [x29, #-24]
    movz w0, #2
    neg w0, w0
    stur w0, [x29, #-32]
    movz w0, #1
    stur w0, [x29, #-40]
    movz w0, #3
    stur w0, [x29, #-48]
    movz w0, #7
    stur w0, [x29, #-56]
    movz w0, #11
    str x0, [sp, #-16]!
    ldur w0, [x29, #-16]
    str x0, [sp, #-16]!
    ldr x1, [sp], #16
    ldr x0, [sp], #16
    bl _ipow
    stur x0, [x29, #-64]
    ldur w0, [x29, #-48]
    neg w0, w0
    stur w0, [x29, #-8]
Lfor13:
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    movz w0, #3
    str x0, [sp, #-16]!
    movz w0, #3
    str x0, [sp, #-16]!
    ldr x1, [sp], #16
    ldr x0, [sp], #16
    bl _ipow
    ldr x1, [sp], #16
    sxtw x1, w1
    cmp x1, x0
    cset w0, le
    cbz w0, Lforend15
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _process
Lforupd14:
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-48]
    ldr x1, [sp], #16
    add w0, w1, w0
    stur w0, [x29, #-8]
    b Lfor13
Lforend15:
    ldur w0, [x29, #-56]
    neg w0, w0
    stur w0, [x29, #-8]
Lfor16:
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-56]
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, le
    cbz w0, Lforend18
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _process
Lforupd17:
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-16]
    ldr x1, [sp], #16
    add w0, w1, w0
    stur w0, [x29, #-8]
    b Lfor16
Lforend18:
    movz w0, #555
    stur w0, [x29, #-8]
Lfor19:
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    movz w0, #550
    str x0, [sp, #-16]!
    ldur w0, [x29, #-24]
    ldr x1, [sp], #16
    sub w0, w1, w0
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, le
    cbz w0, Lforend21
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _process
Lforupd20:
    ldur w0, [x29, #-8]
    add w0, w0, #1
    stur w0, [x29, #-8]
    b Lfor19
Lforend21:
    movz w0, #22
    stur w0, [x29, #-8]
Lfor22:
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    movz w0, #28
    neg w0, w0
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ge
    cbz w0, Lforend24
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _process
Lforupd23:
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-48]
    ldr x1, [sp], #16
    sub w0, w1, w0
    stur w0, [x29, #-8]
    b Lfor22
Lforend24:
    movz w0, #1927
    stur w0, [x29, #-8]
Lfor25:
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    movz w0, #1939
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, le
    cbz w0, Lforend27
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _process
Lforupd26:
    ldur w0, [x29, #-8]
    add w0, w0, #1
    stur w0, [x29, #-8]
    b Lfor25
Lforend27:
    ldur w0, [x29, #-16]
    stur w0, [x29, #-8]
Lfor28:
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-24]
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ge
    cbz w0, Lforend30
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _process
Lforupd29:
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-32]
    neg w0, w0
    ldr x1, [sp], #16
    sub w0, w1, w0
    stur w0, [x29, #-8]
    b Lfor28
Lforend30:
    ldur x0, [x29, #-64]
    stur w0, [x29, #-8]
Lfor31:
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldur x0, [x29, #-64]
    str x0, [sp, #-16]!
    ldur w0, [x29, #-40]
    ldr x1, [sp], #16
    sxtw x0, w0
    add x0, x1, x0
    ldr x1, [sp], #16
    sxtw x1, w1
    cmp x1, x0
    cset w0, le
    cbz w0, Lforend33
    ldur w0, [x29, #-8]
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _process
Lforupd32:
    ldur w0, [x29, #-8]
    add w0, w0, #1
    stur w0, [x29, #-8]
    b Lfor31
Lforend33:
    movz w0, #4
    str x0, [sp, #-16]!
    adrp x0, Lstr34@PAGE
    add x0, x0, Lstr34@PAGEOFF
    str x0, [sp, #-16]!
    ldr x1, [sp], #16
    ldr x0, [sp], #16
    bl _setlocale
    adrp x0, Lstr35@PAGE
    add x0, x0, Lstr35@PAGEOFF
    str x0, [sp, #-16]!
    adrp x9, _sum@PAGE
    add x9, x9, _sum@PAGEOFF
    ldr x0, [x9]
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    adrp x0, Lstr36@PAGE
    add x0, x0, Lstr36@PAGEOFF
    str x0, [sp, #-16]!
    adrp x9, _prod@PAGE
    add x9, x9, _prod@PAGEOFF
    ldr x0, [x9]
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    b Lmain_return12
    mov w0, #0
Lmain_return12:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .data
    .p2align 3
    .globl _prod
_prod:
    .quad 1

    .data
    .p2align 3
    .globl _sum
_sum:
    .quad 0

    .data
    .p2align 2
Lstr34:
    .asciz ""
    .p2align 2
Lstr35:
    .asciz "sum  = % 'ld\n"
    .p2align 2
Lstr36:
    .asciz "prod = % 'ld\n"
