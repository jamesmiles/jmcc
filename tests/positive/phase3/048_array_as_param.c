// TEST: array_as_param
// DESCRIPTION: Pass array to function, modify through pointer
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 0 1 4 9 16
// ENVIRONMENT: hosted
// PHASE: 3

int printf(const char *fmt, ...);

void fill_squares(int *arr, int n) {
    int i;
    for (i = 0; i < n; i = i + 1) {
        arr[i] = i * i;
    }
}

int main(void) {
    int data[5];
    fill_squares(data, 5);
    printf("%d %d %d %d %d\n", data[0], data[1], data[2], data[3], data[4]);
    return 0;
}
