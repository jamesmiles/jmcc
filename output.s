    .text

    .p2align 2
_ntd_print:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #48
    stur x0, [x29, #-16]
    stur x1, [x29, #-8]
    stur x2, [x29, #-24]
    stur x3, [x29, #-32]
    sub x0, x29, #16
    add x0, x0, #0
    ldr x0, [x0]
    str x0, [sp, #-16]!
    movz w0, #0
    ldr x1, [sp], #16
    sxtw x0, w0
    cmp x1, x0
    cset w0, hi
    cbz w0, Lelse2
    movz w0, #91
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _putchar
    movz w0, #0
    stur x0, [x29, #-40]
Lfor4:
    ldur x0, [x29, #-40]
    str x0, [sp, #-16]!
    sub x0, x29, #16
    add x0, x0, #0
    ldr x0, [x0]
    ldr x1, [sp], #16
    cmp x1, x0
    cset w0, lo
    cbz w0, Lforend6
    ldur x0, [x29, #-40]
    str x0, [sp, #-16]!
    movz w0, #0
    ldr x1, [sp], #16
    sxtw x0, w0
    cmp x1, x0
    cset w0, hi
    cbz w0, Lelse7
    movz w0, #44
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _putchar
Lelse7:
    sub x0, x29, #16
    add x0, x0, #8
    add x0, x0, #0
    ldr x0, [x0]
    str x0, [sp, #-16]!
    ldur x0, [x29, #-40]
    sxtw x0, w0
    ldr x1, [sp], #16
    mov x2, #16
    mul x0, x0, x2
    add x0, x1, x0
    mov x9, x0
    ldr x0, [x9]
    ldr x1, [x9, #8]
    str x1, [sp, #-16]!
    str x0, [sp, #-16]!
    ldur x0, [x29, #-24]
    str x0, [sp, #-16]!
    ldur x0, [x29, #-32]
    str x0, [sp, #-16]!
    ldr x3, [sp], #16
    ldr x2, [sp], #16
    ldr x0, [sp], #16
    ldr x1, [sp], #16
    bl _ntd_print
Lforupd5:
    ldur x0, [x29, #-40]
    mov x1, x0
    add x1, x1, #1
    stur x1, [x29, #-40]
    b Lfor4
Lforend6:
    movz w0, #93
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _putchar
    b Lifend3
Lelse2:
    adrp x0, Lstr9@PAGE
    add x0, x0, Lstr9@PAGEOFF
    str x0, [sp, #-16]!
    ldur x0, [x29, #-24]
    str x0, [sp, #-16]!
    sub x0, x29, #16
    add x0, x0, #8
    add x0, x0, #0
    ldr x0, [x0]
    sxtw x0, w0
    ldr x1, [sp], #16
    mov x2, #8
    mul x0, x0, x2
    add x0, x1, x0
    ldr x0, [x0]
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    ldur x0, [x29, #-32]
    str x0, [sp, #-16]!
    sub x0, x29, #16
    add x0, x0, #8
    add x0, x0, #0
    ldr x0, [x0]
    str x0, [sp, #-16]!
    movz w0, #32
    ldr x1, [sp], #16
    sxtw x0, w0
    udiv x0, x1, x0
    sxtw x0, w0
    ldr x1, [sp], #16
    mov x2, #4
    mul x0, x0, x2
    add x0, x1, x0
    ldr w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #1
    str x0, [sp, #-16]!
    sub x0, x29, #16
    add x0, x0, #8
    add x0, x0, #0
    ldr x0, [x0]
    str x0, [sp, #-16]!
    movz w0, #32
    ldr x1, [sp], #16
    sxtw x0, w0
    udiv x2, x1, x0
    msub x0, x2, x0, x1
    ldr x1, [sp], #16
    lslv x0, x1, x0
    ldr x1, [sp], #16
    orr w0, w1, w0
    str x0, [sp, #-16]!
    ldur x0, [x29, #-32]
    str x0, [sp, #-16]!
    sub x0, x29, #16
    add x0, x0, #8
    add x0, x0, #0
    ldr x0, [x0]
    str x0, [sp, #-16]!
    movz w0, #32
    ldr x1, [sp], #16
    sxtw x0, w0
    udiv x0, x1, x0
    sxtw x0, w0
    ldr x1, [sp], #16
    mov x2, #4
    mul x0, x0, x2
    add x0, x1, x0
    ldr x1, [sp], #16
    str w1, [x0]
    mov x0, x1
Lifend3:
    mov w0, #0
Lntd_print_return1:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .p2align 2
    .globl _main
_main:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #112
    stur w0, [x29, #-8]
    stur x1, [x29, #-16]
    stur xzr, [x29, #-32]
    stur xzr, [x29, #-24]
    movz w0, #16
    str x0, [sp, #-16]!
    movz w0, #16
    ldr x1, [sp], #16
    sdiv w0, w1, w0
    sub x9, x29, #32
    str x0, [x9]
    stur xzr, [x29, #-24]
    sub sp, sp, #16
    mov x9, sp
    sub sp, sp, #16
    mov x9, sp
    movz w0, #16
    str x0, [sp, #-16]!
    movz w0, #16
    ldr x1, [sp], #16
    sdiv w0, w1, w0
    str x0, [x9, #0]
    sub sp, sp, #16
    mov x9, sp
    sub sp, sp, #16
    mov x9, sp
    movz w0, #16
    str x0, [sp, #-16]!
    movz w0, #16
    ldr x1, [sp], #16
    sdiv w0, w1, w0
    str x0, [x9, #0]
    sub sp, sp, #16
    mov x9, sp
    sub sp, sp, #16
    mov x9, sp
    movz w0, #0
    str x0, [x9, #0]
    movz w0, #1
    str x0, [x9, #8]
    ldr x0, [x9]
    ldr x1, [x9, #8]
    add sp, sp, #16
    str x0, [x9, #0]
    sub sp, sp, #16
    mov x9, sp
    movz w0, #0
    str x0, [x9, #0]
    movz w0, #2
    str x0, [x9, #8]
    ldr x0, [x9]
    ldr x1, [x9, #8]
    add sp, sp, #16
    str x0, [x9, #8]
    ldr x0, [x9]
    ldr x1, [x9, #8]
    add sp, sp, #16
    str x0, [x9, #8]
    ldr x0, [x9]
    ldr x1, [x9, #8]
    add sp, sp, #16
    str x0, [x9, #0]
    sub sp, sp, #16
    mov x9, sp
    movz w0, #16
    str x0, [sp, #-16]!
    movz w0, #16
    ldr x1, [sp], #16
    sdiv w0, w1, w0
    str x0, [x9, #0]
    sub sp, sp, #16
    mov x9, sp
    sub sp, sp, #16
    mov x9, sp
    movz w0, #0
    str x0, [x9, #0]
    movz w0, #3
    str x0, [x9, #8]
    ldr x0, [x9]
    ldr x1, [x9, #8]
    add sp, sp, #16
    str x0, [x9, #0]
    sub sp, sp, #16
    mov x9, sp
    movz w0, #0
    str x0, [x9, #0]
    movz w0, #4
    str x0, [x9, #8]
    ldr x0, [x9]
    ldr x1, [x9, #8]
    add sp, sp, #16
    str x0, [x9, #8]
    ldr x0, [x9]
    ldr x1, [x9, #8]
    add sp, sp, #16
    str x0, [x9, #8]
    ldr x0, [x9]
    ldr x1, [x9, #8]
    add sp, sp, #16
    str x0, [x9, #8]
    ldr x0, [x9]
    ldr x1, [x9, #8]
    add sp, sp, #16
    str x0, [x9, #8]
    ldr x0, [x9]
    ldr x1, [x9, #8]
    add sp, sp, #16
    str x0, [x9, #0]
    ldr x0, [x9]
    ldr x1, [x9, #8]
    add sp, sp, #16
    sub x9, x29, #24
    str x0, [x9]
    adrp x0, Lstr11@PAGE
    add x0, x0, Lstr11@PAGEOFF
    sub x9, x29, #88
    str x0, [x9]
    adrp x0, Lstr12@PAGE
    add x0, x0, Lstr12@PAGEOFF
    sub x9, x29, #80
    str x0, [x9]
    adrp x0, Lstr13@PAGE
    add x0, x0, Lstr13@PAGEOFF
    sub x9, x29, #72
    str x0, [x9]
    adrp x0, Lstr14@PAGE
    add x0, x0, Lstr14@PAGEOFF
    sub x9, x29, #64
    str x0, [x9]
    adrp x0, Lstr15@PAGE
    add x0, x0, Lstr15@PAGEOFF
    sub x9, x29, #56
    str x0, [x9]
    adrp x0, Lstr16@PAGE
    add x0, x0, Lstr16@PAGEOFF
    sub x9, x29, #48
    str x0, [x9]
    adrp x0, Lstr17@PAGE
    add x0, x0, Lstr17@PAGEOFF
    sub x9, x29, #40
    str x0, [x9]
    movz w0, #0
    sub x9, x29, #96
    str w0, [x9]
    sub x0, x29, #32
    mov x9, x0
    ldr x0, [x9]
    ldr x1, [x9, #8]
    str x1, [sp, #-16]!
    str x0, [sp, #-16]!
    sub x0, x29, #88
    str x0, [sp, #-16]!
    sub x0, x29, #96
    str x0, [sp, #-16]!
    ldr x3, [sp], #16
    ldr x2, [sp], #16
    ldr x0, [sp], #16
    ldr x1, [sp], #16
    bl _ntd_print
    movz w0, #10
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _putchar
    movz w0, #0
    stur x0, [x29, #-104]
Lfor18:
    ldur x0, [x29, #-104]
    str x0, [sp, #-16]!
    movz w0, #56
    str x0, [sp, #-16]!
    movz w0, #8
    ldr x1, [sp], #16
    sdiv w0, w1, w0
    ldr x1, [sp], #16
    sxtw x0, w0
    cmp x1, x0
    cset w0, lo
    cbz w0, Lforend20
    sub x0, x29, #96
    str x0, [sp, #-16]!
    ldur x0, [x29, #-104]
    str x0, [sp, #-16]!
    movz w0, #32
    ldr x1, [sp], #16
    sxtw x0, w0
    udiv x0, x1, x0
    sxtw x0, w0
    ldr x1, [sp], #16
    mov x2, #4
    mul x0, x0, x2
    add x0, x1, x0
    ldr w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #1
    str x0, [sp, #-16]!
    ldur x0, [x29, #-104]
    str x0, [sp, #-16]!
    movz w0, #32
    ldr x1, [sp], #16
    sxtw x0, w0
    udiv x2, x1, x0
    msub x0, x2, x0, x1
    ldr x1, [sp], #16
    lslv x0, x1, x0
    ldr x1, [sp], #16
    and w0, w1, w0
    cmp w0, #0
    cset w0, eq
    cbz w0, Lelse21
    adrp x0, Lstr23@PAGE
    add x0, x0, Lstr23@PAGEOFF
    str x0, [sp, #-16]!
    sub x0, x29, #88
    str x0, [sp, #-16]!
    ldur x0, [x29, #-104]
    sxtw x0, w0
    ldr x1, [sp], #16
    mov x2, #8
    mul x0, x0, x2
    add x0, x1, x0
    ldr x0, [x0]
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
Lelse21:
Lforupd19:
    ldur x0, [x29, #-104]
    mov x1, x0
    add x1, x1, #1
    stur x1, [x29, #-104]
    b Lfor18
Lforend20:
    movz w0, #0
    b Lmain_return10
    mov w0, #0
Lmain_return10:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .data
    .p2align 2
Lstr9:
    .asciz "'%s'"
    .p2align 2
Lstr11:
    .asciz "Payload#0"
    .p2align 2
Lstr12:
    .asciz "Payload#1"
    .p2align 2
Lstr13:
    .asciz "Payload#2"
    .p2align 2
Lstr14:
    .asciz "Payload#3"
    .p2align 2
Lstr15:
    .asciz "Payload#4"
    .p2align 2
Lstr16:
    .asciz "Payload#5"
    .p2align 2
Lstr17:
    .asciz "Payload#6"
    .p2align 2
Lstr23:
    .asciz "'%s' unused\n"
