// TEST: array_basic
// DESCRIPTION: Array declaration, assignment, and indexing
// EXPECTED_EXIT: 30
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.5.2.1 (Array subscripting)

int main(void) {
    int arr[3];
    arr[0] = 10;
    arr[1] = 20;
    arr[2] = 30;
    return arr[2];
}
