// TEST: ctest_00087
// DESCRIPTION: c-testsuite test 00087
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

struct S
{
	int	(*fptr)();
};

int
foo()
{
	return 0;
}

int
main()
{
	struct S v;
	
	v.fptr = foo;
	return v.fptr();
}

