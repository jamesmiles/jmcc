// TEST: while_loop
// DESCRIPTION: While loop summing 1 to 5
// EXPECTED_EXIT: 15
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.8.5.1 (The while statement)

int main(void) {
    int sum = 0;
    int i = 1;
    while (i <= 5) {
        sum = sum + i;
        i = i + 1;
    }
    return sum;
}
