// TEST: file_typedef_redecl
// DESCRIPTION: redeclaring FILE typedef must not corrupt FILE* parameter passing
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* jmcc's bundled <stdio.h> declares `typedef void FILE;`. System headers
   (pulled in via <sys/stat.h>, <unistd.h>, etc.) later redeclare
   `typedef struct _IO_FILE FILE;`. C allows this — a second typedef with
   the same name and a compatible type completion is legal.

   After the redeclaration, jmcc miscompiles any function taking three
   FILE* parameters whose body initializes a local FILE* array from
   those parameters:

       static T foo(FILE *a, FILE *b, FILE *c) {
           FILE *arr[3] = { a, b, c };   // arr ends up {NULL, NULL, NULL}
           ...
       }

   jmcc's stack allocator overlaps the saved-parameter slots with the
   local array's slots, AND the initializer copies from the parameter
   values are never emitted — the array ends up all-NULL. The caller's
   stderr/stdout/stdin pointers are correct at the call site; the callee
   just sees NULL.

   This blocks jmcc-compiling SQLite's shell.c, whose consoleClassifySetup
   follows exactly this pattern. The bug only triggers when a second FILE
   typedef follows the first and there is some intervening type / global
   context (enum, struct, static var). Extract the function to a minimal
   file without the second typedef and it compiles correctly. */

/* Emulate jmcc's bundled stdio.h */
typedef void FILE;
extern FILE *stdin;
extern FILE *stdout;
extern FILE *stderr;

/* Emulate system-header redeclaration arriving later */
struct _IO_FILE;
typedef struct _IO_FILE FILE;

/* Intervening declarations that the actual shell.c has before the
   offending function — these are needed to trigger the allocator bug. */
typedef enum E { E_ZERO = 0, E_ONE = 1 } E;

typedef struct Tag {
    short reaches;
    FILE *pf;
} Tag;

typedef struct Info {
    Tag a[3];
    Tag b[3];
    E which;
} Info;

static Info g_info;

int printf(const char *fmt, ...);
int fprintf(FILE *stream, const char *fmt, ...);

static short helper(FILE *pf, Tag *t) {
    t->pf = pf;
    return 0;
}

static void noop(void) {}

static E
classify(FILE *pfIn, FILE *pfOut, FILE *pfErr) {
    E rv = E_ZERO;
    FILE *apf[3] = { pfIn, pfOut, pfErr };
    int ix;
    for (ix = 2; ix >= 0; --ix) {
        Tag *t = &g_info.a[ix];
        if (helper(apf[ix], t)) rv |= (E_ONE<<ix);
    }
    if (apf[0] != pfIn) return (E)100;
    if (apf[1] != pfOut) return (E)101;
    if (apf[2] != pfErr) return (E)102;
    noop();
    return rv;
}

int main(void) {
    E rv = classify(stdin, stdout, stderr);
    if ((int)rv >= 100) {
        printf("FAIL: apf entries are NULL (rv=%d)\n", (int)rv);
        return (int)rv;
    }
    printf("ok\n");
    return 0;
}
