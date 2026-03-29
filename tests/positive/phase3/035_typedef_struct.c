// TEST: typedef_struct
// DESCRIPTION: Typedef a struct type
// EXPECTED_EXIT: 30
// ENVIRONMENT: hosted
// PHASE: 3

typedef struct {
    int x;
    int y;
} Point;

int main(void) {
    Point p;
    p.x = 10;
    p.y = 20;
    return p.x + p.y;
}
