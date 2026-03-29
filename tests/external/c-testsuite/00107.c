// TEST: ctest_00107
// DESCRIPTION: c-testsuite test 00107
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

typedef int myint;
myint x = (myint)1;

int
main(void)
{
	return x-1;
}
