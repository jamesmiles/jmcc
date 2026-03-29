// TEST: string_length
// DESCRIPTION: Manual strlen implementation
// EXPECTED_EXIT: 13
// ENVIRONMENT: hosted
// PHASE: 3

int my_strlen(char *s) {
    int len = 0;
    while (s[len] != 0) {
        len = len + 1;
    }
    return len;
}

int main(void) {
    return my_strlen("Hello, World!");
}
