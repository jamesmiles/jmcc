// TEST: ctest_00165
// DESCRIPTION: c-testsuite test 00165
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 12
// STDOUT: 12, 24, 36

#include <stdio.h>

#define FRED 12
#define BLOGGS(x) (12*(x))

int main()
{
   printf("%d\n", FRED);
   printf("%d, %d, %d\n", BLOGGS(1), BLOGGS(2), BLOGGS(3));

   return 0;
}

// vim: set expandtab ts=4 sw=3 sts=3 tw=80 :
