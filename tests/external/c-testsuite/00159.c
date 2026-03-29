// TEST: ctest_00159
// DESCRIPTION: c-testsuite test 00159
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 9
// STDOUT: 16
// STDOUT: a=1234
// STDOUT: qfunc()

#include <stdio.h>

int myfunc(int x)
{
   return x * x;
}

void vfunc(int a)
{
   printf("a=%d\n", a);
}

void qfunc()
{
   printf("qfunc()\n");
}

void zfunc()
{
   ((void (*)(void))0) ();
}

int main()
{
   printf("%d\n", myfunc(3));
   printf("%d\n", myfunc(4));

   vfunc(1234);

   qfunc();

   return 0;
}

// vim: set expandtab ts=4 sw=3 sts=3 tw=80 :
