// TEST: tower_of_hanoi
// DESCRIPTION: Count moves in Tower of Hanoi (2^n - 1)
// EXPECTED_EXIT: 31
// ENVIRONMENT: hosted
// PHASE: 3

int count = 0;

void hanoi(int n, int from, int to, int aux) {
    if (n == 0) return;
    hanoi(n - 1, from, aux, to);
    count = count + 1;
    hanoi(n - 1, aux, to, from);
}

int main(void) {
    hanoi(5, 1, 3, 2);
    return count;
}
