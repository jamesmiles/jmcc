// TEST: global_array
// DESCRIPTION: Global array variable
// EXPECTED_EXIT: 15
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.7.9 (Initialization)

int arr[5];

int main(void) {
    int i;
    for (i = 0; i < 5; i = i + 1) {
        arr[i] = i + 1;
    }
    int sum = 0;
    for (i = 0; i < 5; i = i + 1) {
        sum = sum + arr[i];
    }
    return sum;
}
