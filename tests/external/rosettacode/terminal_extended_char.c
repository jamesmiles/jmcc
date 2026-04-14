// TEST: rosetta_terminal_extended_char
// DESCRIPTION: Rosetta Code - Terminal control/Display an extended character (UTF-8 output wrong)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Terminal_control/Display_an_extended_character#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: £
// STDOUT: £

#include <stdio.h>

int
main()
{
	puts("£");
	puts("\302\243"); /* if your terminal is utf-8 */
	return 0;
}
