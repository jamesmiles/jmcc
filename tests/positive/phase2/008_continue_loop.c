// TEST: continue_loop
// DESCRIPTION: Continue statement in a for loop (sum odd numbers 1-10)
// EXPECTED_EXIT: 25
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.8.6.2 (The continue statement)

int main(void) {
    int sum = 0;
    int i;
    for (i = 1; i <= 10; i = i + 1) {
        if (i % 2 == 0)
            continue;
        sum = sum + i;
    }
    return sum;
}
