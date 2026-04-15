// TEST: rosetta_formatted_numeric_output
// DESCRIPTION: Rosetta Code - Formatted numeric output (compile)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Formatted_numeric_output#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT:     -7.125
// STDOUT:      7.125
// STDOUT:  7.125    
// STDOUT:  -0007.125
// STDOUT:  00007.125
// STDOUT:  7.125    

#include <stdio.h>
main(){
  float r=7.125;
  printf(" %9.3f\n",-r);
  printf(" %9.3f\n",r);
  printf(" %-9.3f\n",r);
  printf(" %09.3f\n",-r);
  printf(" %09.3f\n",r);
  printf(" %-09.3f\n",r);
  return 0;
}