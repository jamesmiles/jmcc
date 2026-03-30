// TEST: nested_loops_break
// DESCRIPTION: Break in nested loops only breaks inner loop
// EXPECTED_EXIT: 6
// ENVIRONMENT: hosted
// PHASE: 3

int main(void) {
    int count = 0;
    int i;
    int j;
    for (i = 0; i < 3; i = i + 1) {
        for (j = 0; j < 10; j = j + 1) {
            if (j == 2) break;
            count = count + 1;
        }
    }
    return count;
}
