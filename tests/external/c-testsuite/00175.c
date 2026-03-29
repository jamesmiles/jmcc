// TEST: ctest_00175
// DESCRIPTION: c-testsuite test 00175
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: char: a
// STDOUT: char: b
// STDOUT: char: c
// STDOUT: int: 97
// STDOUT: int: 98
// STDOUT: int: 99
// STDOUT: float: 97.000000
// STDOUT: float: 98.000000
// STDOUT: float: 99.000000
// STDOUT: 97 97
// STDOUT: 97 97
// STDOUT: 97.000000 97.000000

#include <stdio.h>

void charfunc(char a)
{
   printf("char: %c\n", a);
}

void intfunc(int a)
{
   printf("int: %d\n", a);
}

void floatfunc(float a)
{
   printf("float: %f\n", a);
}

int main()
{
   charfunc('a');
   charfunc(98);
   charfunc(99.0);

   intfunc('a');
   intfunc(98);
   intfunc(99.0);

   floatfunc('a');
   floatfunc(98);
   floatfunc(99.0);

   /* printf("%c %d %f\n", 'a', 'b', 'c'); */
   /* printf("%c %d %f\n", 97, 98, 99); */
   /* printf("%c %d %f\n", 97.0, 98.0, 99.0); */

   char b = 97;
   char c = 97.0;

   printf("%d %d\n", b, c);

   int d = 'a';
   int e = 97.0;

   printf("%d %d\n", d, e);

   float f = 'a';
   float g = 97;

   printf("%f %f\n", f, g);

   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
