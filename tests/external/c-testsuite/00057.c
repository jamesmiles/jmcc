// TEST: ctest_00057
// DESCRIPTION: c-testsuite test 00057
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	char a[16], b[16];
	
	if(sizeof(a) != sizeof(b))
		return 1;
	return 0;
}
