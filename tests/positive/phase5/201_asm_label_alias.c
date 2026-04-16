// TEST: asm_label_alias
// DESCRIPTION: __asm__("name") label aliases on function declarations must be accepted
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* glibc uses __asm__ label aliases to switch between symbol names
   at the linker level. Example from sys/mman.h for 32/64-bit off_t:
     extern void *mmap(void *addr, size_t len, int prot, int flags,
                       int fd, __off64_t offset)
         __asm__("mmap64") __attribute__((__nothrow__));

   jmcc already handles __asm__ statements (test 172) and the
   __attribute__ suffix (test 165). But the combined pattern of
   __asm__("label") between the parameter list and __attribute__
   isn't recognized — jmcc complains "expected ';', got '__asm__'".

   Appears in SQLite (blocker at line 42404 after preprocessing),
   and in virtually any program that includes <sys/mman.h>. */

int printf(const char *fmt, ...);

/* Function declaration with asm label (semantically: this symbol
   links to "my_real_name" at link time) */
extern int my_func(int x) __asm__("my_func");

/* With __attribute__ too */
extern int tagged_func(int x) __asm__("tagged_func") __attribute__((__nothrow__));

int my_func(int x) { return x * 2; }
int tagged_func(int x) { return x + 10; }

int main(void) {
    if (my_func(21) != 42) return 1;
    if (tagged_func(5) != 15) return 2;

    printf("ok\n");
    return 0;
}
