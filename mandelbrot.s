    .text

    .globl main
    .type main, @function
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $224, %rsp
    movl %edi, -8(%rbp)
    movq %rsi, -16(%rbp)
    movl -8(%rbp), %eax
    pushq %rax
    movl $8, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setne %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .endif2
    movq -16(%rbp), %rax
    pushq %rax
    xorl %eax, %eax
    movslq %eax, %rax
    imulq $8, %rax
    popq %rcx
    addq %rcx, %rax
    movq (%rax), %rax
    pushq %rax
    leaq .str3(%rip), %rax
    pushq %rax
    popq %rdi
    popq %rsi
    movl $0, %eax
    call printf
    movq -16(%rbp), %rax
    pushq %rax
    xorl %eax, %eax
    movslq %eax, %rax
    imulq $8, %rax
    popq %rcx
    addq %rcx, %rax
    movq (%rax), %rax
    pushq %rax
    leaq .str4(%rip), %rax
    pushq %rax
    popq %rdi
    popq %rsi
    movl $0, %eax
    call printf
    movl $1, %eax
    pushq %rax
    popq %rdi
    movl $0, %eax
    call exit
.endif2:
    movq -16(%rbp), %rax
    pushq %rax
    movl $1, %eax
    movslq %eax, %rax
    imulq $8, %rax
    popq %rcx
    addq %rcx, %rax
    movq (%rax), %rax
    pushq %rax
    popq %rdi
    movl $0, %eax
    call atof
    movq %xmm0, %rax
    movq %rax, -24(%rbp)
    movq -16(%rbp), %rax
    pushq %rax
    movl $2, %eax
    movslq %eax, %rax
    imulq $8, %rax
    popq %rcx
    addq %rcx, %rax
    movq (%rax), %rax
    pushq %rax
    popq %rdi
    movl $0, %eax
    call atof
    movq %xmm0, %rax
    movq %rax, -32(%rbp)
    movq -16(%rbp), %rax
    pushq %rax
    movl $3, %eax
    movslq %eax, %rax
    imulq $8, %rax
    popq %rcx
    addq %rcx, %rax
    movq (%rax), %rax
    pushq %rax
    popq %rdi
    movl $0, %eax
    call atof
    movq %xmm0, %rax
    movq %rax, -40(%rbp)
    movq -16(%rbp), %rax
    pushq %rax
    movl $4, %eax
    movslq %eax, %rax
    imulq $8, %rax
    popq %rcx
    addq %rcx, %rax
    movq (%rax), %rax
    pushq %rax
    popq %rdi
    movl $0, %eax
    call atof
    movq %xmm0, %rax
    movq %rax, -48(%rbp)
    movq -16(%rbp), %rax
    pushq %rax
    movl $5, %eax
    movslq %eax, %rax
    imulq $8, %rax
    popq %rcx
    addq %rcx, %rax
    movq (%rax), %rax
    pushq %rax
    popq %rdi
    movl $0, %eax
    call atoi
    movl %eax, -56(%rbp)
    movq -16(%rbp), %rax
    pushq %rax
    movl $6, %eax
    movslq %eax, %rax
    imulq $8, %rax
    popq %rcx
    addq %rcx, %rax
    movq (%rax), %rax
    pushq %rax
    popq %rdi
    movl $0, %eax
    call atoi
    movl %eax, -64(%rbp)
    movl -64(%rbp), %eax
    cvtsi2sd %eax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -48(%rbp), %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -40(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    subsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    mulsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -32(%rbp), %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -24(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    subsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    divsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, %xmm0
    cvttsd2si %xmm0, %eax
    movl %eax, -72(%rbp)
    movq -16(%rbp), %rax
    pushq %rax
    movl $7, %eax
    movslq %eax, %rax
    imulq $8, %rax
    popq %rcx
    addq %rcx, %rax
    movq (%rax), %rax
    movq %rax, -80(%rbp)
    leaq .str5(%rip), %rax
    pushq %rax
    movq -80(%rbp), %rax
    pushq %rax
    popq %rdi
    popq %rsi
    movl $0, %eax
    call fopen
    movq %rax, -88(%rbp)
    leaq .str6(%rip), %rax
    movq %rax, -96(%rbp)
    movl -56(%rbp), %eax
    pushq %rax
    movl $256, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setl %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .tern_f7
    movl $256, %eax
    jmp .tern_e8
.tern_f7:
    movl -56(%rbp), %eax
.tern_e8:
    pushq %rax
    movl -72(%rbp), %eax
    pushq %rax
    movl -64(%rbp), %eax
    pushq %rax
    movl -56(%rbp), %eax
    pushq %rax
    movq -48(%rbp), %rax
    pushq %rax
    movq -40(%rbp), %rax
    pushq %rax
    movq -32(%rbp), %rax
    pushq %rax
    movq -24(%rbp), %rax
    pushq %rax
    leaq .str9(%rip), %rax
    pushq %rax
    movq -88(%rbp), %rax
    pushq %rax
    popq %rdi
    popq %rsi
    popq %rax
    movq %rax, %xmm0
    popq %rax
    movq %rax, %xmm1
    popq %rax
    movq %rax, %xmm2
    popq %rax
    movq %rax, %xmm3
    popq %rdx
    popq %rcx
    popq %r8
    popq %r9
    movl $4, %eax
    call fprintf
    movq -32(%rbp), %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -24(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    subsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movl -64(%rbp), %eax
    cvtsi2sd %eax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    divsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, -104(%rbp)
    movq -48(%rbp), %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -40(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    subsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movl -72(%rbp), %eax
    cvtsi2sd %eax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    divsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, -112(%rbp)
    xorl %eax, %eax
    pushq %rax
    leaq -160(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
.for10:
    movl -160(%rbp), %eax
    pushq %rax
    movl -72(%rbp), %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setl %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .endfor12
    movq -48(%rbp), %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movl -160(%rbp), %eax
    cvtsi2sd %eax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -112(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    mulsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    subsd %xmm1, %xmm0
    movq %xmm0, %rax
    pushq %rax
    leaq -128(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movq %rax, (%rcx)
    xorl %eax, %eax
    pushq %rax
    leaq -152(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
.for13:
    movl -152(%rbp), %eax
    pushq %rax
    movl -64(%rbp), %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setl %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .endfor15
    movsd .flt16(%rip), %xmm0
    movq %xmm0, %rax
    movq %rax, -176(%rbp)
    movsd .flt17(%rip), %xmm0
    movq %xmm0, %rax
    movq %rax, -184(%rbp)
    movq -176(%rbp), %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -176(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    mulsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, -192(%rbp)
    movq -184(%rbp), %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -184(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    mulsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, -200(%rbp)
    movq -24(%rbp), %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movl -152(%rbp), %eax
    cvtsi2sd %eax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -104(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    mulsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    addsd %xmm1, %xmm0
    movq %xmm0, %rax
    pushq %rax
    leaq -120(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movq %rax, (%rcx)
    movl $1, %eax
    pushq %rax
    leaq -168(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
.for18:
    movl -168(%rbp), %eax
    pushq %rax
    movl -56(%rbp), %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setl %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .and_false21
    movq -192(%rbp), %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -200(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    addsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movsd .flt23(%rip), %xmm0
    movq %xmm0, %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    ucomisd %xmm1, %xmm0
    setb %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .and_false21
    movl $1, %eax
    jmp .and_end22
.and_false21:
    xorl %eax, %eax
.and_end22:
    cmpl $0, %eax
    je .endfor20
    movl $2, %eax
    cvtsi2sd %eax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -176(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    mulsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -184(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    mulsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -128(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    addsd %xmm1, %xmm0
    movq %xmm0, %rax
    pushq %rax
    leaq -184(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movq %rax, (%rcx)
    movq -192(%rbp), %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -200(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    subsd %xmm1, %xmm0
    movq %xmm0, %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -120(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    addsd %xmm1, %xmm0
    movq %xmm0, %rax
    pushq %rax
    leaq -176(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movq %rax, (%rcx)
    movq -176(%rbp), %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -176(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    mulsd %xmm1, %xmm0
    movq %xmm0, %rax
    pushq %rax
    leaq -192(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movq %rax, (%rcx)
    movq -184(%rbp), %rax
    movq %rax, %xmm0
    subq $8, %rsp
    movsd %xmm0, (%rsp)
    movq -184(%rbp), %rax
    movq %rax, %xmm1
    movsd (%rsp), %xmm0
    addq $8, %rsp
    mulsd %xmm1, %xmm0
    movq %xmm0, %rax
    pushq %rax
    leaq -200(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movq %rax, (%rcx)
.forupd19:
    leaq -168(%rbp), %rax
    pushq %rax
    movl (%rax), %eax
    movl %eax, %edx
    addl $1, %eax
    popq %rcx
    movl %eax, (%rcx)
    movl %edx, %eax
    jmp .for18
.endfor20:
    movl -168(%rbp), %eax
    pushq %rax
    movl -56(%rbp), %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setge %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .else24
    xorl %eax, %eax
    movb %al, -208(%rbp)
    xorl %eax, %eax
    movb %al, -207(%rbp)
    xorl %eax, %eax
    movb %al, -206(%rbp)
    xorl %eax, %eax
    movb %al, -205(%rbp)
    xorl %eax, %eax
    movb %al, -204(%rbp)
    xorl %eax, %eax
    movb %al, -203(%rbp)
    movq -88(%rbp), %rax
    pushq %rax
    movl $1, %eax
    pushq %rax
    movl $6, %eax
    pushq %rax
    leaq -208(%rbp), %rax
    pushq %rax
    popq %rdi
    popq %rsi
    popq %rdx
    popq %rcx
    movl $0, %eax
    call fwrite
    jmp .endif25
.else24:
    movl -168(%rbp), %eax
    pushq %rax
    movl $8, %eax
    movl %eax, %ecx
    popq %rax
    sarl %cl, %eax
    pushq %rax
    leaq -216(%rbp), %rax
    pushq %rax
    xorl %eax, %eax
    movslq %eax, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movb %al, (%rcx)
    movl -168(%rbp), %eax
    pushq %rax
    movl $255, %eax
    movl %eax, %ecx
    popq %rax
    andl %ecx, %eax
    pushq %rax
    leaq -216(%rbp), %rax
    pushq %rax
    movl $1, %eax
    movslq %eax, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movb %al, (%rcx)
    movl -168(%rbp), %eax
    pushq %rax
    movl $8, %eax
    movl %eax, %ecx
    popq %rax
    sarl %cl, %eax
    pushq %rax
    leaq -216(%rbp), %rax
    pushq %rax
    movl $2, %eax
    movslq %eax, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movb %al, (%rcx)
    movl -168(%rbp), %eax
    pushq %rax
    movl $255, %eax
    movl %eax, %ecx
    popq %rax
    andl %ecx, %eax
    pushq %rax
    leaq -216(%rbp), %rax
    pushq %rax
    movl $3, %eax
    movslq %eax, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movb %al, (%rcx)
    movl -168(%rbp), %eax
    pushq %rax
    movl $8, %eax
    movl %eax, %ecx
    popq %rax
    sarl %cl, %eax
    pushq %rax
    leaq -216(%rbp), %rax
    pushq %rax
    movl $4, %eax
    movslq %eax, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movb %al, (%rcx)
    movl -168(%rbp), %eax
    pushq %rax
    movl $255, %eax
    movl %eax, %ecx
    popq %rax
    andl %ecx, %eax
    pushq %rax
    leaq -216(%rbp), %rax
    pushq %rax
    movl $5, %eax
    movslq %eax, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movb %al, (%rcx)
    movq -88(%rbp), %rax
    pushq %rax
    movl $1, %eax
    pushq %rax
    movl $6, %eax
    pushq %rax
    leaq -216(%rbp), %rax
    pushq %rax
    popq %rdi
    popq %rsi
    popq %rdx
    popq %rcx
    movl $0, %eax
    call fwrite
.endif25:
.forupd14:
    leaq -152(%rbp), %rax
    pushq %rax
    movl (%rax), %eax
    movl %eax, %edx
    addl $1, %eax
    popq %rcx
    movl %eax, (%rcx)
    movl %edx, %eax
    jmp .for13
.endfor15:
.forupd11:
    leaq -160(%rbp), %rax
    pushq %rax
    movl (%rax), %eax
    movl %eax, %edx
    addl $1, %eax
    popq %rcx
    movl %eax, (%rcx)
    movl %edx, %eax
    jmp .for10
.endfor12:
    movq -88(%rbp), %rax
    pushq %rax
    popq %rdi
    movl $0, %eax
    call fclose
    xorl %eax, %eax
    leave
    ret
    movl $0, %eax
    leave
    ret
    .align 8
.flt16:
    .quad 0
    .align 8
.flt17:
    .quad 0
    .align 8
.flt23:
    .quad 4616189618054758400

    .section .rodata
.str3:
    .string "Usage:   %s <xmin> <xmax> <ymin> <ymax> <maxiter> <xres> <out.ppm>\n"
.str4:
    .string "Example: %s 0.27085 0.27100 0.004640 0.004810 1000 1024 pic.ppm\n"
.str5:
    .string "wb"
.str6:
    .string "# Mandelbrot set"
.str9:
    .string "P6\n# Mandelbrot, xmin=%lf, xmax=%lf, ymin=%lf, ymax=%lf, maxiter=%d\n%d\n%d\n%d\n"
