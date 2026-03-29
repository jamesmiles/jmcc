// TEST: ctest_00121
// DESCRIPTION: c-testsuite test 00121
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int f(int a), g(int a), a;


int
main()
{
	return f(1) - g(1);
}

int
f(int a)
{
	return a;
}

int
g(int a)
{
	return a;
}
