// TEST: cast_func_ptr_ptr_return
// DESCRIPTION: Cast to function pointer where return type is a pointer type
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SQLite casts the mmap syscall pointer:
     ((void*(*)(void*,size_t,int,int,int,off_t))aSyscall[22].pCurrent)(...)
   Return type is void*. jmcc handles (uid_t(*)(void)) (test 202) but
   fails when the return type is a POINTER type like void*. */

int printf(const char *fmt, ...);

void *get_null(void) { return (void *)0; }
char *get_string(void) { return "hello"; }

int main(void) {
    /* Test 1: void* return in cast */
    void *p = (void *)get_null;
    void *r1 = ((void*(*)(void))p)();
    if (r1 != (void *)0) return 1;

    /* Test 2: char* return */
    void *p2 = (void *)get_string;
    char *r2 = ((char*(*)(void))p2)();
    if (r2[0] != 'h') return 2;

    /* Test 3: void* return with params */
    void *p3 = (void *)get_null;
    void *r3 = ((void*(*)(int, int))p3)(0, 0);
    if (r3 != (void *)0) return 3;

    printf("ok\n");
    return 0;
}
