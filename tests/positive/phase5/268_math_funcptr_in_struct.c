// TEST: math_funcptr_in_struct
// DESCRIPTION: undeclared math functions stored as void* in struct initializer must not become NULL/crash
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
#include <math.h>

typedef double (*MathFunc)(double);

static struct { void *fn; const char *name; } mathFuncs[] = {
    {(void*)asinh, "asinh"},
    {(void*)acosh, "acosh"},
    {(void*)atanh, "atanh"},
};

int main(void) {
    int ok = 1;
    double inputs[] = {1.0, 2.0, 0.5};
    double expected[] = {0.8813736, 1.3169579, 0.5493061};
    for (int i = 0; i < 3; i++) {
        MathFunc f = (MathFunc)mathFuncs[i].fn;
        if (f == 0) { printf("FAIL: %s ptr is NULL\n", mathFuncs[i].name); ok=0; continue; }
        double r = f(inputs[i]);
        if (r < expected[i] - 0.001 || r > expected[i] + 0.001) {
            printf("FAIL: %s(%g)=%g expected ~%g\n", mathFuncs[i].name, inputs[i], r, expected[i]);
            ok=0;
        }
    }
    if (ok) printf("ok\n");
    return ok ? 0 : 1;
}
