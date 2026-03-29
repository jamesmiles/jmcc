// TEST: define_const
// DESCRIPTION: Object-like macro (constant definition)
// EXPECTED_EXIT: 42
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.10.3 (Macro replacement)

#define ANSWER 42

int main(void) {
    return ANSWER;
}
