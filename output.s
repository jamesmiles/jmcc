    .text

    .p2align 2
    .globl _main
_main:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #32
    movz w0, #1
    stur w0, [x29, #-8]
    adrp x0, Lstr2@PAGE
    add x0, x0, Lstr2@PAGEOFF
    sturb w0, [x29, #-16]
    sub x0, x29, #16
    str x0, [sp, #-16]!
    movz w0, #0
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #88
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse3
    adrp x0, Lstr5@PAGE
    add x0, x0, Lstr5@PAGEOFF
    str x0, [sp, #-16]!
    sub x0, x29, #16
    str x0, [sp, #-16]!
    movz w0, #0
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    stur w0, [x29, #-8]
Lelse3:
    sub x0, x29, #16
    str x0, [sp, #-16]!
    movz w0, #1
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #0
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse6
    adrp x0, Lstr8@PAGE
    add x0, x0, Lstr8@PAGEOFF
    str x0, [sp, #-16]!
    sub x0, x29, #16
    str x0, [sp, #-16]!
    movz w0, #1
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    and w0, w0, #0xff
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    stur w0, [x29, #-8]
Lelse6:
    sub x0, x29, #16
    str x0, [sp, #-16]!
    movz w0, #2
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #89
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse9
    adrp x0, Lstr11@PAGE
    add x0, x0, Lstr11@PAGEOFF
    str x0, [sp, #-16]!
    sub x0, x29, #16
    str x0, [sp, #-16]!
    movz w0, #2
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    stur w0, [x29, #-8]
Lelse9:
    sub x0, x29, #16
    str x0, [sp, #-16]!
    movz w0, #3
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #0
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse12
    adrp x0, Lstr14@PAGE
    add x0, x0, Lstr14@PAGEOFF
    str x0, [sp, #-16]!
    sub x0, x29, #16
    str x0, [sp, #-16]!
    movz w0, #3
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    and w0, w0, #0xff
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    stur w0, [x29, #-8]
Lelse12:
    adrp x0, Lstr15@PAGE
    add x0, x0, Lstr15@PAGEOFF
    sturb w0, [x29, #-24]
    sub x0, x29, #24
    str x0, [sp, #-16]!
    movz w0, #0
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #10
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse16
    adrp x0, Lstr18@PAGE
    add x0, x0, Lstr18@PAGEOFF
    str x0, [sp, #-16]!
    sub x0, x29, #24
    str x0, [sp, #-16]!
    movz w0, #0
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    and w0, w0, #0xff
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    stur w0, [x29, #-8]
Lelse16:
    sub x0, x29, #24
    str x0, [sp, #-16]!
    movz w0, #1
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #0
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse19
    adrp x0, Lstr21@PAGE
    add x0, x0, Lstr21@PAGEOFF
    str x0, [sp, #-16]!
    sub x0, x29, #24
    str x0, [sp, #-16]!
    movz w0, #1
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    and w0, w0, #0xff
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    stur w0, [x29, #-8]
Lelse19:
    adrp x0, Lstr22@PAGE
    add x0, x0, Lstr22@PAGEOFF
    sturb w0, [x29, #-32]
    sub x0, x29, #32
    str x0, [sp, #-16]!
    movz w0, #0
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #65
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse23
    adrp x0, Lstr25@PAGE
    add x0, x0, Lstr25@PAGEOFF
    str x0, [sp, #-16]!
    sub x0, x29, #32
    str x0, [sp, #-16]!
    movz w0, #0
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    stur w0, [x29, #-8]
Lelse23:
    sub x0, x29, #32
    str x0, [sp, #-16]!
    movz w0, #1
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #0
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse26
    adrp x0, Lstr28@PAGE
    add x0, x0, Lstr28@PAGEOFF
    str x0, [sp, #-16]!
    sub x0, x29, #32
    str x0, [sp, #-16]!
    movz w0, #1
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    and w0, w0, #0xff
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    stur w0, [x29, #-8]
Lelse26:
    adrp x0, Lstatic_main_zAff@PAGE
    add x0, x0, Lstatic_main_zAff@PAGEOFF
    str x0, [sp, #-16]!
    movz w0, #0
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #66
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse29
    adrp x0, Lstr31@PAGE
    add x0, x0, Lstr31@PAGEOFF
    str x0, [sp, #-16]!
    adrp x0, Lstatic_main_zAff@PAGE
    add x0, x0, Lstatic_main_zAff@PAGEOFF
    str x0, [sp, #-16]!
    movz w0, #0
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    stur w0, [x29, #-8]
Lelse29:
    adrp x0, Lstatic_main_zAff@PAGE
    add x0, x0, Lstatic_main_zAff@PAGEOFF
    str x0, [sp, #-16]!
    movz w0, #1
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #0
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse32
    adrp x0, Lstr34@PAGE
    add x0, x0, Lstr34@PAGEOFF
    str x0, [sp, #-16]!
    adrp x0, Lstatic_main_zAff@PAGE
    add x0, x0, Lstatic_main_zAff@PAGEOFF
    str x0, [sp, #-16]!
    movz w0, #1
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    and w0, w0, #0xff
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    stur w0, [x29, #-8]
Lelse32:
    adrp x0, Lstatic_main_zAff@PAGE
    add x0, x0, Lstatic_main_zAff@PAGEOFF
    str x0, [sp, #-16]!
    movz w0, #2
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #67
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse35
    adrp x0, Lstr37@PAGE
    add x0, x0, Lstr37@PAGEOFF
    str x0, [sp, #-16]!
    adrp x0, Lstatic_main_zAff@PAGE
    add x0, x0, Lstatic_main_zAff@PAGEOFF
    str x0, [sp, #-16]!
    movz w0, #2
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    stur w0, [x29, #-8]
Lelse35:
    adrp x0, Lstatic_main_zAff@PAGE
    add x0, x0, Lstatic_main_zAff@PAGEOFF
    str x0, [sp, #-16]!
    movz w0, #4
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #68
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse38
    adrp x0, Lstr40@PAGE
    add x0, x0, Lstr40@PAGEOFF
    str x0, [sp, #-16]!
    adrp x0, Lstatic_main_zAff@PAGE
    add x0, x0, Lstatic_main_zAff@PAGEOFF
    str x0, [sp, #-16]!
    movz w0, #4
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    stur w0, [x29, #-8]
Lelse38:
    adrp x0, Lstatic_main_zAff@PAGE
    add x0, x0, Lstatic_main_zAff@PAGEOFF
    str x0, [sp, #-16]!
    movz w0, #6
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    movz w0, #69
    ldr x1, [sp], #16
    cmp w1, w0
    cset w0, ne
    cbz w0, Lelse41
    adrp x0, Lstr43@PAGE
    add x0, x0, Lstr43@PAGEOFF
    str x0, [sp, #-16]!
    adrp x0, Lstatic_main_zAff@PAGE
    add x0, x0, Lstatic_main_zAff@PAGEOFF
    str x0, [sp, #-16]!
    movz w0, #6
    sxtw x0, w0
    ldr x1, [sp], #16
    add x0, x1, x0
    ldrb w0, [x0]
    str x0, [sp, #-16]!
    mov x10, sp
    sub sp, sp, #16
    ldr x9, [x10, #0]
    str x9, [sp, #0]
    ldr x0, [x10, #16]
    bl _printf
    add sp, sp, #48
    movz w0, #0
    stur w0, [x29, #-8]
Lelse41:
    ldur w0, [x29, #-8]
    cbz w0, Lelse44
    adrp x0, Lstr46@PAGE
    add x0, x0, Lstr46@PAGEOFF
    str x0, [sp, #-16]!
    ldr x0, [sp], #16
    bl _printf
Lelse44:
    ldur w0, [x29, #-8]
    cbz w0, Lternfalse47
    movz w0, #0
    b Lternend48
Lternfalse47:
    movz w0, #1
Lternend48:
    b Lmain_return1
    mov w0, #0
Lmain_return1:
    add sp, sp, #32
    ldp x29, x30, [sp], #16
    ret

    .data
    .p2align 2
Lstatic_main_zAff:
    .asciz "B C D E F"

    .data
    .p2align 2
Lstr2:
    .asciz "X Y"
    .p2align 2
Lstr5:
    .asciz "FAIL a[0]='%c'\n"
    .p2align 2
Lstr8:
    .asciz "FAIL a[1]=0x%02x not NUL\n"
    .p2align 2
Lstr11:
    .asciz "FAIL a[2]='%c' expected 'Y'\n"
    .p2align 2
Lstr14:
    .asciz "FAIL a[3]=0x%02x not NUL\n"
    .p2align 2
Lstr15:
    .asciz "\n"
    .p2align 2
Lstr18:
    .asciz "FAIL b[0]=0x%02x expected 0x0a\n"
    .p2align 2
Lstr21:
    .asciz "FAIL b[1]=0x%02x not NUL\n"
    .p2align 2
Lstr22:
    .asciz "A"
    .p2align 2
Lstr25:
    .asciz "FAIL c[0]='%c' expected 'A'\n"
    .p2align 2
Lstr28:
    .asciz "FAIL c[1]=0x%02x not NUL\n"
    .p2align 2
Lstr31:
    .asciz "FAIL zAff[0]='%c'\n"
    .p2align 2
Lstr34:
    .asciz "FAIL zAff[1]=0x%02x not NUL\n"
    .p2align 2
Lstr37:
    .asciz "FAIL zAff[2]='%c' expected 'C'\n"
    .p2align 2
Lstr40:
    .asciz "FAIL zAff[4]='%c' expected 'D'\n"
    .p2align 2
Lstr43:
    .asciz "FAIL zAff[6]='%c' expected 'E'\n"
    .p2align 2
Lstr46:
    .asciz "ok\n"
