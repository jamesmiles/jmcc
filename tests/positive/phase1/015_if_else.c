// TEST: if_else
// DESCRIPTION: If-else statement
// EXPECTED_EXIT: 2
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.8.4.1 (The if statement)

int main(void) {
    int x = 0;
    if (x)
        return 1;
    else
        return 2;
}
