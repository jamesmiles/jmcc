// TEST: ctest_00015
// DESCRIPTION: c-testsuite test 00015
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	int arr[2];

	arr[0] = 1;
	arr[1] = 2;

	return arr[0] + arr[1] - 3;
}
