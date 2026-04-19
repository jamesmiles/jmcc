// TEST: func_type_typedef
// DESCRIPTION: typedef for a function type (not pointer) must work: typedef void fn(int); fn *p = &f;
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

struct EventLoop;
typedef void FileProc(struct EventLoop *loop, int fd, void *data, int mask);
typedef int TimeProc(struct EventLoop *loop, long long id, void *data);

static int called = 0;

static void my_handler(struct EventLoop *loop, int fd, void *data, int mask) {
    (void)loop; (void)fd; (void)data; (void)mask;
    called = 1;
}

int main(void) {
    FileProc *fp = my_handler;
    fp(0, 0, 0, 0);
    if (!called) return 1;
    printf("OK\n");
    return 0;
}
