// TEST: typedef_array_param
// DESCRIPTION: Typedef'd array type as function parameter must decay to pointer
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Chocolate Doom's sha1.c declares:
     typedef byte sha1_digest_t[20];
     void SHA1_Final(sha1_digest_t digest, sha1_context_t *context);
   In C, array parameters decay to pointers. So sha1_digest_t digest
   becomes byte *digest. jmcc treats it as a 20-byte value instead
   of a pointer, causing the memcpy at the end of SHA1_Final to
   write to NULL. This is the second Chocolate Doom runtime crash. */

int printf(const char *fmt, ...);
void *memcpy(void *dst, const void *src, long n);

typedef unsigned char byte;
typedef byte digest_t[20];
typedef int vec3_t[3];

/* Function taking typedef'd array parameter — must receive as pointer */
void fill_digest(digest_t out, int seed) {
    int i;
    for (i = 0; i < 20; i++)
        out[i] = seed + i;
}

/* Another variant */
void fill_vec(vec3_t v, int x, int y, int z) {
    v[0] = x;
    v[1] = y;
    v[2] = z;
}

/* With memcpy into the parameter (Chocolate Doom's exact pattern) */
void copy_digest(digest_t dest, const byte *src) {
    memcpy(dest, src, 20);
}

int main(void) {
    /* Test 1: basic typedef array param */
    byte buf[20];
    fill_digest(buf, 10);
    if (buf[0] != 10) return 1;
    if (buf[19] != 29) return 2;

    /* Test 2: int array typedef */
    int v[3];
    fill_vec(v, 100, 200, 300);
    if (v[0] != 100) return 3;
    if (v[2] != 300) return 4;

    /* Test 3: memcpy into typedef array param */
    byte src[20];
    byte dst[20];
    int i;
    for (i = 0; i < 20; i++) src[i] = i * 2;
    copy_digest(dst, src);
    if (dst[0] != 0) return 5;
    if (dst[10] != 20) return 6;
    if (dst[19] != 38) return 7;

    printf("ok\n");
    return 0;
}
