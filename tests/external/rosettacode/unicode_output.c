// TEST: rosetta_unicode_output
// DESCRIPTION: Rosetta Code - Terminal control/Unicode output (\u escape sequence unsupported)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Terminal_control/Unicode_output#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: Unicode is supported on this terminal and U+25B3 is : △


#include<stdlib.h>
#include<stdio.h>

int
main ()
{
  int i;
  char *str = getenv ("LANG");

  for (i = 0; str[i + 2] != 00; i++)
    {
      if ((str[i] == 'u' && str[i + 1] == 't' && str[i + 2] == 'f')
          || (str[i] == 'U' && str[i + 1] == 'T' && str[i + 2] == 'F'))
        {
          printf
            ("Unicode is supported on this terminal and U+25B3 is : \u25b3");
          i = -1;
          break;
        }
    }

  if (i != -1)
    printf ("Unicode is not supported on this terminal.");

  return 0;
}
