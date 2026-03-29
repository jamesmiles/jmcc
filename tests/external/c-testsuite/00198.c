// TEST: ctest_00198
// DESCRIPTION: c-testsuite test 00198
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: a=0
// STDOUT: b=1
// STDOUT: c=2
// STDOUT: e=0
// STDOUT: f=1
// STDOUT: g=2
// STDOUT: i=0
// STDOUT: j=1
// STDOUT: k=2

#include <stdio.h>

enum fred { a, b, c };

int main()
{
   printf("a=%d\n", a);
   printf("b=%d\n", b);
   printf("c=%d\n", c);

   enum fred d;

   typedef enum { e, f, g } h;
   typedef enum { i, j, k } m;

   printf("e=%d\n", e);
   printf("f=%d\n", f);
   printf("g=%d\n", g);

   printf("i=%d\n", i);
   printf("j=%d\n", j);
   printf("k=%d\n", k);

   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
