// TEST: short_array_struct_member
// DESCRIPTION: Struct member with 'short' type and multi-dim array (Doom's node_t)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: bbox=10
// STDOUT: children=3
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

typedef struct {
    int x;
    int y;
    int dx;
    int dy;
    short bbox[2][4];
    unsigned short children[2];
} node_t;

int main(void) {
    node_t node;
    node.bbox[1][2] = 10;
    node.children[0] = 3;
    printf("bbox=%d\n", node.bbox[1][2]);
    printf("children=%d\n", node.children[0]);
    return 0;
}
