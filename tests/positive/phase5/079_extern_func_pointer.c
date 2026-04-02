// TEST: extern_func_pointer
// DESCRIPTION: extern function pointer must not allocate storage (Doom's colfunc linker error)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: called
// ENVIRONMENT: hosted
// PHASE: 5
// MULTI_FILE: helpers/079_helper.c
// NOTE: Requires multi-file compilation. Tests that extern function pointer
//       declarations don't emit .bss storage, which causes duplicate symbol
//       errors at link time. This blocks Doom from linking (4 symbols).

int printf(const char *fmt, ...);

extern void (*colfunc)(void);

void my_col(void) {
    printf("called\n");
}

int main(void) {
    colfunc = my_col;
    colfunc();
    return 0;
}
