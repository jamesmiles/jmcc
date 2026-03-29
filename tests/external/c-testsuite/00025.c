// TEST: ctest_00025
// DESCRIPTION: c-testsuite test 00025
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int strlen(char *);

int
main()
{
	char *p;
	
	p = "hello";
	return strlen(p) - 5;
}
