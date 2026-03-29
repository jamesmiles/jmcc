// TEST: ctest_00153
// DESCRIPTION: c-testsuite test 00153
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#define x f
#define y() f

typedef struct { int f; } S;

int
main()
{
	S s;

	s.x = 0;
	return s.y();
}
