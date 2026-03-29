// TEST: ctest_00163
// DESCRIPTION: c-testsuite test 00163
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: a = 42
// STDOUT: bolshevic.a = 12
// STDOUT: bolshevic.b = 34
// STDOUT: bolshevic.c = 56
// STDOUT: tsar->a = 12
// STDOUT: tsar->b = 34
// STDOUT: tsar->c = 56
// STDOUT: bolshevic.b = 34

#include <stdio.h>

struct ziggy
{
   int a;
   int b;
   int c;
} bolshevic;

int main()
{
   int a;
   int *b;
   int c;

   a = 42;
   b = &a;
   printf("a = %d\n", *b);

   bolshevic.a = 12;
   bolshevic.b = 34;
   bolshevic.c = 56;

   printf("bolshevic.a = %d\n", bolshevic.a);
   printf("bolshevic.b = %d\n", bolshevic.b);
   printf("bolshevic.c = %d\n", bolshevic.c);

   struct ziggy *tsar = &bolshevic;

   printf("tsar->a = %d\n", tsar->a);
   printf("tsar->b = %d\n", tsar->b);
   printf("tsar->c = %d\n", tsar->c);

   b = &(bolshevic.b);
   printf("bolshevic.b = %d\n", *b);

   return 0;
}

// vim: set expandtab ts=4 sw=3 sts=3 tw=80 :
