    .text

    .globl count_neighbors
    .type count_neighbors, @function
count_neighbors:
    pushq %rbp
    movq %rsp, %rbp
    subq $64, %rsp
    movl %edi, -8(%rbp)
    movl %esi, -16(%rbp)
    xorl %eax, %eax
    movl %eax, -24(%rbp)
    movl $1, %eax
    negl %eax
    pushq %rax
    leaq -32(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
.for1:
    movl -32(%rbp), %eax
    pushq %rax
    movl $1, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setle %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .endfor3
    movl $1, %eax
    negl %eax
    pushq %rax
    leaq -40(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
.for4:
    movl -40(%rbp), %eax
    pushq %rax
    movl $1, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setle %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .endfor6
    movl -32(%rbp), %eax
    pushq %rax
    xorl %eax, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    sete %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .and_false9
    movl -40(%rbp), %eax
    pushq %rax
    xorl %eax, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    sete %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .and_false9
    movl $1, %eax
    jmp .and_end10
.and_false9:
    xorl %eax, %eax
.and_end10:
    cmpl $0, %eax
    je .endif8
    jmp .forupd5
.endif8:
    movl -8(%rbp), %eax
    pushq %rax
    movl -32(%rbp), %eax
    movl %eax, %ecx
    popq %rax
    addl %ecx, %eax
    movl %eax, -48(%rbp)
    movl -16(%rbp), %eax
    pushq %rax
    movl -40(%rbp), %eax
    movl %eax, %ecx
    popq %rax
    addl %ecx, %eax
    movl %eax, -56(%rbp)
    movl -48(%rbp), %eax
    pushq %rax
    xorl %eax, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setge %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .and_false17
    movl -48(%rbp), %eax
    pushq %rax
    movl $24, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setl %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .and_false17
    movl $1, %eax
    jmp .and_end18
.and_false17:
    xorl %eax, %eax
.and_end18:
    cmpl $0, %eax
    je .and_false15
    movl -56(%rbp), %eax
    pushq %rax
    xorl %eax, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setge %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .and_false15
    movl $1, %eax
    jmp .and_end16
.and_false15:
    xorl %eax, %eax
.and_end16:
    cmpl $0, %eax
    je .and_false13
    movl -56(%rbp), %eax
    pushq %rax
    movl $60, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setl %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .and_false13
    movl $1, %eax
    jmp .and_end14
.and_false13:
    xorl %eax, %eax
.and_end14:
    cmpl $0, %eax
    je .endif12
    leaq -24(%rbp), %rax
    pushq %rax
    movl (%rax), %eax
    pushq %rax
    leaq grid(%rip), %rax
    pushq %rax
    movl -48(%rbp), %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl -56(%rbp), %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movl (%rax), %eax
    movl %eax, %ecx
    popq %rax
    addl %ecx, %eax
    popq %rcx
    movl %eax, (%rcx)
.endif12:
.forupd5:
    leaq -40(%rbp), %rax
    pushq %rax
    movl (%rax), %eax
    movl %eax, %edx
    addl $1, %eax
    popq %rcx
    movl %eax, (%rcx)
    movl %edx, %eax
    jmp .for4
.endfor6:
.forupd2:
    leaq -32(%rbp), %rax
    pushq %rax
    movl (%rax), %eax
    movl %eax, %edx
    addl $1, %eax
    popq %rcx
    movl %eax, (%rcx)
    movl %edx, %eax
    jmp .for1
.endfor3:
    movl -24(%rbp), %eax
    leave
    ret
    leave
    ret

    .globl step
    .type step, @function
step:
    pushq %rbp
    movq %rsp, %rbp
    subq $32, %rsp
    xorl %eax, %eax
    pushq %rax
    leaq -8(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
.for19:
    movl -8(%rbp), %eax
    pushq %rax
    movl $24, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setl %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .endfor21
    xorl %eax, %eax
    pushq %rax
    leaq -16(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
.for22:
    movl -16(%rbp), %eax
    pushq %rax
    movl $60, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setl %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .endfor24
    movl -16(%rbp), %eax
    pushq %rax
    movl -8(%rbp), %eax
    pushq %rax
    popq %rdi
    popq %rsi
    movl $0, %eax
    call count_neighbors
    movl %eax, -24(%rbp)
    leaq grid(%rip), %rax
    pushq %rax
    movl -8(%rbp), %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl -16(%rbp), %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movl (%rax), %eax
    cmpl $0, %eax
    je .else25
    movl -24(%rbp), %eax
    pushq %rax
    movl $2, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    sete %al
    movzbl %al, %eax
    cmpl $0, %eax
    jne .or_true29
    movl -24(%rbp), %eax
    pushq %rax
    movl $3, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    sete %al
    movzbl %al, %eax
    cmpl $0, %eax
    jne .or_true29
    xorl %eax, %eax
    jmp .or_end30
.or_true29:
    movl $1, %eax
.or_end30:
    cmpl $0, %eax
    je .tern_f27
    movl $1, %eax
    jmp .tern_e28
.tern_f27:
    xorl %eax, %eax
.tern_e28:
    pushq %rax
    leaq next(%rip), %rax
    pushq %rax
    movl -8(%rbp), %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl -16(%rbp), %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
    jmp .endif26
.else25:
    movl -24(%rbp), %eax
    pushq %rax
    movl $3, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    sete %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .tern_f31
    movl $1, %eax
    jmp .tern_e32
.tern_f31:
    xorl %eax, %eax
.tern_e32:
    pushq %rax
    leaq next(%rip), %rax
    pushq %rax
    movl -8(%rbp), %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl -16(%rbp), %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
.endif26:
.forupd23:
    leaq -16(%rbp), %rax
    pushq %rax
    movl (%rax), %eax
    movl %eax, %edx
    addl $1, %eax
    popq %rcx
    movl %eax, (%rcx)
    movl %edx, %eax
    jmp .for22
.endfor24:
.forupd20:
    leaq -8(%rbp), %rax
    pushq %rax
    movl (%rax), %eax
    movl %eax, %edx
    addl $1, %eax
    popq %rcx
    movl %eax, (%rcx)
    movl %edx, %eax
    jmp .for19
.endfor21:
    xorl %eax, %eax
    pushq %rax
    leaq -8(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
.for33:
    movl -8(%rbp), %eax
    pushq %rax
    movl $24, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setl %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .endfor35
    xorl %eax, %eax
    pushq %rax
    leaq -16(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
.for36:
    movl -16(%rbp), %eax
    pushq %rax
    movl $60, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setl %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .endfor38
    leaq next(%rip), %rax
    pushq %rax
    movl -8(%rbp), %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl -16(%rbp), %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movl (%rax), %eax
    pushq %rax
    leaq grid(%rip), %rax
    pushq %rax
    movl -8(%rbp), %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl -16(%rbp), %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
.forupd37:
    leaq -16(%rbp), %rax
    pushq %rax
    movl (%rax), %eax
    movl %eax, %edx
    addl $1, %eax
    popq %rcx
    movl %eax, (%rcx)
    movl %edx, %eax
    jmp .for36
.endfor38:
.forupd34:
    leaq -8(%rbp), %rax
    pushq %rax
    movl (%rax), %eax
    movl %eax, %edx
    addl $1, %eax
    popq %rcx
    movl %eax, (%rcx)
    movl %edx, %eax
    jmp .for33
.endfor35:
    leave
    ret

    .globl print_grid
    .type print_grid, @function
print_grid:
    pushq %rbp
    movq %rsp, %rbp
    subq $32, %rsp
    movl %edi, -8(%rbp)
    leaq .str39(%rip), %rax
    pushq %rax
    popq %rdi
    movl $0, %eax
    call printf
    movl -8(%rbp), %eax
    pushq %rax
    leaq .str40(%rip), %rax
    pushq %rax
    popq %rdi
    popq %rsi
    movl $0, %eax
    call printf
    xorl %eax, %eax
    pushq %rax
    leaq -16(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
.for41:
    movl -16(%rbp), %eax
    pushq %rax
    movl $24, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setl %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .endfor43
    xorl %eax, %eax
    pushq %rax
    leaq -24(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
.for44:
    movl -24(%rbp), %eax
    pushq %rax
    movl $60, %eax
    movl %eax, %ecx
    popq %rax
    cmpl %ecx, %eax
    setl %al
    movzbl %al, %eax
    cmpl $0, %eax
    je .endfor46
    leaq grid(%rip), %rax
    pushq %rax
    movl -16(%rbp), %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl -24(%rbp), %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movl (%rax), %eax
    cmpl $0, %eax
    je .tern_f47
    movl $35, %eax
    jmp .tern_e48
.tern_f47:
    movl $46, %eax
.tern_e48:
    pushq %rax
    leaq .str49(%rip), %rax
    pushq %rax
    popq %rdi
    popq %rsi
    movl $0, %eax
    call printf
.forupd45:
    leaq -24(%rbp), %rax
    pushq %rax
    movl (%rax), %eax
    movl %eax, %edx
    addl $1, %eax
    popq %rcx
    movl %eax, (%rcx)
    movl %edx, %eax
    jmp .for44
.endfor46:
    leaq .str50(%rip), %rax
    pushq %rax
    popq %rdi
    movl $0, %eax
    call printf
.forupd42:
    leaq -16(%rbp), %rax
    pushq %rax
    movl (%rax), %eax
    movl %eax, %edx
    addl $1, %eax
    popq %rcx
    movl %eax, (%rcx)
    movl %edx, %eax
    jmp .for41
.endfor43:
    leave
    ret

    .globl main
    .type main, @function
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $16, %rsp
    movl $1, %eax
    pushq %rax
    leaq grid(%rip), %rax
    pushq %rax
    movl $1, %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl $2, %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
    movl $1, %eax
    pushq %rax
    leaq grid(%rip), %rax
    pushq %rax
    movl $2, %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl $3, %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
    movl $1, %eax
    pushq %rax
    leaq grid(%rip), %rax
    pushq %rax
    movl $3, %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl $1, %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
    movl $1, %eax
    pushq %rax
    leaq grid(%rip), %rax
    pushq %rax
    movl $3, %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl $2, %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
    movl $1, %eax
    pushq %rax
    leaq grid(%rip), %rax
    pushq %rax
    movl $3, %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl $3, %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
    movl $1, %eax
    pushq %rax
    leaq grid(%rip), %rax
    pushq %rax
    movl $10, %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl $30, %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
    movl $1, %eax
    pushq %rax
    leaq grid(%rip), %rax
    pushq %rax
    movl $10, %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl $31, %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
    movl $1, %eax
    pushq %rax
    leaq grid(%rip), %rax
    pushq %rax
    movl $11, %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl $29, %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
    movl $1, %eax
    pushq %rax
    leaq grid(%rip), %rax
    pushq %rax
    movl $11, %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl $30, %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
    movl $1, %eax
    pushq %rax
    leaq grid(%rip), %rax
    pushq %rax
    movl $12, %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl $30, %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
    movl $1, %eax
    pushq %rax
    leaq grid(%rip), %rax
    pushq %rax
    movl $18, %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl $10, %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
    movl $1, %eax
    pushq %rax
    leaq grid(%rip), %rax
    pushq %rax
    movl $18, %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl $11, %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
    movl $1, %eax
    pushq %rax
    leaq grid(%rip), %rax
    pushq %rax
    movl $18, %eax
    movslq %eax, %rax
    imulq $240, %rax
    popq %rcx
    addq %rcx, %rax
    pushq %rax
    movl $12, %eax
    movslq %eax, %rax
    imulq $4, %rax
    popq %rcx
    addq %rcx, %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
    leaq .str51(%rip), %rax
    pushq %rax
    popq %rdi
    movl $0, %eax
    call printf
    xorl %eax, %eax
    pushq %rax
    leaq -8(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    movl %eax, (%rcx)
.for52:
    movl -8(%rbp), %eax
    pushq %rax
    popq %rdi
    movl $0, %eax
    call print_grid
    movl $0, %eax
    call step
    movl $80000, %eax
    pushq %rax
    popq %rdi
    movl $0, %eax
    call usleep
.forupd53:
    leaq -8(%rbp), %rax
    pushq %rax
    movl (%rax), %eax
    movl %eax, %edx
    addl $1, %eax
    popq %rcx
    movl %eax, (%rcx)
    movl %edx, %eax
    jmp .for52
.endfor54:
    xorl %eax, %eax
    leave
    ret
    movl $0, %eax
    leave
    ret

    .bss
    .globl grid
    .align 4
grid:
    .zero 5760

    .bss
    .globl next
    .align 4
next:
    .zero 5760

    .section .rodata
.str39:
    .string "\033[H"
.str40:
    .string "Generation: %d\n"
.str49:
    .string "%c"
.str50:
    .string "\n"
.str51:
    .string "\033[2J"
