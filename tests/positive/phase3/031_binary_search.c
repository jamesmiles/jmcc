// TEST: binary_search
// DESCRIPTION: Binary search algorithm
// EXPECTED_EXIT: 3
// ENVIRONMENT: hosted
// PHASE: 3

int bsearch(int *arr, int n, int target) {
    int lo = 0;
    int hi = n - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] == target)
            return mid;
        if (arr[mid] < target)
            lo = mid + 1;
        else
            hi = mid - 1;
    }
    return -1;
}

int main(void) {
    int arr[7];
    arr[0] = 2;
    arr[1] = 5;
    arr[2] = 8;
    arr[3] = 12;
    arr[4] = 16;
    arr[5] = 23;
    arr[6] = 38;
    return bsearch(arr, 7, 12);
}
