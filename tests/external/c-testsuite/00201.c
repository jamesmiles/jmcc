// TEST: ctest_00201
// DESCRIPTION: c-testsuite test 00201
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 42

#include <stdio.h>	// printf()

#define CAT2(a,b) a##b
#define CAT(a,b) CAT2(a,b)
#define AB(x) CAT(x,y)

int main(void)
{
  int xy = 42;
  printf("%d\n", CAT(A,B)(x));
  return 0;
}
