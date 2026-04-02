// TEST: global_char_ptr_string_init
// DESCRIPTION: Global char* initialized with string literal must not be NULL at runtime
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: hello
// STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's i_sound.c has: char* sndserver_filename = "./sndserver ";
   If global char* string initialization emits .bss/.zero instead of
   .data with the string address, the pointer is NULL at runtime and
   sprintf crashes with a segfault in I_InitSound. */

int printf(const char *fmt, ...);

char *msg = "hello";

int main(void) {
    if (msg == 0) return 1;
    printf("%s\n", msg);
    if (msg[0] != 'h') return 2;
    printf("ok\n");
    return 0;
}
