// TEST: test_multidim
// DESCRIPTION: Multi-dimensional char array store and load
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
int main(void) {
    char arr[2][4];
    arr[1][3] = 42;
    if (arr[1][3] != 42) return 1;
    return 0;
}
