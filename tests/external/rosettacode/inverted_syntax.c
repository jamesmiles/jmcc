// TEST: rosetta_inverted_syntax
// DESCRIPTION: Rosetta Code - Inverted syntax (compile)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Inverted_syntax#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: 4


#include <stdio.h>
#include <stdlib.h>
#define otherwise       do { register int _o = 2; do { switch (_o) {  case 1:
#define given(Mc)       ;case 0: break; case 2: _o = !!(Mc); continue; } break; } while (1); } while (0)


int foo() { return 1; }

main()
{
        int a = 0;

        otherwise  a = 4 given (foo());
        printf("%d\n", a);
        exit(0);
}
