// TEST: ctest_00130
// DESCRIPTION: c-testsuite test 00130
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	char arr[2][4], (*p)[4], *q;
	int v[4];

	p = arr;
	q = &arr[1][3];
	arr[1][3] = 2;
	v[0] = 2;

	if (arr[1][3] != 2)
		return 1;
	if (p[1][3] != 2)
		return 1;
	if (*q != 2)
		return 1;
	if (*v != 2)
		return 1;

	return 0;
}
