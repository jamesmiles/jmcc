// TEST: break_loop
// DESCRIPTION: Break statement in a while loop
// EXPECTED_EXIT: 5
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.8.6.3 (The break statement)

int main(void) {
    int i = 0;
    while (1) {
        if (i == 5)
            break;
        i = i + 1;
    }
    return i;
}
