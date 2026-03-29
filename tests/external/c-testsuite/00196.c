// TEST: ctest_00196
// DESCRIPTION: c-testsuite test 00196
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: fred
// STDOUT: 0
// STDOUT: fred
// STDOUT: joe
// STDOUT: 1
// STDOUT: joe
// STDOUT: fred
// STDOUT: 0
// STDOUT: joe
// STDOUT: 1
// STDOUT: fred
// STDOUT: 0
// STDOUT: fred
// STDOUT: joe
// STDOUT: 1
// STDOUT: joe
// STDOUT: fred
// STDOUT: 0
// STDOUT: joe
// STDOUT: 1

#include <stdio.h>

int fred()
{
   printf("fred\n");
   return 0;
}

int joe()
{
   printf("joe\n");
   return 1;
}

int main()
{
   printf("%d\n", fred() && joe());
   printf("%d\n", fred() || joe());
   printf("%d\n", joe() && fred());
   printf("%d\n", joe() || fred());
   printf("%d\n", fred() && (1 + joe()));
   printf("%d\n", fred() || (0 + joe()));
   printf("%d\n", joe() && (0 + fred()));
   printf("%d\n", joe() || (1 + fred()));

   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
