// TEST: ctest_00137
// DESCRIPTION: c-testsuite test 00137
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#define x(y) #y

int
main(void)
{
	char *p;
	p = x(hello)  " is better than bye";

	return (*p == 'h') ? 0 : 1;
}
