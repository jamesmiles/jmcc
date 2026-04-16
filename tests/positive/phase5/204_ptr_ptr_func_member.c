// TEST: ptr_ptr_func_member
// DESCRIPTION: Pointer-to-pointer-to-function struct member must parse
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SQLite's auto-extension system declares:
     struct { u32 nExt; void (**aExt)(void); } sqlite3Autoext;
   aExt is: pointer to pointer to function-taking-void-returning-void.
   The declarator is  void (**name)(void)
   jmcc fails to parse the double-star declarator form. */

int printf(const char *fmt, ...);

void fa(void) {}
void fb(void) {}

struct ext_table {
    int n_funcs;
    void (**funcs)(void);    /* array of function pointers, accessed by ptr */
};

int main(void) {
    void (*table[2])(void) = { fa, fb };
    struct ext_table ext;
    ext.n_funcs = 2;
    ext.funcs = table;

    if (ext.n_funcs != 2) return 1;
    if (ext.funcs[0] != fa) return 2;
    if (ext.funcs[1] != fb) return 3;

    ext.funcs[0]();  /* should call fa, no-op */

    printf("ok\n");
    return 0;
}
