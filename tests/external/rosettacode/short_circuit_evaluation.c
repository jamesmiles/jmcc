// TEST: rosetta_short_circuit_evaluation
// DESCRIPTION: Rosetta Code - Short-circuit evaluation (preprocessor # stringify)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Short-circuit_evaluation#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: I am a
// STDOUT: false && true = false
// STDOUT:
// STDOUT: I am a
// STDOUT: true || false = true
// STDOUT:
// STDOUT: I am a
// STDOUT: I am b
// STDOUT: true && false = false
// STDOUT:
// STDOUT: I am a
// STDOUT: I am b
// STDOUT: false || false = false
// STDOUT:

#include <stdio.h>
#include <stdbool.h>

bool a(bool in)
{
  printf("I am a\n");
  return in;
}

bool b(bool in)
{
  printf("I am b\n");
  return in;
}

#define TEST(X,Y,O)						\
  do {								\
    x = a(X) O b(Y);						\
    printf(#X " " #O " " #Y " = %s\n\n", x ? "true" : "false");	\
  } while(false);

int main()
{
  bool x;

  TEST(false, true, &&); // b is not evaluated
  TEST(true, false, ||); // b is not evaluated
  TEST(true, false, &&); // b is evaluated
  TEST(false, false, ||); // b is evaluated

  return 0;
}
