// TEST: enum_switch
// DESCRIPTION: Use enum values in switch statement
// EXPECTED_EXIT: 2
// ENVIRONMENT: hosted
// PHASE: 3

enum Direction { UP, DOWN, LEFT, RIGHT };

int main(void) {
    enum Direction d = DOWN;
    switch (d) {
        case UP: return 1;
        case DOWN: return 2;
        case LEFT: return 3;
        case RIGHT: return 4;
    }
    return 0;
}
