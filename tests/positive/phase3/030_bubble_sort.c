// TEST: bubble_sort
// DESCRIPTION: Bubble sort algorithm
// EXPECTED_EXIT: 1
// ENVIRONMENT: hosted
// PHASE: 3

void sort(int *arr, int n) {
    int i;
    int j;
    for (i = 0; i < n - 1; i = i + 1) {
        for (j = 0; j < n - i - 1; j = j + 1) {
            if (arr[j] > arr[j + 1]) {
                int tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
            }
        }
    }
}

int main(void) {
    int arr[5];
    arr[0] = 5;
    arr[1] = 3;
    arr[2] = 1;
    arr[3] = 4;
    arr[4] = 2;
    sort(arr, 5);
    // Check sorted: 1 2 3 4 5
    if (arr[0] != 1) return 0;
    if (arr[1] != 2) return 0;
    if (arr[2] != 3) return 0;
    if (arr[3] != 4) return 0;
    if (arr[4] != 5) return 0;
    return 1;
}
