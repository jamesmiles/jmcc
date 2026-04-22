    .text

    .p2align 2
    .globl _main
_main:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #16
    movz w0, #1
    cbz w0, Lelse2
    movz w0, #1
    stur w0, [x29, #-8]
    b Lifend3
Lelse2:
    movz w0, #1
    cbz w0, Lelse4
    adrp x9, Lfpconst6@PAGE
    ldr s0, [x9, Lfpconst6@PAGEOFF]
    fcvt d0, s0
    stur w0, [x29, #-8]
    ldur w0, [x29, #-8]
    mov w0, w0
    b Lmain_return1
Lelse4:
Lifend3:
    movz w0, #0
    b Lmain_return1
    mov w0, #0
Lmain_return1:
    mov sp, x29
    ldp x29, x30, [sp], #16
    ret

    .section __TEXT,__literal4,4byte_literals
    .p2align 2
Lfpconst6:
    .long 1073741824
