// TEST: string_literal_dedup
// DESCRIPTION: identical string literals should share storage (or code relying on it must still work)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* GCC and most C compilers merge identical string literals into a single
   storage location, so `"foo" == "foo"` and pointer arithmetic against
   a literal used at multiple call sites is consistent.

   jmcc emits each occurrence as a separate .rodata object, so:

       const char *cp = strchr("abcd", 'c');
       long off = cp - "abcd";   // SECOND occurrence — different address

   returns a garbage offset instead of 2.

   Reduced from rosettacode/poker_hand_analyser, which classifies face
   values via:

       #define FACES "23456789tjqka"
       cp = strchr(FACES, tolower(hand[i]));
       cards[j].face = cp - FACES;

   With jmcc, the two FACES occurrences expand to different addresses,
   so face values are random negative numbers, `groups[cards[i].face]++`
   corrupts stack memory, and every hand misclassifies as "high-card". */

#include <stdio.h>
#include <string.h>

int main(void) {
    /* Direct check */
    const char *a = "hello";
    const char *b = "hello";
    if (a != b) {
        printf("FAIL identical literals not merged: a=%p b=%p\n",
               (void*)a, (void*)b);
        return 1;
    }

    /* The poker pattern */
    const char *cp = strchr("23456789tjqka", '3');
    long off = cp - "23456789tjqka";
    if (off != 1) {
        printf("FAIL pointer diff: got %ld want 1\n", off);
        return 2;
    }

    /* Macro-expanded repetition */
    #define FACES "23456789tjqka"
    cp = strchr(FACES, 'k');
    off = cp - FACES;
    if (off != 11) {
        printf("FAIL macro repetition: got %ld want 11\n", off);
        return 3;
    }

    printf("ok\n");
    return 0;
}
