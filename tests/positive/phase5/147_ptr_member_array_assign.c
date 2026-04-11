// TEST: ptr_member_array_assign
// DESCRIPTION: Assigning to ptr->ptr_array[i] must not trigger struct copy
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's wi_stuff.c does:
     a->p[i] = (patch_t *)W_CacheLumpName(name, PU_STATIC);
   where a is anim_t* and p is patch_t*[3] (array of pointers).
   a->p[i] is a patch_t* (POINTER), but the compiler identifies it
   as patch_t (STRUCT by value) and tries to do rep movsb copy.
   gen_lvalue_addr is then called on the function call result,
   which is not an lvalue, producing "expression is not an lvalue". */

int printf(const char *fmt, ...);

typedef struct { short w; short h; } patch_t;

typedef struct {
    int id;
    patch_t *p[3];
} container_t;

patch_t patches[3] = {{10, 20}, {30, 40}, {50, 60}};

patch_t *get_patch(int i) {
    return &patches[i];
}

int main(void) {
    container_t c;
    container_t *a = &c;

    /* ptr->ptr_array[i] = function_returning_ptr() */
    a->p[0] = get_patch(0);
    a->p[1] = get_patch(1);
    a->p[2] = get_patch(2);

    if (a->p[0]->w != 10) return 1;
    if (a->p[1]->w != 30) return 2;
    if (a->p[2]->h != 60) return 3;

    /* Also with direct pointer assignment */
    a->p[0] = &patches[2];
    if (a->p[0]->w != 50) return 4;

    printf("ok\n");
    return 0;
}
