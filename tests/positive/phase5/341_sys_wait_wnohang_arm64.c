/* Test: sys/wait.h must provide WNOHANG and waitpid on arm64-apple-darwin
 * Mirrors textscreen/txt_fileselect.c: #include <sys/wait.h> then
 * waitpid(pid, &status, WNOHANG)
 * clang: accepts, jmcc arm64: "undefined variable 'WNOHANG'"
 */
#include <sys/wait.h>

int check_child(int pid) {
    int status = 0;
    return waitpid(pid, &status, WNOHANG);
}

int main(void) {
    return 0;
}
