// TEST: for_loop
// DESCRIPTION: For loop summing 1 to 10
// EXPECTED_EXIT: 55
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.8.5.3 (The for statement)

int main(void) {
    int sum = 0;
    int i;
    for (i = 1; i <= 10; i = i + 1) {
        sum = sum + i;
    }
    return sum;
}
