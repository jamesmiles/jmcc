// TEST: func_pointer_array
// DESCRIPTION: Function pointer dispatch table (Doom action array pattern)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: action 0
// STDOUT: action 1
// STDOUT: action 2
// STDOUT: action 3
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

void fn0(int x) { printf("action %d\n", x); }
void fn1(int x) { printf("action %d\n", x); }
void fn2(int x) { printf("action %d\n", x); }
void fn3(int x) { printf("action %d\n", x); }

int main(void) {
    void (*actions[4])(int) = {fn0, fn1, fn2, fn3};
    int i;
    for (i = 0; i < 4; i++) {
        actions[i](i);
    }
    return 0;
}
