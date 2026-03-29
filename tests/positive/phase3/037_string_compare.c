// TEST: string_compare
// DESCRIPTION: Manual string comparison
// EXPECTED_EXIT: 1
// ENVIRONMENT: hosted
// PHASE: 3

int streq(char *a, char *b) {
    while (*a && *b) {
        if (*a != *b) return 0;
        a = a + 1;
        b = b + 1;
    }
    return *a == *b;
}

int main(void) {
    return streq("hello", "hello");
}
