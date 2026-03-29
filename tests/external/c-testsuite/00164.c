// TEST: ctest_00164
// DESCRIPTION: c-testsuite test 00164
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 134
// STDOUT: 134
// STDOUT: 0
// STDOUT: 1
// STDOUT: 1
// STDOUT: 1
// STDOUT: 1
// STDOUT: 46
// STDOUT: 1, 0
// STDOUT: 0, 1
// STDOUT: 1
// STDOUT: 1916
// STDOUT: 1916
// STDOUT: 64
// STDOUT: 4

#include <stdio.h>

int main()
{
   int a;
   int b;
   int c;
   int d;
   int e;
   int f;
   int x;
   int y;

   a = 12;
   b = 34;
   c = 56;
   d = 78;
   e = 0;
   f = 1;

   printf("%d\n", c + d);
   printf("%d\n", (y = c + d));
   printf("%d\n", e || e && f);
   printf("%d\n", e || f && f);
   printf("%d\n", e && e || f);
   printf("%d\n", e && f || f);
   printf("%d\n", a && f | f);
   printf("%d\n", a | b ^ c & d);
   printf("%d, %d\n", a == a, a == b);
   printf("%d, %d\n", a != a, a != b);
   printf("%d\n", a != b && c != d);
   printf("%d\n", a + b * c / f);
   printf("%d\n", a + b * c / f);
   printf("%d\n", (4 << 4));
   printf("%d\n", (64 >> 4));

   return 0;
}

// vim: set expandtab ts=4 sw=3 sts=3 tw=80 :
