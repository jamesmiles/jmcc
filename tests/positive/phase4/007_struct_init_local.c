// TEST: struct_init_local
// DESCRIPTION: Local struct initialization with init list
// EXPECTED_EXIT: 10
// ENVIRONMENT: hosted
// PHASE: 4

struct Vec2 { int x; int y; };

int dot(struct Vec2 a, struct Vec2 b) {
    return a.x * b.x + a.y * b.y;
}

int main(void) {
    struct Vec2 v;
    v.x = 1;
    v.y = 2;
    struct Vec2 w;
    w.x = 2;
    w.y = 4;
    return dot(v, w);
}
