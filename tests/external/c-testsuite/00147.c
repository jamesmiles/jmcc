// TEST: ctest_00147
// DESCRIPTION: c-testsuite test 00147
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int arr[3] = {[2] = 2, [0] = 0, [1] = 1};

int
main()
{
	if(arr[0] != 0)
		return 1;
	if(arr[1] != 1)
		return 2;
	if(arr[2] != 2)
		return 3;
	return 0;
}
