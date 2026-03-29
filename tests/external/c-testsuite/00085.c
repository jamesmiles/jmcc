// TEST: ctest_00085
// DESCRIPTION: c-testsuite test 00085
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#define ZERO_0() 0
#define ZERO_1(A) 0
#define ZERO_2(A, B) 0
#define ZERO_VAR(...) 0
#define ZERO_1_VAR(A, ...) 0

int
main()
{
	if (ZERO_0())
		return 1;
	if (ZERO_1(1))
		return 1;
	if (ZERO_2(1, 2))
		return 1;
	if (ZERO_VAR(1))
		return 1;
	if (ZERO_VAR(1, 2))
		return 1;
	if (ZERO_1_VAR(1, 2))
		return 1;
	if (ZERO_1_VAR(1, 2, 3))
		return 1;
		
	return 0;
}
