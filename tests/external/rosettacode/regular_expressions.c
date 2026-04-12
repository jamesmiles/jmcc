// TEST: rosetta_regular_expressions
// DESCRIPTION: Rosetta Code - Regular expressions (regex.h, SIGSEGV)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Regular_expressions#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: 'this is a matching string' matched with 'string$'
// STDOUT: 'this is not a matching string!' did not matched with 'string$'
// STDOUT: mod string: 'this is a mistyfied string'

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <regex.h>
#include <string.h>

int main()
{
   regex_t preg;
   regmatch_t substmatch[1];
   const char *tp = "string$";
   const char *t1 = "this is a matching string";
   const char *t2 = "this is not a matching string!";
   const char *ss = "istyfied";
   
   regcomp(&preg, "string$", REG_EXTENDED);
   printf("'%s' %smatched with '%s'\n", t1,
                                        (regexec(&preg, t1, 0, NULL, 0)==0) ? "" : "did not ", tp);
   printf("'%s' %smatched with '%s'\n", t2,
                                        (regexec(&preg, t2, 0, NULL, 0)==0) ? "" : "did not ", tp);
   regfree(&preg);
   /* change "a[a-z]+" into "istifyed"?*/
   regcomp(&preg, "a[a-z]+", REG_EXTENDED);
   if ( regexec(&preg, t1, 1, substmatch, 0) == 0 )
   {
      //fprintf(stderr, "%d, %d\n", substmatch[0].rm_so, substmatch[0].rm_eo);
      char *ns = malloc(substmatch[0].rm_so + 1 + strlen(ss) +
                        (strlen(t1) - substmatch[0].rm_eo) + 2);
      memcpy(ns, t1, substmatch[0].rm_so+1);
      memcpy(&ns[substmatch[0].rm_so], ss, strlen(ss));
      memcpy(&ns[substmatch[0].rm_so+strlen(ss)], &t1[substmatch[0].rm_eo],
                strlen(&t1[substmatch[0].rm_eo]));
      ns[ substmatch[0].rm_so + strlen(ss) +
          strlen(&t1[substmatch[0].rm_eo]) ] = 0;
      printf("mod string: '%s'\n", ns);
      free(ns); 
   } else {
      printf("the string '%s' is the same: no matching!\n", t1);
   }
   regfree(&preg);
   
   return 0;
}
