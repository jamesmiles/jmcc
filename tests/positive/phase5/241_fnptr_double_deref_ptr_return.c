// TEST: fnptr_double_deref_ptr_return
// DESCRIPTION: double-dereference of function pointer typedef whose return type is a pointer
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* sqlite3.c line 43809:
     pLockingStyle = (**(finder_type*)pVfs->pAppData)(zFilename, pNew);
   where finder_type = const sqlite3_io_methods *(*)(const char*, unixFile*)

   Bug: when the function pointer's return type is a pointer, the second '*'
   in '(**fp)()' generates a spurious extra movq load, treating the function
   pointer value as a data pointer and calling garbage. Should be a no-op
   (dereferencing a function designator gives the same function). */

#include <stdio.h>

struct methods { int version; };

/* function pointer typedef returning a pointer (the trigger for the bug) */
typedef const struct methods *(*finder_type)(const char *, void *);

static const struct methods g_methods = { 99 };

static const struct methods *my_finder(const char *z, void *p) {
    (void)z; (void)p;
    return &g_methods;
}

/* static const function pointer, address stored via void* -- like sqlite's UNIXVFS */
static const struct methods *(*const posixFinder)(const char *, void *) = my_finder;

struct vfs {
    int iVersion;
    int szOsFile;
    int mxPathname;
    int pad;
    void *pNext;
    const char *zName;
    void *pAppData;   /* (void*)&posixFinder */
};

static struct vfs aVfs = {
    1, 0, 512, 0, 0, "unix",
    (void*)&posixFinder
};

static const struct methods *call_finder(struct vfs *pVfs, const char *z) {
    return (**(finder_type*)pVfs->pAppData)(z, (void*)0);
}

int main(void) {
    const struct methods *m = call_finder(&aVfs, "test.db");
    if (!m || m->version != 99) {
        printf("FAIL: m=%p version=%d\n", (void*)m, m ? m->version : -1);
        return 1;
    }
    printf("ok\n");
    return 0;
}
