// TEST: struct_pass
// DESCRIPTION: Pass struct pointer to function
// EXPECTED_EXIT: 50
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.7.2.1 (Structure and union specifiers)

struct Rect {
    int w;
    int h;
};

int area(struct Rect *r) {
    return r->w * r->h;
}

int main(void) {
    struct Rect r;
    r.w = 5;
    r.h = 10;
    return area(&r);
}
