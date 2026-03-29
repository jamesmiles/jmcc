// TEST: pointer_arithmetic
// DESCRIPTION: Pointer to function parameter (pass by reference)
// EXPECTED_EXIT: 20
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.5.6 (Additive operators) - pointer arithmetic

void swap(int *a, int *b) {
    int tmp = *a;
    *a = *b;
    *b = tmp;
}

int main(void) {
    int x = 20;
    int y = 10;
    swap(&x, &y);
    return y;
}
