// TEST: struct_return_ptr
// DESCRIPTION: Function returning pointer to struct
// EXPECTED_EXIT: 7
// ENVIRONMENT: hosted
// PHASE: 3

struct Pair { int a; int b; };

struct Pair global_pair;

struct Pair *make_pair(int a, int b) {
    global_pair.a = a;
    global_pair.b = b;
    return &global_pair;
}

int main(void) {
    struct Pair *p = make_pair(3, 4);
    return p->a + p->b;
}
