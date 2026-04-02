// TEST: char_ptr_array_iterate
// DESCRIPTION: Iterate NULL-terminated char*[] after D_AddFile pattern (Doom WAD loading)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: file: test.wad
// STDOUT: done
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's W_InitMultipleFiles iterates char** wadfiles with:
     for ( ; *filenames ; filenames++) W_AddFile(*filenames);
   The wadfiles[] array is filled by D_AddFile which malloc+strcpy's paths.
   If the pointer comparison or array iteration has a codegen bug,
   Doom passes NULL to W_AddFile and crashes. */

int printf(const char *fmt, ...);
int strlen(const char *s);
int strcpy(char *dst, const char *src);
void *malloc(unsigned long size);

#define MAXFILES 20

char *wadfiles[MAXFILES];

void D_AddFile(char *file) {
    int numwadfiles;
    char *newfile;

    for (numwadfiles = 0; wadfiles[numwadfiles]; numwadfiles++)
        ;

    newfile = (char *)malloc(strlen(file) + 1);
    strcpy(newfile, file);
    wadfiles[numwadfiles] = newfile;
}

void W_InitMultipleFiles(char **filenames) {
    for ( ; *filenames ; filenames++) {
        printf("file: %s\n", *filenames);
    }
}

int main(void) {
    D_AddFile("test.wad");
    W_InitMultipleFiles(wadfiles);
    printf("done\n");
    return 0;
}
