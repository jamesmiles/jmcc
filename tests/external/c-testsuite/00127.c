// TEST: ctest_00127
// DESCRIPTION: c-testsuite test 00127
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int c;

int
main()
{
	if(0) {
		return 1;
	} else if(0) {
	} else {
		if(1) {
			if(c)
				return 1;
			else
				return 0;
		} else {
			return 1;
		}
	}
	return 1;
}
