// TEST: ctest_00194
// DESCRIPTION: c-testsuite test 00194
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 0

#include <stdio.h>

int main()
{
   int a;
   char b;

   a = 0;
   while (a < 2)
   {
      printf("%d", a++);
      break;

      b = 'A';
      while (b < 'C')
      {
         printf("%c", b++);
      }
      printf("e");
   }
   printf("\n");

   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
