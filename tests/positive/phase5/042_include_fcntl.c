// TEST: include_fcntl
// DESCRIPTION: #include <fcntl.h> for O_RDONLY/O_WRONLY (Doom's m_menu.c/m_misc.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: O_RDONLY=0
// STDOUT: O_WRONLY=1
// ENVIRONMENT: hosted
// PHASE: 5

#include <fcntl.h>

int printf(const char *fmt, ...);

int main(void) {
    printf("O_RDONLY=%d\n", O_RDONLY);
    printf("O_WRONLY=%d\n", O_WRONLY);
    return 0;
}
