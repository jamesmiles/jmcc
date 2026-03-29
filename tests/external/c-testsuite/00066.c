// TEST: ctest_00066
// DESCRIPTION: c-testsuite test 00066
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#define A 3
#define FOO(X,Y,Z) X + Y + Z
#define SEMI ;

int
main()
{
	if(FOO(1, 2, A) != 6)
		return 1 SEMI
	return FOO(0,0,0);
}
