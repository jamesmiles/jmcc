// TEST: func_ptr_ptr_param
// DESCRIPTION: Pointer-to-function-pointer as function parameter must parse
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Chocolate Doom's deh_frame.c (Heretic) declares:
     static boolean GetActionPointerForOffset(
         int offset,
         void (**result)(struct mobj_s *, struct player_s *, struct pspdef_s *))
   This is a double pointer to a function (**result)(...) as a parameter.
   jmcc can't parse the complex declarator. */

int printf(const char *fmt, ...);

typedef void (*action_fn)(int x, int y);

/* Function that takes a pointer-to-function-pointer parameter */
int find_action(int id, void (**result)(int, int)) {
    *result = 0;
    return id > 0;
}

/* With named struct parameters */
struct enemy;
struct player;

void attack(struct enemy *e, struct player *p) {}

int get_action(int offset, void (**out)(struct enemy *, struct player *)) {
    *out = attack;
    return 1;
}

/* Simpler: pointer-to-function-pointer */
int call_indirect(int (**fpp)(void)) {
    return (*fpp)();
}

int returns_42(void) { return 42; }

int main(void) {
    /* Test 1: basic pointer-to-function-pointer param */
    action_fn fn = 0;
    void (**pp)(int, int) = &fn;
    find_action(1, pp);

    /* Test 2: get function through output param */
    void (*action)(struct enemy *, struct player *) = 0;
    get_action(5, &action);
    if (action != attack) return 2;

    /* Test 3: call through double indirection */
    int (*f)(void) = returns_42;
    int (**fp)(void) = &f;
    if (call_indirect(fp) != 42) return 3;

    printf("ok\n");
    return 0;
}
