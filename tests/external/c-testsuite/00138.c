// TEST: ctest_00138
// DESCRIPTION: c-testsuite test 00138
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#define M(x) x
#define A(a,b) a(b)

int
main(void)
{
	char *a = A(M,"hi");

	return (a[1] == 'i') ? 0 : 1;
}
