// TEST: ctest_00145
// DESCRIPTION: c-testsuite test 00145
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#if 0 != (0 && (0/0))
   #error 0 != (0 && (0/0))
#endif

#if 1 != (-1 || (0/0))
   #error 1 != (-1 || (0/0))
#endif

#if 3 != (-1 ? 3 : (0/0))
   #error 3 != (-1 ? 3 : (0/0))
#endif

int
main()
{
	return 0;
}
