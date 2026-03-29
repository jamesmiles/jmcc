// TEST: nested_loops
// DESCRIPTION: Nested for loops
// EXPECTED_EXIT: 45
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.8.5.3 (The for statement)

int main(void) {
    int sum = 0;
    int i;
    int j;
    for (i = 0; i < 3; i = i + 1) {
        for (j = 0; j < 3; j = j + 1) {
            sum = sum + (i * 3 + j + 1);
        }
    }
    return sum;
}
