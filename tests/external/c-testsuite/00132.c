// TEST: ctest_00132
// DESCRIPTION: c-testsuite test 00132
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: Hello world
// STDOUT: Count = -5
// STDOUT: Count = -4
// STDOUT: Count = -3
// STDOUT: Count = -2
// STDOUT: Count = -1
// STDOUT: Count = 0
// STDOUT: Count = 1
// STDOUT: Count = 2
// STDOUT: Count = 3
// STDOUT: Count = 4
// STDOUT: Count = 5
// STDOUT: String 'hello', 'there' is 'hello', 'there'
// STDOUT: Character 'A' is 'A'
// STDOUT: Character 'a' is 'a'

#include <stdio.h>

int main() 
{
   printf("Hello world\n");

   int Count;
   for (Count = -5; Count <= 5; Count++)
      printf("Count = %d\n", Count);

   printf("String 'hello', 'there' is '%s', '%s'\n", "hello", "there");
   printf("Character 'A' is '%c'\n", 65);
   printf("Character 'a' is '%c'\n", 'a');

   return 0;
}

// vim: set expandtab ts=4 sw=3 sts=3 tw=80 :
