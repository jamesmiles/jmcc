// TEST: array_pointer_decay
// DESCRIPTION: Array decays to pointer when passed to function
// EXPECTED_EXIT: 15
// ENVIRONMENT: hosted
// PHASE: 3

int sum(int *arr, int n) {
    int total = 0;
    int i;
    for (i = 0; i < n; i = i + 1)
        total = total + arr[i];
    return total;
}

int main(void) {
    int arr[5];
    arr[0] = 1; arr[1] = 2; arr[2] = 3; arr[3] = 4; arr[4] = 5;
    return sum(arr, 5);
}
