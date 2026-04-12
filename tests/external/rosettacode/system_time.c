// TEST: rosetta_system_time
// DESCRIPTION: Rosetta Code - System time (time_t typedef not recognized)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/System_time#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: Sun Apr 12 23:26:09 2026

#include<time.h>
#include<stdio.h>
#include<stdlib.h>
int main(){
  time_t my_time = time(NULL);
  printf("%s", ctime(&my_time));
  return 0;
}
