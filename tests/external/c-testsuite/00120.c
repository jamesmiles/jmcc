// TEST: ctest_00120
// DESCRIPTION: c-testsuite test 00120
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

struct {
	enum { X } x;
} s;


int
main()
{
	return X;
}
