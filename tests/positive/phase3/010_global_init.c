// TEST: global_init
// DESCRIPTION: Global variable with initializer, modified in function
// EXPECTED_EXIT: 15
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.7.9 (Initialization)

int counter = 10;

void increment(int n) {
    counter = counter + n;
}

int main(void) {
    increment(5);
    return counter;
}
