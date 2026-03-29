// TEST: cast_int_to_char
// DESCRIPTION: Cast integer to char (truncation)
// EXPECTED_EXIT: 65
// ENVIRONMENT: hosted
// PHASE: 4
// STANDARD_REF: 6.3 (Conversions)

int main(void) {
    int x = 321;
    char c = (char)x;
    return c;
}
