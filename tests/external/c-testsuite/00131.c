// TEST: ctest_00131
// DESCRIPTION: c-testsuite test 00131
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: Hello
// STDOUT: Hello
// STDOUT: Hello
// STDOUT: Hello
// STDOUT: Hello

#include <stdio.h>

int main() 
{
   printf("Hello\n");
   printf("Hello\n"); /* this is a comment */ printf("Hello\n");
   printf("Hello\n");
   // this is also a comment sayhello();
   printf("Hello\n");

   return 0;
}

// vim: set expandtab ts=4 sw=3 sts=3 tw=80 :
