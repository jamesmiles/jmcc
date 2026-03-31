// TEST: string_table
// DESCRIPTION: Array of string pointers with index lookup (Doom name tables)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: imp
// STDOUT: demon
// STDOUT: baron
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

int main(void) {
    const char *names[] = {"imp", "demon", "baron", "cyberdemon", "spider"};
    printf("%s\n", names[0]);
    printf("%s\n", names[1]);
    printf("%s\n", names[2]);
    return 0;
}
