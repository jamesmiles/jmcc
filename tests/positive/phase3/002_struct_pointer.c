// TEST: struct_pointer
// DESCRIPTION: Struct pointer and arrow operator
// EXPECTED_EXIT: 42
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.5.2.3 (Structure and union members)

struct Pair {
    int a;
    int b;
};

int main(void) {
    struct Pair p;
    struct Pair *pp = &p;
    pp->a = 20;
    pp->b = 22;
    return pp->a + pp->b;
}
