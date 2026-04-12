// TEST: rosetta_return_multiple_values
// DESCRIPTION: Rosetta Code - Return multiple values (large struct return by value)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Return_multiple_values#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT: Values from a function returning a structure : { 1, 2.300000, a, Hello World, 45.678000}

#include<stdio.h>

typedef struct{
	int integer;
	float decimal;
	char letter;
	char string[100];
	double bigDecimal;
}Composite;

Composite example()
{
	Composite C = {1, 2.3, 'a', "Hello World", 45.678};
	return C;
}


int main()
{
	Composite C = example();

	printf("Values from a function returning a structure : { %d, %f, %c, %s, %f}\n", C.integer, C.decimal, C.letter, C.string, C.bigDecimal);

	return 0;
}
