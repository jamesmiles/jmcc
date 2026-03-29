// TEST: ctest_00186
// DESCRIPTION: c-testsuite test 00186
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: ->01<-
// STDOUT: ->02<-
// STDOUT: ->03<-
// STDOUT: ->04<-
// STDOUT: ->05<-
// STDOUT: ->06<-
// STDOUT: ->07<-
// STDOUT: ->08<-
// STDOUT: ->09<-
// STDOUT: ->10<-
// STDOUT: ->11<-
// STDOUT: ->12<-
// STDOUT: ->13<-
// STDOUT: ->14<-
// STDOUT: ->15<-
// STDOUT: ->16<-
// STDOUT: ->17<-
// STDOUT: ->18<-
// STDOUT: ->19<-
// STDOUT: ->20<-

#include <stdio.h>

int main()
{
   char Buf[100];
   int Count;

   for (Count = 1; Count <= 20; Count++)
   {
      sprintf(Buf, "->%02d<-\n", Count);
      printf("%s", Buf);
   }

   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
