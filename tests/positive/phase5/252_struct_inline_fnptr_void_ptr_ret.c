// Bug 252: inline function pointer struct member — jmcc misidentifies return type,
// emits movslq after indirect call, corrupting void* return value for mmap addresses
#include <stdio.h>
#include <stdlib.h>

struct methods {
    void *(*xRealloc)(void*, int);  // inline fnptr — no typedef
};

static void *my_realloc(void *p, int n) { return realloc(p, (size_t)n); }
static struct methods g = { my_realloc };

int main(void) {
    void *p = malloc(200000);   // force mmap address (>128KB)
    if (!p) return 1;
    void *q = g.xRealloc(p, 300000);  // indirect call via inline fnptr member
    if (!q) { printf("FAIL: NULL\n"); return 1; }
    // Write/read to verify pointer is not truncated
    ((unsigned char*)q)[0] = 0xAB;
    ((unsigned char*)q)[299999] = 0xCD;
    if (((unsigned char*)q)[0] != 0xAB || ((unsigned char*)q)[299999] != 0xCD) {
        printf("FAIL: pointer corrupted (got %p)\n", q);
        return 1;
    }
    printf("ok\n");
    free(q);
    return 0;
}
