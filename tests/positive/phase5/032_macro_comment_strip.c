// TEST: macro_comment_strip
// DESCRIPTION: Macro definition with trailing comment must not include comment in expansion
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: tag=1
// STDOUT: level=2
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

#define PU_STATIC	1	// static entire execution time
#define PU_SOUND	2	// static while playing
#define PU_MUSIC	3	// static while playing

typedef struct {
    int tag;
} memblock_t;

int main(void) {
    memblock_t block;
    block.tag = PU_STATIC;
    printf("tag=%d\n", block.tag);

    int level = PU_SOUND;
    printf("level=%d\n", level);
    return 0;
}
