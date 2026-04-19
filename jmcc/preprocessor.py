"""JMCC Preprocessor - Handles #include, #define, #ifdef, etc."""

import os
import re
from typing import Dict, List, Optional, Set, Tuple
from .errors import JMCCError


class PreprocessorError(JMCCError):
    pass


class Preprocessor:
    """Simple C preprocessor.

    Handles:
    - #include "file" and #include <file> (with search paths)
    - #define NAME value (object-like macros)
    - #define NAME(args) body (function-like macros)
    - #undef NAME
    - #ifdef / #ifndef / #if / #elif / #else / #endif
    - #error
    - #pragma (ignored)
    - #line (ignored)
    - Predefined macros: __LINE__, __FILE__, __DATE__, __TIME__
    - ## (token paste) and # (stringify) in function-like macros
    """

    # Built-in freestanding headers that JMCC provides
    BUILTIN_HEADERS = {
        "alloca.h": """
#define alloca __builtin_alloca
""",
        "setjmp.h": """
typedef long int __jmp_buf[8];
struct __jmp_buf_tag {
    __jmp_buf __jmpbuf;
    int __mask_was_saved;
    int __jmpbuf_pad;
    unsigned long __saved_mask[16];
};
typedef struct __jmp_buf_tag jmp_buf[1];
typedef struct __jmp_buf_tag sigjmp_buf[1];
#define setjmp(env) __sigsetjmp((env), 0)
int __sigsetjmp(struct __jmp_buf_tag env[1], int savemask);
void longjmp(struct __jmp_buf_tag env[1], int val);
#define sigsetjmp(env, savemask) __sigsetjmp((env), (savemask))
void siglongjmp(struct __jmp_buf_tag env[1], int val);
""",
        "stddef.h": """
typedef long ptrdiff_t;
typedef unsigned long size_t;
typedef int wchar_t;
#define NULL ((void*)0)
#define offsetof(type, member) __builtin_offsetof(type, member)
""",
        # stdint.h — use real system header
        "stdbool.h": """
#define bool _Bool
#define true 1
#define false 0
#define __bool_true_false_are_defined 1
""",
        "stdarg.h": """
typedef struct {
    unsigned int gp_offset;
    unsigned int fp_offset;
    void *overflow_arg_area;
    void *reg_save_area;
} __va_list_tag;
typedef __va_list_tag va_list[1];
#define va_start(ap, param) __builtin_va_start(ap, param)
#define va_end(ap) __builtin_va_end(ap)
#define va_arg(ap, type) __builtin_va_arg(ap, type)
#define va_copy(dest, src) __builtin_va_copy(dest, src)
""",
        "limits.h": """
#ifndef _JMCC_LIMITS_H
#define _JMCC_LIMITS_H
#define CHAR_BIT 8
#define SCHAR_MIN (-128)
#define SCHAR_MAX 127
#define UCHAR_MAX 255
#define CHAR_MIN SCHAR_MIN
#define CHAR_MAX SCHAR_MAX
#define SHRT_MIN (-32768)
#define SHRT_MAX 32767
#define USHRT_MAX 65535
#define INT_MIN (-2147483647-1)
#define INT_MAX 2147483647
#define UINT_MAX 4294967295U
#define LONG_MIN (-9223372036854775807L-1L)
#define LONG_MAX 9223372036854775807L
#define ULONG_MAX 18446744073709551615UL
#define LLONG_MIN (-9223372036854775807LL-1LL)
#define LLONG_MAX 9223372036854775807LL
#define ULLONG_MAX 18446744073709551615ULL
#define LONG_LONG_MIN LLONG_MIN
#define LONG_LONG_MAX LLONG_MAX
#define MB_LEN_MAX 16
#define PATH_MAX 4096
#endif
""",
        "stdnoreturn.h": """
#define noreturn _Noreturn
""",
        "stdalign.h": """
#define alignas _Alignas
#define alignof _Alignof
""",
        "float.h": """
#define FLT_RADIX 2
#define FLT_MIN 1.17549435e-38F
#define FLT_MAX 3.40282347e+38F
#define FLT_EPSILON 1.19209290e-07F
#define DBL_MIN 2.2250738585072014e-308
#define DBL_MAX 1.7976931348623157e+308
#define DBL_EPSILON 2.2204460492503131e-16
""",
        # stdio.h — real header has function-type typedefs parser can't handle yet
        "stdio.h": """
#ifndef _JMCC_STDIO_H
#define _JMCC_STDIO_H
#include <stddef.h>
typedef void FILE;
typedef long fpos_t;
/* BSD-style short unsigned typedefs (historically in sys/types.h, widely expected) */
#ifndef _JMCC_BSD_TYPES
#define _JMCC_BSD_TYPES
typedef unsigned int uint;
typedef unsigned short ushort;
typedef unsigned long ulong;
typedef unsigned char u_char;
typedef unsigned short u_short;
typedef unsigned int u_int;
typedef unsigned long u_long;
#endif
extern FILE *stdin;
extern FILE *stdout;
extern FILE *stderr;
#define SEEK_SET 0
#define SEEK_CUR 1
#define SEEK_END 2
#define BUFSIZ 8192
#define EOF (-1)
#define FILENAME_MAX 4096
#define FOPEN_MAX 16
#define L_tmpnam 20
#define TMP_MAX 238328
#define _IOFBF 0
#define _IOLBF 1
#define _IONBF 2
int printf(const char *fmt, ...);
int fprintf(FILE *stream, const char *fmt, ...);
int sprintf(char *str, const char *fmt, ...);
int snprintf(char *str, unsigned long size, const char *fmt, ...);
int vprintf(const char *fmt, void *ap);
int vfprintf(FILE *stream, const char *fmt, void *ap);
int vsprintf(char *str, const char *fmt, void *ap);
int vsnprintf(char *str, unsigned long size, const char *fmt, void *ap);
int scanf(const char *fmt, ...);
int fscanf(FILE *stream, const char *fmt, ...);
int sscanf(const char *str, const char *fmt, ...);
FILE *fopen(const char *path, const char *mode);
FILE *freopen(const char *path, const char *mode, FILE *stream);
FILE *fdopen(int fd, const char *mode);
FILE *tmpfile(void);
char *tmpnam(char *s);
int fclose(FILE *stream);
int fflush(FILE *stream);
int fgetc(FILE *stream);
char *fgets(char *s, int size, FILE *stream);
int fputc(int c, FILE *stream);
int fputs(const char *s, FILE *stream);
int getc(FILE *stream);
int getchar(void);
char *gets(char *s);
int putc(int c, FILE *stream);
int putchar(int c);
int puts(const char *s);
int ungetc(int c, FILE *stream);
unsigned long fread(void *ptr, unsigned long size, unsigned long nmemb, FILE *stream);
unsigned long fwrite(const void *ptr, unsigned long size, unsigned long nmemb, FILE *stream);
int fseek(FILE *stream, long offset, int whence);
long ftell(FILE *stream);
void rewind(FILE *stream);
int fgetpos(FILE *stream, fpos_t *pos);
int fsetpos(FILE *stream, const fpos_t *pos);
void clearerr(FILE *stream);
int feof(FILE *stream);
int ferror(FILE *stream);
int fileno(FILE *stream);
void perror(const char *s);
int remove(const char *path);
int rename(const char *old_path, const char *new_path);
void setbuf(FILE *stream, char *buf);
int setvbuf(FILE *stream, char *buf, int mode, unsigned long size);
FILE *popen(const char *command, const char *mode);
int pclose(FILE *stream);
#endif
""",
        "stdlib.h": """
#ifndef _JMCC_STDLIB_H
#define _JMCC_STDLIB_H
#include <stddef.h>
#ifndef _JMCC_BSD_TYPES
#define _JMCC_BSD_TYPES
typedef unsigned int uint;
typedef unsigned short ushort;
typedef unsigned long ulong;
typedef unsigned char u_char;
typedef unsigned short u_short;
typedef unsigned int u_int;
typedef unsigned long u_long;
#endif
#define EXIT_SUCCESS 0
#define EXIT_FAILURE 1
#define RAND_MAX 2147483647
int abs(int);
long labs(long);
long long llabs(long long);
int atoi(const char *);
long atol(const char *);
long long atoll(const char *);
double atof(const char *);
long strtol(const char *, char **, int);
long long strtoll(const char *, char **, int);
unsigned long strtoul(const char *, char **, int);
unsigned long long strtoull(const char *, char **, int);
double strtod(const char *, char **);
void *malloc(size_t);
void *calloc(size_t, size_t);
void *realloc(void *, size_t);
void free(void *);
void exit(int);
void abort(void);
int atexit(void (*)(void));
char *getenv(const char *);
int system(const char *);
int rand(void);
void srand(unsigned int);
void qsort(void *, size_t, size_t, int (*)(const void *, const void *));
void *bsearch(const void *, const void *, size_t, size_t, int (*)(const void *, const void *));
#endif
""",
        "string.h": """
#include <stddef.h>
""",
        "ctype.h": "",
        "assert.h": """
#define assert(x) ((void)0)
""",
        "math.h": """
double sin(double);
double cos(double);
double tan(double);
double asin(double);
double acos(double);
double atan(double);
double atan2(double, double);
double sinh(double);
double cosh(double);
double tanh(double);
double sqrt(double);
double cbrt(double);
double fabs(double);
double pow(double, double);
double log(double);
double log2(double);
double log10(double);
double exp(double);
double exp2(double);
double floor(double);
double ceil(double);
double round(double);
double trunc(double);
double fmod(double, double);
double hypot(double, double);
double ldexp(double, int);
double frexp(double, int *);
double modf(double, double *);
float sqrtf(float);
float fabsf(float);
float floorf(float);
float ceilf(float);
float roundf(float);
float log2f(float);
float log10f(float);
float logf(float);
float expf(float);
float powf(float, float);
float sinf(float);
float cosf(float);
float tanf(float);
float fmodf(float, float);
#define INFINITY (__builtin_inff())
#define NAN (__builtin_nanf(""))
#define M_PI 3.14159265358979323846
#define M_E  2.71828182845904523536
#define M_LN2  0.69314718055994530942
#define M_LOG2E 1.44269504088896340736
#define M_SQRT2 1.41421356237309504880
""",
        # POSIX headers — keep stubs for now (real headers cause recursion
        # in macro expansion and parser failures with complex typedefs)
        "wchar.h": """
#ifndef _JMCC_WCHAR_H
#define _JMCC_WCHAR_H
typedef int wchar_t;
typedef unsigned int wint_t;
#define WEOF ((wint_t)-1)
#endif
""",
        "unistd.h": """
#define R_OK 4
#define W_OK 2
#define X_OK 1
#define F_OK 0
#define STDIN_FILENO 0
#define STDOUT_FILENO 1
#define STDERR_FILENO 2
#define SEEK_SET 0
#define SEEK_CUR 1
#define SEEK_END 2
#define _SC_ARG_MAX 0
#define _SC_CHILD_MAX 1
#define _SC_CLK_TCK 2
#define _SC_NGROUPS_MAX 3
#define _SC_OPEN_MAX 4
#define _SC_STREAM_MAX 5
#define _SC_TZNAME_MAX 6
#define _SC_JOB_CONTROL 7
#define _SC_SAVED_IDS 8
#define _SC_VERSION 29
#define _SC_PAGESIZE 30
#define _SC_PAGE_SIZE 30
#define _SC_NPROCESSORS_CONF 83
#define _SC_NPROCESSORS_ONLN 84
#define _SC_PHYS_PAGES 85
#define _SC_AVPHYS_PAGES 86
typedef int ssize_t;
int access(const char *path, int mode);
int close(int fd);
long read(int fd, void *buf, unsigned long count);
long write(int fd, const void *buf, unsigned long count);
long lseek(int fd, long offset, int whence);
long sysconf(int name);
int unlink(const char *path);
int rmdir(const char *path);
int chdir(const char *path);
char *getcwd(char *buf, unsigned long size);
int dup(int fd);
int dup2(int oldfd, int newfd);
int pipe(int pipefd[2]);
int isatty(int fd);
unsigned int sleep(unsigned int seconds);
int usleep(unsigned int usec);
int fsync(int fd);
int fdatasync(int fd);
int ftruncate(int fd, long length);
int truncate(const char *path, long length);
int getpid(void);
int getppid(void);
int getuid(void);
int geteuid(void);
int getgid(void);
int getegid(void);
char *getlogin(void);
int execv(const char *path, char *const argv[]);
int execvp(const char *file, char *const argv[]);
int execve(const char *path, char *const argv[], char *const envp[]);
int fork(void);
int _exit(int status);
long pread(int fd, void *buf, unsigned long count, long offset);
long pwrite(int fd, const void *buf, unsigned long count, long offset);
long pread64(int fd, void *buf, unsigned long count, long offset);
long pwrite64(int fd, const void *buf, unsigned long count, long offset);
int getpagesize(void);
long readlink(const char *path, char *buf, unsigned long bufsiz);
int fchown(int fd, unsigned int owner, unsigned int group);
""",
        "fcntl.h": """
#define O_RDONLY 0
#define O_WRONLY 1
#define O_RDWR 2
#define O_ACCMODE 3
#define O_CREAT 64
#define O_EXCL 128
#define O_NOCTTY 256
#define O_TRUNC 512
#define O_APPEND 1024
#define O_NONBLOCK 2048
#define O_NDELAY O_NONBLOCK
#define O_SYNC 1052672
#define O_DSYNC 4096
#define O_RSYNC O_SYNC
#define O_DIRECTORY 65536
#define O_NOFOLLOW 131072
#define O_CLOEXEC 524288
#define O_ASYNC 8192
#define O_LARGEFILE 0
#define F_DUPFD 0
#define F_GETFD 1
#define F_SETFD 2
#define F_GETFL 3
#define F_SETFL 4
#define F_GETLK 5
#define F_SETLK 6
#define F_SETLKW 7
#define FD_CLOEXEC 1
#define F_RDLCK 0
#define F_WRLCK 1
#define F_UNLCK 2
struct flock {
    short l_type;
    short l_whence;
    long l_start;
    long l_len;
    int l_pid;
};
int open(const char *path, int flags, ...);
int fcntl(int fd, int cmd, ...);
int creat(const char *path, int mode);
""",
        "sys/stat.h": """
struct stat {
    unsigned long st_dev;
    unsigned long st_ino;
    unsigned long st_nlink;
    unsigned int st_mode;
    unsigned int st_uid;
    unsigned int st_gid;
    unsigned int __pad0;
    unsigned long st_rdev;
    long st_size;
    long st_blksize;
    long st_blocks;
    long st_atime;
    long st_atimensec;
    long st_mtime;
    long st_mtimensec;
    long st_ctime;
    long st_ctimensec;
    long __unused[3];
};
#define S_IFMT   0170000
#define S_IFSOCK 0140000
#define S_IFLNK  0120000
#define S_IFREG  0100000
#define S_IFBLK  0060000
#define S_IFDIR  0040000
#define S_IFCHR  0020000
#define S_IFIFO  0010000
#define S_ISUID  0004000
#define S_ISGID  0002000
#define S_ISVTX  0001000
#define S_IRWXU  0000700
#define S_IRUSR  0000400
#define S_IWUSR  0000200
#define S_IXUSR  0000100
#define S_IRWXG  0000070
#define S_IRGRP  0000040
#define S_IWGRP  0000020
#define S_IXGRP  0000010
#define S_IRWXO  0000007
#define S_IROTH  0000004
#define S_IWOTH  0000002
#define S_IXOTH  0000001
#define S_ISREG(m)  (((m) & S_IFMT) == S_IFREG)
#define S_ISDIR(m)  (((m) & S_IFMT) == S_IFDIR)
#define S_ISLNK(m)  (((m) & S_IFMT) == S_IFLNK)
#define S_ISCHR(m)  (((m) & S_IFMT) == S_IFCHR)
#define S_ISBLK(m)  (((m) & S_IFMT) == S_IFBLK)
#define S_ISFIFO(m) (((m) & S_IFMT) == S_IFIFO)
#define S_ISSOCK(m) (((m) & S_IFMT) == S_IFSOCK)
int stat(const char *path, struct stat *buf);
int fstat(int fd, struct stat *buf);
int lstat(const char *path, struct stat *buf);
int chmod(const char *path, unsigned int mode);
int fchmod(int fd, unsigned int mode);
int mkdir(const char *path, unsigned int mode);
unsigned int umask(unsigned int mask);
""",
        "signal.h": """
#define SIGHUP 1
#define SIGINT 2
#define SIGQUIT 3
#define SIGILL 4
#define SIGABRT 6
#define SIGFPE 8
#define SIGKILL 9
#define SIGSEGV 11
#define SIGPIPE 13
#define SIGALRM 14
#define SIGTERM 15
#define SIGUSR1 10
#define SIGUSR2 12
#define SIG_DFL ((void (*)(int))0)
#define SIG_IGN ((void (*)(int))1)
typedef void (*sighandler_t)(int);
typedef struct { unsigned long __val[16]; } sigset_t;
typedef int pid_t;
typedef int uid_t;
typedef long clock_t;
typedef unsigned int uint;
typedef unsigned char uchar;
typedef unsigned short ushort;
typedef unsigned long ulong;
typedef struct {
    int si_signo;
    int si_errno;
    int si_code;
    int __pad0;
    int _pad[28];
} siginfo_t;
struct sigaction {
    void (*sa_sigaction)(int, siginfo_t *, void *);
    sigset_t sa_mask;
    int sa_flags;
    int __sa_pad;
    void (*sa_restorer)(void);
};
#define sa_handler sa_sigaction
int sigaction(int signum, const struct sigaction *act, struct sigaction *oldact);
int sigemptyset(sigset_t *set);
int sigfillset(sigset_t *set);
int sigaddset(sigset_t *set, int signum);
int sigdelset(sigset_t *set, int signum);
int sigprocmask(int how, const sigset_t *set, sigset_t *oldset);
sighandler_t signal(int signum, sighandler_t handler);
int raise(int sig);
int kill(int pid, int sig);
#define SA_NOCLDSTOP 0x00000001
#define SA_NOCLDWAIT 0x00000002
#define SA_SIGINFO 0x00000004
#define SA_ONSTACK 0x08000000
#define SA_RESTART 0x10000000
#define SA_NODEFER 0x40000000
#define SA_RESETHAND 0x80000000
#define FPE_INTDIV 1
#define FPE_INTOVF 2
#define FPE_FLTDIV 3
#define FPE_FLTOVF 4
#define FPE_FLTUND 5
#define FPE_FLTRES 6
#define FPE_FLTINV 7
""",
        "sys/time.h": """
struct timeval {
    long tv_sec;
    long tv_usec;
};
struct timezone {
    int tz_minuteswest;
    int tz_dsttime;
};
struct itimerval {
    struct timeval it_interval;
    struct timeval it_value;
};
int gettimeofday(struct timeval *tv, struct timezone *tz);
int setitimer(int which, const struct itimerval *new_value, struct itimerval *old_value);
#define ITIMER_REAL 0
#define ITIMER_VIRTUAL 1
#define ITIMER_PROF 2
""",
        "netinet/in.h": """
#define IPPROTO_TCP 6
#define IPPROTO_UDP 17
typedef unsigned short in_port_t;
typedef unsigned int in_addr_t;
#define INADDR_ANY ((in_addr_t)0)
#define INADDR_BROADCAST ((in_addr_t)0xffffffff)
struct in_addr { in_addr_t s_addr; };
struct sockaddr_in {
    unsigned short sin_family;
    in_port_t sin_port;
    struct in_addr sin_addr;
    unsigned char sin_zero[8];
};
unsigned short htons(unsigned short hostshort);
unsigned short ntohs(unsigned short netshort);
unsigned int htonl(unsigned int hostlong);
unsigned int ntohl(unsigned int netlong);
""",
        "sys/socket.h": """
#define SOCK_STREAM 1
#define SOCK_DGRAM 2
#define AF_INET 2
#define PF_INET 2
#define SOL_SOCKET 1
#define SO_BROADCAST 6
typedef unsigned int socklen_t;
struct sockaddr { unsigned short sa_family; char sa_data[14]; };
int socket(int domain, int type, int protocol);
int bind(int sockfd, const struct sockaddr *addr, socklen_t addrlen);
int sendto(int sockfd, const void *buf, unsigned long len, int flags, const struct sockaddr *dest, socklen_t addrlen);
int recvfrom(int sockfd, void *buf, unsigned long len, int flags, struct sockaddr *src, socklen_t *addrlen);
""",
        "sys/ioctl.h": """
#define FIONBIO 0x5421
#define FIONREAD 0x541B
""",
        "netdb.h": """
struct hostent {
    char *h_name;
    char **h_aliases;
    int h_addrtype;
    int h_length;
    char **h_addr_list;
};
struct hostent *gethostbyname(const char *name);
""",
        "values.h": """
#define MININT (-2147483647-1)
#define MAXINT 2147483647
#define MINSHORT (-32768)
#define MAXSHORT 32767
""",
        # X11/Xlib.h, X11/Xutil.h, X11/keysym.h — use real system headers
        # X11/extensions/XShm.h — use real system header (libxext-dev)
        "arpa/inet.h": """
#include <netinet/in.h>
in_addr_t inet_addr(const char *cp);
char *inet_ntoa(struct in_addr in);
int inet_aton(const char *cp, struct in_addr *inp);
""",
        # netdb.h — use real system header
        # sys/ipc.h, sys/shm.h, errno.h — use real system headers
        # values.h — use real system header
    }

    # System include search paths (appended after user-specified paths)
    SYSTEM_INCLUDE_PATHS = [
        "/usr/include/x86_64-linux-gnu",
        "/usr/include",
    ]

    def __init__(self, filename: str = "<stdin>", include_paths: List[str] = None):
        self.filename = filename
        self.include_paths = (include_paths or []) + [
            p for p in self.SYSTEM_INCLUDE_PATHS if os.path.isdir(p)
        ]
        self.macros: Dict[str, 'Macro'] = {}
        self.macro_stack: Dict[str, List] = {}  # name -> stack of saved Macro objects
        self.included_files: Set[str] = set()

        # Predefined macros
        import time
        now = time.localtime()
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        self.macros["__STDC__"] = Macro("__STDC__", body="1")
        self.macros["__STDC_VERSION__"] = Macro("__STDC_VERSION__", body="201112L")
        self.macros["__STDC_HOSTED__"] = Macro("__STDC_HOSTED__", body="1")
        self.macros["__JMCC__"] = Macro("__JMCC__", body="1")
        self.macros["__x86_64__"] = Macro("__x86_64__", body="1")
        self.macros["__linux__"] = Macro("__linux__", body="1")
        self.macros["__unix__"] = Macro("__unix__", body="1")
        self.macros["NULL"] = Macro("NULL", body="((void*)0)")
        self.macros["EOF"] = Macro("EOF", body="(-1)")
        self.macros["__LP64__"] = Macro("__LP64__", body="1")
        self.macros["__GNUC__"] = Macro("__GNUC__", body="4")
        self.macros["__GNUC_MINOR__"] = Macro("__GNUC_MINOR__", body="0")
        self.macros["__GNUC_PATCHLEVEL__"] = Macro("__GNUC_PATCHLEVEL__", body="0")
        # GCC builtin type limits (needed when __GNUC__ is defined, limits.h uses these)
        self.macros["__INT_MAX__"] = Macro("__INT_MAX__", body="2147483647")
        self.macros["__LONG_MAX__"] = Macro("__LONG_MAX__", body="9223372036854775807L")
        self.macros["__LONG_LONG_MAX__"] = Macro("__LONG_LONG_MAX__", body="9223372036854775807LL")
        self.macros["__SHRT_MAX__"] = Macro("__SHRT_MAX__", body="32767")
        self.macros["__SCHAR_MAX__"] = Macro("__SCHAR_MAX__", body="127")
        self.macros["__SIZEOF_INT__"] = Macro("__SIZEOF_INT__", body="4")
        self.macros["__SIZEOF_LONG__"] = Macro("__SIZEOF_LONG__", body="8")
        self.macros["__SIZEOF_POINTER__"] = Macro("__SIZEOF_POINTER__", body="8")
        self.macros["__SIZEOF_SHORT__"] = Macro("__SIZEOF_SHORT__", body="2")
        self.macros["__extension__"] = Macro("__extension__", body="")  # GCC extension prefix, ignored
        # Size/byte-order macros needed by glibc headers
        self.macros["__BYTE_ORDER__"] = Macro("__BYTE_ORDER__", body="1234")
        self.macros["__ORDER_LITTLE_ENDIAN__"] = Macro("__ORDER_LITTLE_ENDIAN__", body="1234")
        self.macros["__ORDER_BIG_ENDIAN__"] = Macro("__ORDER_BIG_ENDIAN__", body="4321")
        self.macros["__SIZEOF_INT__"] = Macro("__SIZEOF_INT__", body="4")
        self.macros["__SIZEOF_LONG__"] = Macro("__SIZEOF_LONG__", body="8")
        self.macros["__SIZEOF_POINTER__"] = Macro("__SIZEOF_POINTER__", body="8")
        self.macros["__SIZEOF_SHORT__"] = Macro("__SIZEOF_SHORT__", body="2")
        self.macros["__SIZEOF_LONG_LONG__"] = Macro("__SIZEOF_LONG_LONG__", body="8")
        self.macros["__CHAR_BIT__"] = Macro("__CHAR_BIT__", body="8")
        # Prevent system limits.h from trying to include GCC's internal limits.h
        self.macros["_GCC_LIMITS_H_"] = Macro("_GCC_LIMITS_H_", body="1")
        # __has_builtin must be in macros so #ifdef __has_builtin works
        self.macros["__has_builtin"] = Macro("__has_builtin", body="__has_builtin",
                                              is_func=True, params=["x"], is_variadic=False)
        self.macros["__SIZE_TYPE__"] = Macro("__SIZE_TYPE__", body="unsigned long")
        self.macros["__PTRDIFF_TYPE__"] = Macro("__PTRDIFF_TYPE__", body="long")
        self.macros["__WCHAR_TYPE__"] = Macro("__WCHAR_TYPE__", body="int")
        self.macros["__WINT_TYPE__"] = Macro("__WINT_TYPE__", body="unsigned int")
        self.macros["__INT_MAX__"] = Macro("__INT_MAX__", body="2147483647")
        self.macros["__LONG_MAX__"] = Macro("__LONG_MAX__", body="9223372036854775807L")
        self.macros["__SHRT_MAX__"] = Macro("__SHRT_MAX__", body="32767")
        # GNU extension keywords — define as standard equivalents or empty
        # (not defining __GNUC__ means cdefs.h takes the simple path)
        self.macros["__volatile__"] = Macro("__volatile__", body="volatile")
        self.macros["__const__"] = Macro("__const__", body="const")
        self.macros["__signed__"] = Macro("__signed__", body="signed")
        self.macros["__inline__"] = Macro("__inline__", body="inline")
        self.macros["__inline"] = Macro("__inline", body="inline")

    @staticmethod
    def _strip_comments(source: str) -> str:
        """Strip C comments from source (translation phase 3).

        Replaces /* ... */ with spaces (preserving newlines) and
        // ... with nothing.  Respects string and char literals.
        """
        result = []
        i = 0
        n = len(source)
        in_string = False
        in_char = False
        while i < n:
            c = source[i]
            # String literal
            if c == '"' and not in_char:
                if in_string:
                    result.append(c)
                    in_string = False
                else:
                    in_string = True
                    result.append(c)
                i += 1
                continue
            # Char literal
            if c == "'" and not in_string:
                if in_char:
                    result.append(c)
                    in_char = False
                else:
                    in_char = True
                    result.append(c)
                i += 1
                continue
            # Escape sequences inside strings/chars
            if (in_string or in_char) and c == '\\' and i + 1 < n:
                result.append(c)
                result.append(source[i + 1])
                i += 2
                continue
            # Inside string or char — pass through
            if in_string or in_char:
                result.append(c)
                i += 1
                continue
            # Block comment /* ... */
            if c == '/' and i + 1 < n and source[i + 1] == '*':
                i += 2
                result.append(' ')  # replace comment with single space
                while i < n:
                    if source[i] == '\n':
                        result.append('\n')  # preserve line numbers
                    elif source[i] == '*' and i + 1 < n and source[i + 1] == '/':
                        i += 2
                        break
                    i += 1
                continue
            # Line comment // ...
            if c == '/' and i + 1 < n and source[i + 1] == '/':
                i += 2
                while i < n and source[i] != '\n':
                    i += 1
                continue
            result.append(c)
            i += 1
        return ''.join(result)

    def preprocess(self, source: str, filename: str = None) -> str:
        if filename:
            self.filename = filename
        # Phase 2: splice lines (backslash-newline removal)
        source = source.replace('\\\n', '')
        # Phase 3: strip comments
        source = self._strip_comments(source)
        lines = source.split('\n')
        output = []
        self._process_lines(lines, output, filename or self.filename)
        # Strip blue-paint sentinels (used internally to prevent re-expansion)
        return '\n'.join(output).replace('\x00', '')

    def _process_lines(self, lines: List[str], output: List[str],
                       filename: str, if_stack: List[dict] = None):
        if if_stack is None:
            if_stack = []

        i = 0
        line_offset = 0  # adjustment from #line directives
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            self._current_line = i + 1 + line_offset

            # Check if we're in a disabled #if branch
            active = all(frame["active"] for frame in if_stack)

            if stripped.startswith('#'):
                directive = self._parse_directive(stripped)
                cmd = directive[0] if directive else ""

                if cmd in ("ifdef", "ifndef", "if"):
                    if cmd == "ifdef":
                        cond = directive[1] in self.macros if len(directive) > 1 else False
                    elif cmd == "ifndef":
                        cond = directive[1] not in self.macros if len(directive) > 1 else True
                    elif cmd == "if":
                        if active:
                            cond = self._eval_if_expr(' '.join(directive[1:]))
                        else:
                            cond = False
                    if_stack.append({
                        "active": active and cond,
                        "any_taken": cond,
                        "parent_active": active,
                    })
                    output.append("")  # blank line to preserve line numbers
                elif cmd == "elif":
                    if not if_stack:
                        output.append("")
                    else:
                        frame = if_stack[-1]
                        if frame["parent_active"] and not frame["any_taken"]:
                            cond = self._eval_if_expr(' '.join(directive[1:]))
                            frame["active"] = cond
                            if cond:
                                frame["any_taken"] = True
                        else:
                            frame["active"] = False
                    output.append("")
                elif cmd == "else":
                    if if_stack:
                        frame = if_stack[-1]
                        if frame["parent_active"] and not frame["any_taken"]:
                            frame["active"] = True
                            frame["any_taken"] = True
                        else:
                            frame["active"] = False
                    output.append("")
                elif cmd == "endif":
                    if if_stack:
                        if_stack.pop()
                    output.append("")
                elif not active:
                    output.append("")
                elif cmd == "define":
                    # Use original stripped line to preserve whitespace inside string literals
                    # (splitting on whitespace would collapse "    " to " ")
                    import re as _re
                    _m = _re.match(r'#\s*define\s+(.*)', stripped)
                    _define_rest = _m.group(1) if _m else ' '.join(directive[1:])
                    self._handle_define(_define_rest, stripped)
                    output.append("")
                elif cmd == "undef":
                    if len(directive) > 1:
                        self.macros.pop(directive[1], None)
                    output.append("")
                elif cmd == "include":
                    included = self._handle_include(stripped, filename)
                    if included:
                        inc_lines = included.split('\n')
                        self._process_lines(inc_lines, output, filename, if_stack)
                    else:
                        output.append("")
                elif cmd == "error":
                    msg = ' '.join(directive[1:])
                    raise PreprocessorError(f"#error {msg}", filename)
                elif cmd == "pragma":
                    # Handle push_macro/pop_macro
                    rest = ' '.join(directive[1:])
                    import re as _re
                    push_m = _re.match(r'push_macro\s*\(\s*"(\w+)"\s*\)', rest)
                    pop_m = _re.match(r'pop_macro\s*\(\s*"(\w+)"\s*\)', rest)
                    if push_m:
                        mname = push_m.group(1)
                        if mname not in self.macro_stack:
                            self.macro_stack[mname] = []
                        self.macro_stack[mname].append(self.macros.get(mname))
                    elif pop_m:
                        mname = pop_m.group(1)
                        if mname in self.macro_stack and self.macro_stack[mname]:
                            saved = self.macro_stack[mname].pop()
                            if saved is not None:
                                self.macros[mname] = saved
                            elif mname in self.macros:
                                del self.macros[mname]
                    output.append("")
                elif cmd == "line":
                    # #line NUMBER sets the current line number
                    if len(directive) > 1:
                        line_expr = self._expand_macros(' '.join(directive[1:2]))
                        try:
                            target_line = int(line_expr)
                            line_offset = target_line - (i + 2)  # +2: next line is i+1, 1-based
                        except ValueError:
                            pass
                    output.append("")
                else:
                    output.append("")
            elif active:
                # Regular line — expand macros
                # Join continuation lines if macro args span multiple lines
                # (Comments already stripped in phase 3)
                joined = line
                while i + 1 < len(lines):
                    depth = 0
                    in_s = False
                    skip_until = -1
                    for ci, ch in enumerate(joined):
                        if ci < skip_until:
                            continue
                        if ch == "'" and not in_s:
                            end = joined.find("'", ci + 1)
                            if end >= 0:
                                skip_until = end + 1
                            continue
                        if ch == '"' and not in_s: in_s = True
                        elif ch == '"' and in_s: in_s = False
                        elif not in_s and ch == '(': depth += 1
                        elif not in_s and ch == ')': depth -= 1
                    if depth > 0:
                        # Don't join across preprocessor directives
                        if i + 1 < len(lines) and lines[i + 1].strip().startswith('#'):
                            break
                        i += 1
                        joined += " " + lines[i].strip()
                        output.append("")  # placeholder for joined line
                    else:
                        break
                self._current_line = i + 1 + line_offset
                self._current_file = filename
                expanded = self._expand_macros(joined)
                output.append(expanded)
            else:
                output.append("")

            i += 1

    def _parse_directive(self, line: str) -> List[str]:
        """Parse a preprocessor directive into parts."""
        # Remove leading #
        line = line.lstrip()
        if line.startswith('#'):
            line = line[1:].strip()
        parts = line.split(None, 1)
        if not parts:
            return [""]
        cmd = parts[0]
        # Handle #include<file> (no space after include)
        if cmd.startswith("include") and len(cmd) > 7 and cmd[7] in '<"':
            return ["include", cmd[7:]] + (parts[1].split() if len(parts) > 1 else [])
        if len(parts) > 1:
            return [cmd] + parts[1].split()
        return [cmd]

    def _handle_define(self, rest: str, full_line: str):
        """Handle #define directive."""
        # Function-like macro: #define NAME(a, b) body
        # Object-like macro: #define NAME value
        rest = rest.strip()
        if not rest:
            return

        # Check for function-like macro (no space before paren)
        match = re.match(r'(\w+)\(([^)]*)\)\s*(.*)', rest)
        if match:
            name = match.group(1)
            params = [p.strip() for p in match.group(2).split(',') if p.strip()]
            body = match.group(3).strip()
            # Handle variadic macros: ... as last param
            is_variadic = False
            if params and params[-1] == '...':
                params.pop()
                is_variadic = True
            elif params and params[-1].endswith('...'):
                params[-1] = params[-1][:-3].strip()
                is_variadic = True
            self.macros[name] = Macro(name, params=params, body=body,
                                       is_func=True, is_variadic=is_variadic)
            return

        # Object-like macro
        parts = rest.split(None, 1)
        name = parts[0]
        body = parts[1].strip() if len(parts) > 1 else ""
        self.macros[name] = Macro(name, body=body)

    # Compatibility shims appended after real system headers are loaded.
    # These override macros that are unsafe for our test patterns (e.g. NULL display).
    HEADER_SHIMS = {
        "X11/Xlib.h": """
#include <X11/Xutil.h>
#undef DefaultScreen
#undef RootWindow
#undef BlackPixel
#undef DefaultVisual
#undef DefaultColormap
#undef DefaultDepth
#undef DisplayWidth
#undef DisplayHeight
#define DefaultScreen(dpy) ((dpy) ? (int)(((_XPrivDisplay)(dpy))->default_screen) : 0)
#define RootWindow(dpy, scr) ((dpy) ? ((((_XPrivDisplay)(dpy))->screens[scr]).root) : (unsigned long)0)
#define BlackPixel(dpy, scr) ((dpy) ? ((((_XPrivDisplay)(dpy))->screens[scr]).black_pixel) : (unsigned long)0)
#define DefaultVisual(dpy, scr) ((dpy) ? ((((_XPrivDisplay)(dpy))->screens[scr]).root_visual) : (Visual *)0)
#define DefaultColormap(dpy, scr) ((dpy) ? ((((_XPrivDisplay)(dpy))->screens[scr]).cmap) : (Colormap)0)
#define DefaultDepth(dpy, scr) ((dpy) ? ((((_XPrivDisplay)(dpy))->screens[scr]).root_depth) : 24)
#define DisplayWidth(dpy, scr) ((dpy) ? ((((_XPrivDisplay)(dpy))->screens[scr]).width) : 320)
#define DisplayHeight(dpy, scr) ((dpy) ? ((((_XPrivDisplay)(dpy))->screens[scr]).height) : 200)
""",
    }

    # Pre-content prepended before loading a real system header
    HEADER_PRE_SHIMS = {
        "X11/extensions/XShm.h": """
#include <X11/Xlib.h>
""",
    }

    # Post-content appended after loading a real system header
    HEADER_POST_SHIMS = {
        "X11/extensions/XShm.h": """
#ifndef ShmCompletion
#define ShmCompletion 0
#endif
""",
    }

    def _handle_include(self, line: str, current_file: str) -> Optional[str]:
        """Handle #include directive, return included content."""
        # Extract filename
        match = re.search(r'#\s*include\s*[<"]([^>"]+)[>"]', line)
        if not match:
            return None

        inc_name = match.group(1)
        is_system = '<' in line.split('include')[1]

        # Check builtin headers first
        if inc_name in self.BUILTIN_HEADERS:
            return self.BUILTIN_HEADERS[inc_name]

        def _load_file(full):
            if full in self.included_files:
                return ""
            self.included_files.add(full)
            with open(full) as f:
                content = f.read().replace('\\\n', '')
                content = self._strip_comments(content)
            # Prepend/append shims if they exist for this header
            if inc_name in self.HEADER_PRE_SHIMS:
                content = self.HEADER_PRE_SHIMS[inc_name] + '\n' + content
            if inc_name in self.HEADER_SHIMS:
                content += '\n' + self.HEADER_SHIMS[inc_name]
            if inc_name in self.HEADER_POST_SHIMS:
                content += '\n' + self.HEADER_POST_SHIMS[inc_name]
            return content

        # For quoted includes, search relative to current file
        if current_file and current_file != "<stdin>":
            dir_path = os.path.dirname(current_file)
            full = os.path.join(dir_path, inc_name)
            if os.path.exists(full):
                return _load_file(full)

        # Search include paths
        for path in self.include_paths:
            full = os.path.join(path, inc_name)
            if os.path.exists(full):
                return _load_file(full)

        return ""

    def _expand_macros(self, line: str, depth=0, expanding=None) -> str:
        """Expand macros in a line of text."""
        if not self.macros or depth > 20:
            return line
        if expanding is None:
            expanding = set()

        # Don't expand inside string literals or comments
        result = []
        i = 0
        in_string = False
        in_char = False
        string_char = None

        while i < len(line):
            ch = line[i]

            # String/char literal passthrough
            if ch == '"' and not in_char:
                if in_string and string_char == '"':
                    in_string = False
                elif not in_string:
                    in_string = True
                    string_char = '"'
                result.append(ch)
                i += 1
                continue
            if ch == "'" and not in_string:
                if in_char:
                    in_char = False
                else:
                    in_char = True
                result.append(ch)
                i += 1
                continue
            if ch == '\\' and (in_string or in_char):
                result.append(ch)
                i += 1
                if i < len(line):
                    result.append(line[i])
                    i += 1
                continue
            if in_string or in_char:
                result.append(ch)
                i += 1
                continue

            # Line comment
            if ch == '/' and i + 1 < len(line) and line[i + 1] == '/':
                result.append(line[i:])
                break

            # Try to match identifier for macro expansion
            if ch.isalpha() or ch == '_':
                j = i
                while j < len(line) and (line[j].isalnum() or line[j] == '_'):
                    j += 1
                word = line[i:j]
                # Blue-paint: identifier surrounded by \x00 sentinels is inhibited
                inhibited = (i > 0 and line[i-1] == '\x00' and j < len(line) and line[j] == '\x00')

                if word == "__LINE__":
                    result.append(str(getattr(self, '_current_line', 0)))
                    i = j
                    continue
                elif word == "__FILE__":
                    result.append(f'"{getattr(self, "_current_file", "<unknown>")}"')
                    i = j
                    continue
                elif word in self.macros and word not in expanding and word != "__has_builtin" and not inhibited:
                    macro = self.macros[word]
                    if macro.is_func:
                        # Function-like macro — look for (args)
                        k = j
                        while k < len(line) and line[k] in ' \t':
                            k += 1
                        if k < len(line) and line[k] == '(':
                            args, end = self._parse_macro_args(line, k)
                            raw_args = list(args)  # save unexpanded for stringify
                            # Pre-expand args (unless used with ## in the body)
                            # Propagate blue-paint set to prevent infinite recursion
                            if '##' not in macro.body:
                                args = [self._expand_macros(a, expanding=expanding | {word}) for a in args]
                            expanded = macro.expand(args, raw_args=raw_args)
                            expanded = self._expand_macros(expanded, expanding=expanding | {word})
                            result.append(expanded)
                            i = end
                            continue
                        # No parens — don't expand function-like macro
                        result.append(word)
                        i = j
                        continue
                    else:
                        expanded = macro.body
                        expanded = self._expand_macros(expanded, expanding=expanding | {word})
                        # If expanded result contains our macro name verbatim, the outer
                        # re-scan would re-expand it — instead, leave it as a literal
                        # identifier (blue-paint per C standard).
                        if re.search(r'\b' + re.escape(word) + r'\b', expanded):
                            # Use \x00<word>\x00 sentinel to inhibit further expansion
                            expanded = re.sub(r'\b' + re.escape(word) + r'\b',
                                             '\x00' + word + '\x00', expanded)
                        result.append(expanded)
                        i = j
                        continue
                else:
                    result.append(word)
                    i = j
                    continue

            result.append(ch)
            i += 1

        final = ''.join(result)
        # Re-scan: if expansion changed the line and there are still macros, re-expand
        if final != line and depth < 20:
            return self._expand_macros(final, depth + 1, expanding=expanding)
        return final

    def _parse_macro_args(self, line: str, start: int) -> Tuple[List[str], int]:
        """Parse macro arguments starting from '('. Returns (args, end_pos)."""
        assert line[start] == '('
        i = start + 1
        depth = 1
        args = []
        current = []

        while i < len(line) and depth > 0:
            ch = line[i]
            # Skip over string and char literals (don't count their parens/commas)
            if ch == '"' or ch == "'":
                quote = ch
                current.append(ch)
                i += 1
                while i < len(line) and line[i] != quote:
                    if line[i] == '\\' and i + 1 < len(line):
                        current.append(line[i])
                        i += 1
                    current.append(line[i])
                    i += 1
                if i < len(line):
                    current.append(line[i])
                    i += 1
                continue
            if ch == '(':
                depth += 1
                current.append(ch)
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    args.append(''.join(current).strip())
                    i += 1
                    break
                current.append(ch)
            elif ch == ',' and depth == 1:
                args.append(''.join(current).strip())
                current = []
            else:
                current.append(ch)
            i += 1

        return args, i

    _SUPPORTED_BUILTINS = {
        "__builtin_bswap16", "__builtin_bswap32", "__builtin_bswap64",
        "__builtin_va_start", "__builtin_va_end", "__builtin_va_arg",
        "__builtin_va_copy", "__builtin_alloca", "__builtin_expect",
        "__builtin_offsetof",
        "__builtin_popcount", "__builtin_popcountl", "__builtin_popcountll",
        "__builtin_clz", "__builtin_clzl", "__builtin_clzll",
        "__builtin_ctz", "__builtin_ctzl", "__builtin_ctzll",
        "__builtin_constant_p",
    }

    def _eval_if_expr(self, expr: str) -> bool:
        """Evaluate a simple #if expression."""
        # Handle __has_builtin(name)
        expr = re.sub(r'__has_builtin\s*\(\s*(\w+)\s*\)',
                       lambda m: '1' if m.group(1) in self._SUPPORTED_BUILTINS else '0', expr)
        # Handle defined(NAME) and defined NAME
        # __has_builtin itself counts as "defined"
        expr = re.sub(r'defined\s*\(\s*(\w+)\s*\)',
                       lambda m: '1' if m.group(1) in self.macros or m.group(1) == '__has_builtin' else '0', expr)
        expr = re.sub(r'defined\s+(\w+)',
                       lambda m: '1' if m.group(1) in self.macros or m.group(1) == '__has_builtin' else '0', expr)

        # Expand macros in the expression
        expr = self._expand_macros(expr)

        # Re-apply __has_builtin substitution after macro expansion
        # (macros that wrap __has_builtin only produce it after expansion)
        expr = re.sub(r'__has_builtin\s*\(\s*(\w+)\s*\)',
                       lambda m: '1' if m.group(1) in self._SUPPORTED_BUILTINS else '0', expr)

        # Replace remaining identifiers with 0 (per C standard)
        expr = re.sub(r'\b[a-zA-Z_]\w*\b', '0', expr)

        try:
            return bool(self._eval_c_expr(expr))
        except Exception:
            return False

    def _eval_c_expr(self, expr: str) -> int:
        """Evaluate a C integer constant expression (for #if)."""
        # Tokenize: integers (hex, octal, decimal with optional suffix),
        # operators, parens
        tokens = []
        i = 0
        expr = expr.strip()
        while i < len(expr):
            if expr[i].isspace():
                i += 1
                continue
            # Integer literal
            if expr[i].isdigit():
                j = i
                if expr[i] == '0' and i + 1 < len(expr) and expr[i + 1] in 'xX':
                    j = i + 2
                    while j < len(expr) and (expr[j] in '0123456789abcdefABCDEF'):
                        j += 1
                elif expr[i] == '0' and i + 1 < len(expr) and expr[i + 1].isdigit():
                    j = i + 1
                    while j < len(expr) and expr[j] in '01234567':
                        j += 1
                else:
                    while j < len(expr) and expr[j].isdigit():
                        j += 1
                num_str = expr[i:j]
                # Skip suffix
                while j < len(expr) and expr[j] in 'uUlL':
                    j += 1
                tokens.append(('NUM', int(num_str, 0)))
                i = j
                continue
            # Char literal
            if expr[i] == "'":
                j = i + 1
                if j < len(expr) and expr[j] == '\\':
                    j += 2
                else:
                    j += 1
                if j < len(expr) and expr[j] == "'":
                    ch = expr[i + 1:j]
                    if ch.startswith('\\'):
                        esc = {'n': 10, 't': 9, 'r': 13, '0': 0, '\\': 92, "'": 39, '"': 34}
                        val = esc.get(ch[1], ord(ch[1]))
                    else:
                        val = ord(ch)
                    tokens.append(('NUM', val))
                    i = j + 1
                    continue
            # Two-char operators
            if i + 1 < len(expr):
                two = expr[i:i + 2]
                if two in ('||', '&&', '==', '!=', '<=', '>=', '<<', '>>'):
                    tokens.append(('OP', two))
                    i += 2
                    continue
            # Single char operators/parens
            if expr[i] in '+-*/%<>!~^|&?:()':
                tokens.append(('OP', expr[i]))
                i += 1
                continue
            # Unknown identifier (should be 0 per C standard, already replaced)
            if expr[i].isalpha() or expr[i] == '_':
                j = i
                while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                    j += 1
                tokens.append(('NUM', 0))
                i = j
                continue
            i += 1

        pos = [0]

        def peek():
            return tokens[pos[0]] if pos[0] < len(tokens) else ('END', None)

        def advance():
            t = peek()
            pos[0] += 1
            return t

        def expect_op(op):
            t = advance()
            if t != ('OP', op):
                raise ValueError(f"expected {op}")

        # Recursive descent with standard C precedence
        def parse_ternary():
            val = parse_or()
            if peek() == ('OP', '?'):
                advance()
                then_val = parse_ternary()
                expect_op(':')
                else_val = parse_ternary()
                return then_val if val else else_val
            return val

        def parse_or():
            val = parse_and()
            while peek() == ('OP', '||'):
                advance()
                rhs = parse_and()
                val = 1 if (val or rhs) else 0
            return val

        def parse_and():
            val = parse_bitor()
            while peek() == ('OP', '&&'):
                advance()
                rhs = parse_bitor()
                val = 1 if (val and rhs) else 0
            return val

        def parse_bitor():
            val = parse_bitxor()
            while peek() == ('OP', '|'):
                advance()
                val |= parse_bitxor()
            return val

        def parse_bitxor():
            val = parse_bitand()
            while peek() == ('OP', '^'):
                advance()
                val ^= parse_bitand()
            return val

        def parse_bitand():
            val = parse_equality()
            while peek() == ('OP', '&'):
                advance()
                val &= parse_equality()
            return val

        def parse_equality():
            val = parse_relational()
            while peek()[1] in ('==', '!='):
                op = advance()[1]
                rhs = parse_relational()
                val = int(val == rhs) if op == '==' else int(val != rhs)
            return val

        def parse_relational():
            val = parse_shift()
            while peek()[1] in ('<', '>', '<=', '>='):
                op = advance()[1]
                rhs = parse_shift()
                if op == '<': val = int(val < rhs)
                elif op == '>': val = int(val > rhs)
                elif op == '<=': val = int(val <= rhs)
                elif op == '>=': val = int(val >= rhs)
            return val

        def parse_shift():
            val = parse_additive()
            while peek()[1] in ('<<', '>>'):
                op = advance()[1]
                rhs = parse_additive()
                val = (val << rhs) if op == '<<' else (val >> rhs)
            return val

        def parse_additive():
            val = parse_multiplicative()
            while peek()[1] in ('+', '-'):
                op = advance()[1]
                rhs = parse_multiplicative()
                val = (val + rhs) if op == '+' else (val - rhs)
            return val

        def parse_multiplicative():
            val = parse_unary()
            while peek()[1] in ('*', '/', '%'):
                op = advance()[1]
                rhs = parse_unary()
                if op == '*': val = val * rhs
                elif op == '/': val = val // rhs if rhs != 0 else 0
                elif op == '%': val = val % rhs if rhs != 0 else 0
            return val

        def parse_unary():
            if peek() == ('OP', '!'):
                advance()
                return int(not parse_unary())
            if peek() == ('OP', '-'):
                advance()
                return -parse_unary()
            if peek() == ('OP', '+'):
                advance()
                return parse_unary()
            if peek() == ('OP', '~'):
                advance()
                return ~parse_unary()
            return parse_primary()

        def parse_primary():
            if peek() == ('OP', '('):
                advance()
                val = parse_ternary()
                if peek() == ('OP', ')'):
                    advance()
                return val
            t = advance()
            if t[0] == 'NUM':
                return t[1]
            return 0

        return parse_ternary()


