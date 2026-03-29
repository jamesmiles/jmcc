// TEST: ctest_00026
// DESCRIPTION: c-testsuite test 00026
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	char *p;
	
	p = "hello";
	return p[0] - 104;
}
