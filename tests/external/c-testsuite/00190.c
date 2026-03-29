// TEST: ctest_00190
// DESCRIPTION: c-testsuite test 00190
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: yo

#include <stdio.h>

void fred(void)
{
   printf("yo\n");
}

int main()
{
   fred();

   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
