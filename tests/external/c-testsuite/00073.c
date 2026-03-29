// TEST: ctest_00073
// DESCRIPTION: c-testsuite test 00073
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	int arr[2];
	int *p;
	
	p = &arr[1];
	p -= 1;
	*p = 123;
	
	if(arr[0] != 123)
		return 1;
	return 0;
}
