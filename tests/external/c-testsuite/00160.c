// TEST: ctest_00160
// DESCRIPTION: c-testsuite test 00160
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 1
// STDOUT: 1
// STDOUT: 2
// STDOUT: 3
// STDOUT: 5
// STDOUT: 8
// STDOUT: 13
// STDOUT: 21
// STDOUT: 34
// STDOUT: 55
// STDOUT: 89

#include <stdio.h>

int main()
{
   int a;
   int p;
   int t;

   a = 1;
   p = 0;
   t = 0;

   while (a < 100)
   {
      printf("%d\n", a);
      t = a;
      a = t + p;
      p = t;
   }

   return 0;
}

// vim: set expandtab ts=4 sw=3 sts=3 tw=80 :
