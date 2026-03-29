// TEST: do_while
// DESCRIPTION: Do-while loop
// EXPECTED_EXIT: 10
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.8.5.2 (The do statement)

int main(void) {
    int x = 0;
    do {
        x = x + 2;
    } while (x < 10);
    return x;
}
