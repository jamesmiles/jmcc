// TEST: ctest_00154
// DESCRIPTION: c-testsuite test 00154
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 12
// STDOUT: 34
// STDOUT: 12
// STDOUT: 34
// STDOUT: 56
// STDOUT: 78

#include <stdio.h>

struct fred
{
   int boris;
   int natasha;
};

int main()
{
   struct fred bloggs;

   bloggs.boris = 12;
   bloggs.natasha = 34;

   printf("%d\n", bloggs.boris);
   printf("%d\n", bloggs.natasha);

   struct fred jones[2];
   jones[0].boris = 12;
   jones[0].natasha = 34;
   jones[1].boris = 56;
   jones[1].natasha = 78;

   printf("%d\n", jones[0].boris);
   printf("%d\n", jones[0].natasha);
   printf("%d\n", jones[1].boris);
   printf("%d\n", jones[1].natasha);

   return 0;
}
