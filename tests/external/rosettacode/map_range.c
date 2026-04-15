// TEST: rosetta_map_range
// DESCRIPTION: Rosetta Code - Map range (compile)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Map_range#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: Mapping [0,10] to [-1,0] at intervals of 1:
// STDOUT: f(0) = 1.01185e-320
// STDOUT: f(1) = 1.01185e-320
// STDOUT: f(2) = 1.01185e-320
// STDOUT: f(3) = 1.01185e-320
// STDOUT: f(4) = 1.01185e-320
// STDOUT: f(5) = 1.01185e-320
// STDOUT: f(6) = 1.01185e-320
// STDOUT: f(7) = 1.01185e-320
// STDOUT: f(8) = 1.01185e-320
// STDOUT: f(9) = 1.01185e-320
// STDOUT: f(10) = 1.01185e-320

#include <stdio.h>

#define mapRange(a1,a2,b1,b2,s) (b1 + (s-a1)*(b2-b1)/(a2-a1))

int main()
{
	int i;
	puts("Mapping [0,10] to [-1,0] at intervals of 1:");
	
	for(i=0;i<=10;i++)
	{
		printf("f(%d) = %g\n",i,mapRange(0,10,-1,0,i));
	}
	
	return 0;
}