class Macro:
    def __init__(self, name: str, params: List[str] = None,
                 body: str = "", is_func: bool = False,
                 is_variadic: bool = False):
        self.name = name
        self.params = params or []
        self.body = body
        self.is_func = is_func
        self.is_variadic = is_variadic

    def expand(self, args: List[str] = None, raw_args: List[str] = None) -> str:
        if not self.is_func:
            return self.body

        args = args or []
        raw_args = raw_args or args
        result = self.body

        # Build param->arg mapping (expanded for substitution, raw for stringify)
        param_map = {}
        raw_param_map = {}
        for i, param in enumerate(self.params):
            if i < len(args):
                param_map[param] = args[i]
            if i < len(raw_args):
                raw_param_map[param] = raw_args[i]

        # Handle __VA_ARGS__ for variadic macros
        if self.is_variadic:
            va_args = ', '.join(args[len(self.params):])
            param_map['__VA_ARGS__'] = va_args

        # First: replace all params with placeholders to avoid partial matches
        markers = {}
        all_params = list(self.params)
        if self.is_variadic:
            all_params.append('__VA_ARGS__')
        for i, param in enumerate(all_params):
            markers[param] = f"\x01PARAM{i}\x02"

        # Replace params with markers (whole word)
        temp = result
        for param, marker in markers.items():
            temp = re.sub(r'\b' + re.escape(param) + r'\b', marker, temp)

        # Handle ## (token paste): mark adjacent markers with a no-space sentinel
        # We use '\x03' as an indicator that "no space should be inserted" on that side
        # First insert the sentinel into the markers that are pasted
        # Then strip the ## tokens
        # \x03MARKER means no space before; MARKER\x03 means no space after.
        temp = re.sub(r'\s*##\s*', '\x03', temp)

        # Handle # (stringify): #MARKER -> "arg" (use raw/unexpanded args)
        for param, marker in markers.items():
            if param in raw_param_map:
                arg = raw_param_map[param]
                temp = temp.replace('#' + marker,
                    '"' + arg.replace('\\', '\\\\').replace('"', '\\"') + '"')

        # Replace remaining markers with args.
        # Use regex to look at adjacent \x03 sentinels - if marker is preceded
        # or followed by \x03, don't insert padding spaces on that side.
        # We must do all replacements together (regex with callback) so that
        # an adjacent \x03 stays in place to inform the next replacement.
        marker_to_arg = {}
        for param, marker in markers.items():
            if param in param_map:
                marker_to_arg[marker] = param_map[param]

        if marker_to_arg:
            # Use lookbehind/lookahead so \x03 sentinels aren't consumed and
            # remain visible to neighboring replacements.
            marker_pat = re.compile(
                '(?<=\x03)?(' + '|'.join(re.escape(m) for m in marker_to_arg) + ')'
            )
            # Simpler: handle adjacency via match, look at characters around
            marker_pat = re.compile('(' + '|'.join(re.escape(m) for m in marker_to_arg) + ')')

            def repl(mo):
                m = mo.group(1)
                start, end = mo.start(), mo.end()
                arg = marker_to_arg[m]
                pre_paste = start > 0 and temp[start - 1] == '\x03'
                post_paste = end < len(temp) and temp[end] == '\x03'
                left = '' if pre_paste else ' '
                right = '' if post_paste else ' '
                return left + arg + right

            temp = marker_pat.sub(repl, temp)

        # Drop any remaining \x03 sentinels (between non-marker tokens, e.g. ident##ident)
        temp = temp.replace('\x03', '')

        return temp
