// TEST: switch_fallthrough
// DESCRIPTION: Switch fallthrough (no break)
// EXPECTED_EXIT: 6
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.8.4.2 (The switch statement)

int main(void) {
    int x = 1;
    int r = 0;
    switch (x) {
        case 1:
            r = r + 1;
        case 2:
            r = r + 2;
        case 3:
            r = r + 3;
            break;
        default:
            r = 99;
    }
    return r;
}
