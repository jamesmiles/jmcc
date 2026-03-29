// TEST: array_sum
// DESCRIPTION: Sum elements of an array using a loop
// EXPECTED_EXIT: 15
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.5.2.1 (Array subscripting)

int main(void) {
    int arr[5];
    arr[0] = 1;
    arr[1] = 2;
    arr[2] = 3;
    arr[3] = 4;
    arr[4] = 5;
    int sum = 0;
    int i;
    for (i = 0; i < 5; i = i + 1) {
        sum = sum + arr[i];
    }
    return sum;
}
