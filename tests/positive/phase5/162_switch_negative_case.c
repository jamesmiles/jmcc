// TEST: switch_negative_case
// DESCRIPTION: Switch/case with negative case values must dispatch correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's T_MovePlane has: switch(direction) { case -1: ... case 1: ... }
   jmcc only emits a comparison for case 1, never for case -1.
   So floor-lowering (direction=-1) is never executed and secret
   platforms in E1M1 don't work. */

int printf(const char *fmt, ...);

int classify(int dir) {
    switch (dir) {
      case -1:
        return 10;
      case 0:
        return 20;
      case 1:
        return 30;
    }
    return -1;
}

/* Nested switch with negative cases (Doom's exact pattern) */
int move_plane(int floor_or_ceiling, int direction) {
    switch (floor_or_ceiling) {
      case 0:
        switch (direction) {
          case -1:
            return 100;  /* floor going down */
          case 1:
            return 200;  /* floor going up */
        }
        break;
      case 1:
        switch (direction) {
          case -1:
            return 300;  /* ceiling going down */
          case 1:
            return 400;  /* ceiling going up */
        }
        break;
    }
    return 0;
}

/* Large negative values */
int big_neg(int x) {
    switch (x) {
      case -100: return 1;
      case -1:   return 2;
      case 0:    return 3;
      case 1:    return 4;
      case 100:  return 5;
    }
    return 0;
}

int main(void) {
    /* Test 1: basic negative case */
    if (classify(-1) != 10) return 1;
    if (classify(0) != 20) return 2;
    if (classify(1) != 30) return 3;

    /* Test 2: Doom's exact pattern — nested switch, direction=-1 */
    if (move_plane(0, -1) != 100) return 4;
    if (move_plane(0, 1) != 200) return 5;
    if (move_plane(1, -1) != 300) return 6;
    if (move_plane(1, 1) != 400) return 7;

    /* Test 3: large negative case values */
    if (big_neg(-100) != 1) return 8;
    if (big_neg(-1) != 2) return 9;
    if (big_neg(100) != 5) return 10;

    printf("ok\n");
    return 0;
}
