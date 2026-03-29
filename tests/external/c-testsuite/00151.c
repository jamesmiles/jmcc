// TEST: ctest_00151
// DESCRIPTION: c-testsuite test 00151
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int arr[][3][5] = {
	{
		{ 0, 0, 3, 5 },
		{ 1, [3] = 6, 7 },
	},
	{
		{ 1, 2 },
		{ [4] = 7, },
	},
};

int
main(void)
{
	return !(arr[0][1][4] == arr[1][1][4]);
}
