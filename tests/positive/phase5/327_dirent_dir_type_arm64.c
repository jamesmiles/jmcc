/* Test: <dirent.h> types (DIR, struct dirent) and opendir/readdir/closedir.
 *
 * Reproduces the blocker in Chocolate Doom's i_glob.c, which stores a
 * DIR * inside a struct and calls opendir/readdir/closedir.
 *
 * Root cause: jmcc has no FALLBACK_HEADER for dirent.h, so DIR and
 * struct dirent are undefined on arm64-apple-darwin.
 *
 * clang: OK
 * jmcc (arm64-apple-darwin): error: expected type specifier (DIR unknown)
 */

#include <dirent.h>
#include <stddef.h>

/* Matches the glob_t / glob_s pattern from Chocolate Doom's i_glob.c */
struct glob_s {
    DIR           *dir;
    struct dirent *current;
    char          *directory;
    int            count;
};
typedef struct glob_s glob_t;

int count_entries(const char *path) {
    glob_t g;
    int n = 0;
    g.dir = opendir(path);
    if (!g.dir) return -1;
    while ((g.current = readdir(g.dir)) != NULL) {
        if (g.current->d_type == DT_DIR) continue;
        n++;
    }
    closedir(g.dir);
    return n;
}

int main(void) {
    /* Just verify the types are usable; don't actually open a directory */
    return 0;
}
