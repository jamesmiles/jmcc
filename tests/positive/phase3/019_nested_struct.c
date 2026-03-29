// TEST: nested_struct
// DESCRIPTION: Nested struct access
// EXPECTED_EXIT: 35
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.7.2.1 (Structure specifiers)

struct Point {
    int x;
    int y;
};

struct Line {
    struct Point start;
    struct Point end;
};

int main(void) {
    struct Line l;
    l.start.x = 10;
    l.start.y = 20;
    l.end.x = 30;
    l.end.y = 5;
    return l.start.x + l.start.y + l.end.y;
}
