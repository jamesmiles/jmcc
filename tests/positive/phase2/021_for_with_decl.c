// TEST: for_with_decl
// DESCRIPTION: For loop with declaration in init (C99/C11)
// EXPECTED_EXIT: 10
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.8.5.3 (The for statement)

int main(void) {
    int sum = 0;
    for (int i = 0; i < 5; i = i + 1) {
        sum = sum + i;
    }
    return sum;
}
