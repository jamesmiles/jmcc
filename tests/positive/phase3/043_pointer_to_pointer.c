// TEST: pointer_to_pointer
// DESCRIPTION: Double pointer dereference and write
// EXPECTED_EXIT: 99
// ENVIRONMENT: hosted
// PHASE: 3

int main(void) {
    int x = 0;
    int *p = &x;
    int **pp = &p;
    **pp = 99;
    return x;
}
