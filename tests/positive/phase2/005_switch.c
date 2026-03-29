// TEST: switch_stmt
// DESCRIPTION: Switch statement with cases and default
// EXPECTED_EXIT: 2
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.8.4.2 (The switch statement)

int main(void) {
    int x = 2;
    int r = 0;
    switch (x) {
        case 1:
            r = 10;
            break;
        case 2:
            r = 2;
            break;
        case 3:
            r = 30;
            break;
        default:
            r = 99;
            break;
    }
    return r;
}
