// TEST: func_returning_func_ptr
// DESCRIPTION: Function returning function pointer declarator must parse
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SQLite's sqlite3_vfs struct has:
     void (*(*xDlSym)(sqlite3_vfs*, void*, const char *z))(void);
   This is a function pointer member where the function returns
   a function pointer. The declarator structure is:
     void (* (*name)(params1) )(params2)
        ^      ^              ^    ^
        |      func ptr       |    returned func takes (void)
        returned func returns void + takes params1

   jmcc fails to parse this. Used in SQLite's VFS interface. */

int printf(const char *fmt, ...);

/* Callable function */
void cb(void) {}

/* Function returning function pointer */
void (*get_cb(int x))(void) {
    (void)x;
    return cb;
}

/* Struct member: function pointer returning function pointer */
struct vfs {
    int size;
    void (*(*xDlSym)(struct vfs*, void*, const char *z))(void);
};

/* Helper that matches xDlSym's signature */
void (*my_dlsym(struct vfs *v, void *h, const char *z))(void) {
    (void)v; (void)h; (void)z;
    return cb;
}

int main(void) {
    /* Test 1: function-returning-fp call */
    void (*fp)(void) = get_cb(42);
    if (fp == 0) return 1;
    fp();  /* calls cb — no-op, no crash */

    /* Test 2: struct with func-returning-fp member */
    struct vfs v;
    v.size = 100;
    v.xDlSym = my_dlsym;

    void (*result)(void) = v.xDlSym(&v, 0, "test");
    if (result != cb) return 2;

    printf("ok\n");
    return 0;
}
