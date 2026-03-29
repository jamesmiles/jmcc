// TEST: ctest_00122
// DESCRIPTION: c-testsuite test 00122
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#define F(a, b) a
int
main()
{
	return F(, 1) 0;
}
