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
        "stddef.h": """
typedef long ptrdiff_t;
typedef unsigned long size_t;
typedef int wchar_t;
#define NULL ((void*)0)
#define offsetof(type, member) __builtin_offsetof(type, member)
""",
        "stdint.h": """
typedef signed char int8_t;
typedef short int16_t;
typedef int int32_t;
typedef long int64_t;
typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
typedef unsigned long uint64_t;
typedef long intptr_t;
typedef unsigned long uintptr_t;
typedef long intmax_t;
typedef unsigned long uintmax_t;
#define INT8_MIN (-128)
#define INT8_MAX 127
#define INT16_MIN (-32768)
#define INT16_MAX 32767
#define INT32_MIN (-2147483647-1)
#define INT32_MAX 2147483647
#define INT64_MIN (-9223372036854775807L-1)
#define INT64_MAX 9223372036854775807L
#define UINT8_MAX 255
#define UINT16_MAX 65535
#define UINT32_MAX 4294967295U
#define UINT64_MAX 18446744073709551615UL
""",
        "stdbool.h": """
#define bool _Bool
#define true 1
#define false 0
""",
        "stdarg.h": """
typedef void *va_list;
#define va_start(ap, param) __builtin_va_start(ap, param)
#define va_end(ap) __builtin_va_end(ap)
#define va_arg(ap, type) __builtin_va_arg(ap, type)
#define va_copy(dest, src) __builtin_va_copy(dest, src)
""",
        "limits.h": """
#define CHAR_BIT 8
#define SCHAR_MIN (-128)
#define SCHAR_MAX 127
#define UCHAR_MAX 255
#define CHAR_MIN (-128)
#define CHAR_MAX 127
#define SHRT_MIN (-32768)
#define SHRT_MAX 32767
#define USHRT_MAX 65535
#define INT_MIN (-2147483647-1)
#define INT_MAX 2147483647
#define UINT_MAX 4294967295U
#define LONG_MIN (-9223372036854775807L-1)
#define LONG_MAX 9223372036854775807L
#define ULONG_MAX 18446744073709551615UL
#define LLONG_MIN (-9223372036854775807LL-1)
#define LLONG_MAX 9223372036854775807LL
#define ULLONG_MAX 18446744073709551615ULL
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
        "stdio.h": """
#ifndef _JMCC_STDIO_H
#define _JMCC_STDIO_H
typedef void FILE;
extern FILE *stdin;
extern FILE *stdout;
extern FILE *stderr;
#define SEEK_SET 0
#define SEEK_CUR 1
#define SEEK_END 2
#define BUFSIZ 8192
#endif
""",
        "stdlib.h": """
#ifndef _JMCC_STDLIB_H
#define _JMCC_STDLIB_H
#define EXIT_SUCCESS 0
#define EXIT_FAILURE 1
#define RAND_MAX 2147483647
#endif
""",
        "string.h": """
""",
        "wchar.h": """
#ifndef _JMCC_WCHAR_H
#define _JMCC_WCHAR_H
typedef int wchar_t;
typedef unsigned int wint_t;
#define WEOF ((wint_t)-1)
#endif
""",
        "ctype.h": """
""",
        "assert.h": """
#define assert(x) ((void)0)
""",
        "math.h": """
double sin(double);
double cos(double);
double tan(double);
double sqrt(double);
double fabs(double);
double pow(double, double);
double log(double);
double exp(double);
double floor(double);
double ceil(double);
""",
        "unistd.h": """
#define R_OK 4
#define W_OK 2
#define X_OK 1
#define F_OK 0
int access(const char *path, int mode);
int close(int fd);
int read(int fd, void *buf, unsigned long count);
int write(int fd, const void *buf, unsigned long count);
int lseek(int fd, long offset, int whence);
""",
        "fcntl.h": """
#define O_RDONLY 0
#define O_WRONLY 1
#define O_RDWR 2
#define O_CREAT 64
#define O_TRUNC 512
int open(const char *path, int flags, ...);
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
int stat(const char *path, struct stat *buf);
int fstat(int fd, struct stat *buf);
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
typedef unsigned long sigset_t;
struct sigaction {
    void (*sa_handler)(int);
    sigset_t sa_mask;
    int sa_flags;
    void (*sa_restorer)(void);
};
int sigaction(int signum, const struct sigaction *act, struct sigaction *oldact);
sighandler_t signal(int signum, sighandler_t handler);
#define SA_RESTART 0x10000000
#define SA_NODEFER 0x40000000
#define SA_RESETHAND 0x80000000
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
        "X11/Xlib.h": """
typedef struct _XDisplay Display;
typedef unsigned long Window;
typedef unsigned long Drawable;
typedef unsigned long Pixmap;
typedef unsigned long Colormap;
typedef unsigned long Atom;
typedef unsigned long Time;
typedef unsigned long KeySym;
typedef unsigned long Cursor;
typedef unsigned char KeyCode;
typedef struct { int type; unsigned long serial; int send_event; Display *display; Window window; } XAnyEvent;
typedef struct { int type; unsigned long serial; int send_event; Display *display; Window window; Window root; Window subwindow; Time time; int x; int y; int x_root; int y_root; unsigned int state; unsigned int keycode; int same_screen; } XKeyEvent;
typedef struct { int type; unsigned long serial; int send_event; Display *display; Window window; Window root; Window subwindow; Time time; int x; int y; int x_root; int y_root; unsigned int state; unsigned int button; int same_screen; } XButtonEvent;
typedef struct { int type; unsigned long serial; int send_event; Display *display; Window window; Window root; Window subwindow; Time time; int x; int y; int x_root; int y_root; unsigned int state; char is_hint; int same_screen; } XMotionEvent;
typedef struct { int type; unsigned long serial; int send_event; Display *display; Window window; int x; int y; int width; int height; int count; } XExposeEvent;
typedef struct { int type; unsigned long serial; int send_event; Display *display; Window window; int width; int height; } XConfigureEvent;
typedef union { int type; XAnyEvent xany; XKeyEvent xkey; XButtonEvent xbutton; XMotionEvent xmotion; XExposeEvent xexpose; XConfigureEvent xconfigure; } XEvent;
typedef struct { int function; unsigned long foreground; unsigned long background; } XGCValues;
typedef struct { unsigned long event_mask; Colormap colormap; } XSetWindowAttributes;
typedef struct { unsigned long pixel; } XColor;
typedef struct _XGC *GC;
typedef struct { int x, y; unsigned int width, height; } XWindowAttributes;
typedef struct { int width, height; } XSizeHints;
typedef struct { unsigned long visualid; int screen; int depth; int class; } Visual;
typedef struct { Visual *visual; unsigned long visualid; int screen; int depth; int class; } XVisualInfo;
typedef struct { int width, height; int xoffset; int format; char *data; int byte_order; int bitmap_unit; int bitmap_bit_order; int bitmap_pad; int depth; int bytes_per_line; int bits_per_pixel; } XImage;
#define KeyPress 2
#define KeyRelease 3
#define ButtonPress 4
#define ButtonRelease 5
#define MotionNotify 6
#define Expose 12
#define ConfigureNotify 22
#define KeyPressMask (1L<<0)
#define KeyReleaseMask (1L<<1)
#define ButtonPressMask (1L<<2)
#define ButtonReleaseMask (1L<<3)
#define PointerMotionMask (1L<<6)
#define ExposureMask (1L<<15)
#define StructureNotifyMask (1L<<17)
#define FocusChangeMask (1L<<21)
#define Button1 1
#define Button2 2
#define Button3 3
#define Button1Mask (1<<8)
#define Button2Mask (1<<9)
#define Button3Mask (1<<10)
#define CWBorderPixel (1L<<3)
#define CWColormap (1L<<13)
#define CWEventMask (1L<<11)
#define InputOutput 1
#define GCGraphicsExposures (1L<<16)
#define GCForeground (1L<<2)
#define GCBackground (1L<<3)
#define AllocAll 1
#define AllocNone 0
#define ZPixmap 2
#define GrabModeAsync 1
#define CurrentTime 0L
#define GXclear 0x0
#define GXcopy 0x3
#define None 0L
#define TrueColor 4
#define True 1
#define False 0
Display *XOpenDisplay(const char *name);
int XCloseDisplay(Display *dpy);
""",
        "X11/Xutil.h": """
/* XSizeHints and XVisualInfo already in Xlib.h */
""",
        "X11/keysym.h": """
#define XK_BackSpace 0xff08
#define XK_Tab 0xff09
#define XK_Return 0xff0d
#define XK_Escape 0xff1b
#define XK_Delete 0xffff
#define XK_Home 0xff50
#define XK_Left 0xff51
#define XK_Up 0xff52
#define XK_Right 0xff53
#define XK_Down 0xff54
#define XK_Prior 0xff55
#define XK_Next 0xff56
#define XK_End 0xff57
#define XK_Insert 0xff63
#define XK_F1 0xffbe
#define XK_F2 0xffbf
#define XK_F3 0xffc0
#define XK_F4 0xffc1
#define XK_F5 0xffc2
#define XK_F6 0xffc3
#define XK_F7 0xffc4
#define XK_F8 0xffc5
#define XK_F9 0xffc6
#define XK_F10 0xffc7
#define XK_F11 0xffc8
#define XK_F12 0xffc9
#define XK_KP_0 0xffb0
#define XK_KP_Enter 0xff8d
#define XK_KP_Add 0xffab
#define XK_KP_Subtract 0xffad
#define XK_KP_Equal 0xffbd
#define XK_Num_Lock 0xff7f
#define XK_Caps_Lock 0xffe5
#define XK_Scroll_Lock 0xff14
#define XK_Shift_R 0xffe2
#define XK_Shift_L 0xffe1
#define XK_Control_R 0xffe4
#define XK_Control_L 0xffe3
#define XK_Alt_R 0xffea
#define XK_Alt_L 0xffe9
#define XK_Meta_R 0xffe8
#define XK_Meta_L 0xffe7
#define XK_Pause 0xff13
#define XK_space 0x0020
#define XK_equal 0x003d
#define XK_minus 0x002d
#define XK_asciitilde 0x007e
""",
        "X11/extensions/XShm.h": """
typedef struct {
    unsigned long shmseg;
    int shmid;
    char *shmaddr;
    int readOnly;
} XShmSegmentInfo;
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
        "sys/ipc.h": """
typedef int key_t;
#define IPC_PRIVATE ((key_t)0)
#define IPC_CREAT 512
#define IPC_EXCL 1024
#define IPC_RMID 0
#define IPC_STAT 2
""",
        "sys/shm.h": """
#define SHM_RDONLY 010000
struct shmid_ds {
    long shm_segsz;
    long shm_atime;
    long shm_dtime;
    long shm_ctime;
    unsigned short shm_cpid;
    unsigned short shm_lpid;
    unsigned short shm_nattch;
};
int shmget(int key, unsigned long size, int shmflg);
void *shmat(int shmid, const void *shmaddr, int shmflg);
int shmdt(const void *shmaddr);
int shmctl(int shmid, int cmd, struct shmid_ds *buf);
""",
        "errno.h": """
extern int errno;
#define EWOULDBLOCK 11
#define EAGAIN 11
#define ECONNREFUSED 111
#define ECONNRESET 104
#define ERANGE 34
""",
        "values.h": """
#define MININT (-2147483647-1)
#define MAXINT 2147483647
#define MINSHORT (-32768)
#define MAXSHORT 32767
""",
    }

    def __init__(self, filename: str = "<stdin>", include_paths: List[str] = None):
        self.filename = filename
        self.include_paths = include_paths or []
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
        self.macros["NULL"] = Macro("NULL", body="((void*)0)")
        self.macros["EOF"] = Macro("EOF", body="(-1)")
        self.macros["__LP64__"] = Macro("__LP64__", body="1")

    def preprocess(self, source: str, filename: str = None) -> str:
        if filename:
            self.filename = filename
        # Phase 2: splice lines (backslash-newline removal)
        source = source.replace('\\\n', '')
        lines = source.split('\n')
        output = []
        self._process_lines(lines, output, filename or self.filename)
        return '\n'.join(output)

    def _process_lines(self, lines: List[str], output: List[str],
                       filename: str, if_stack: List[dict] = None):
        if if_stack is None:
            if_stack = []

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

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
                    self._handle_define(' '.join(directive[1:]), stripped)
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
                    output.append("")
                else:
                    output.append("")
            elif active:
                # Regular line — expand macros
                self._current_line = i + 1
                self._current_file = filename
                expanded = self._expand_macros(line)
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
            # Strip trailing // comments from body
            in_str = False
            for ci in range(len(body)):
                if body[ci] == '"' and (ci == 0 or body[ci-1] != '\\'):
                    in_str = not in_str
                elif not in_str and body[ci:ci+2] == '//':
                    body = body[:ci].rstrip()
                    break
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
        # Strip trailing // comments (outside string literals)
        in_str = False
        for ci in range(len(body)):
            if body[ci] == '"' and (ci == 0 or body[ci-1] != '\\'):
                in_str = not in_str
            elif not in_str and body[ci:ci+2] == '//':
                body = body[:ci].rstrip()
                break
        self.macros[name] = Macro(name, body=body)

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

        # For quoted includes, search relative to current file
        if current_file and current_file != "<stdin>":
            dir_path = os.path.dirname(current_file)
            full = os.path.join(dir_path, inc_name)
            if os.path.exists(full):
                if full in self.included_files:
                    return ""  # already included
                self.included_files.add(full)
                with open(full) as f:
                    return f.read().replace('\\\n', '')

        # Search include paths
        for path in self.include_paths:
            full = os.path.join(path, inc_name)
            if os.path.exists(full):
                if full in self.included_files:
                    return ""
                self.included_files.add(full)
                with open(full) as f:
                    return f.read().replace('\\\n', '')

        return ""

    def _expand_macros(self, line: str, depth=0) -> str:
        """Expand macros in a line of text."""
        if not self.macros or depth > 20:
            return line

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

                if word == "__LINE__":
                    result.append(str(getattr(self, '_current_line', 0)))
                    i = j
                    continue
                elif word == "__FILE__":
                    result.append(f'"{getattr(self, "_current_file", "<unknown>")}"')
                    i = j
                    continue
                elif word in self.macros:
                    macro = self.macros[word]
                    if macro.is_func:
                        # Function-like macro — look for (args)
                        k = j
                        while k < len(line) and line[k] in ' \t':
                            k += 1
                        if k < len(line) and line[k] == '(':
                            args, end = self._parse_macro_args(line, k)
                            # Pre-expand args (unless used with ## in the body)
                            if '##' not in macro.body:
                                args = [self._expand_macros(a) for a in args]
                            expanded = macro.expand(args)
                            expanded = self._expand_macros(expanded)  # recursive
                            result.append(expanded)
                            i = end
                            continue
                        # No parens — don't expand function-like macro
                        result.append(word)
                        i = j
                        continue
                    else:
                        expanded = macro.body
                        expanded = self._expand_macros(expanded)
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
            return self._expand_macros(final, depth + 1)
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

    def _eval_if_expr(self, expr: str) -> bool:
        """Evaluate a simple #if expression."""
        # Handle defined(NAME) and defined NAME
        expr = re.sub(r'defined\s*\(\s*(\w+)\s*\)',
                       lambda m: '1' if m.group(1) in self.macros else '0', expr)
        expr = re.sub(r'defined\s+(\w+)',
                       lambda m: '1' if m.group(1) in self.macros else '0', expr)

        # Expand macros in the expression
        expr = self._expand_macros(expr)

        # Replace remaining identifiers with 0 (per C standard)
        expr = re.sub(r'\b[a-zA-Z_]\w*\b', '0', expr)

        # Simple evaluation
        try:
            # Safe eval with only integer ops
            expr = expr.replace('&&', ' and ').replace('||', ' or ').replace('!', ' not ')
            result = eval(expr, {"__builtins__": {}}, {})
            return bool(result)
        except Exception:
            return False


class Macro:
    def __init__(self, name: str, params: List[str] = None,
                 body: str = "", is_func: bool = False,
                 is_variadic: bool = False):
        self.name = name
        self.params = params or []
        self.body = body
        self.is_func = is_func
        self.is_variadic = is_variadic

    def expand(self, args: List[str] = None) -> str:
        if not self.is_func:
            return self.body

        args = args or []
        result = self.body

        # Build param->arg mapping
        param_map = {}
        for i, param in enumerate(self.params):
            if i < len(args):
                param_map[param] = args[i]

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

        # Handle ## (token paste): remove ## and join adjacent markers
        temp = re.sub(r'\s*##\s*', '', temp)

        # Handle # (stringify): #MARKER -> "arg"
        for param, marker in markers.items():
            if param in param_map:
                arg = param_map[param]
                temp = temp.replace('#' + marker,
                    '"' + arg.replace('\\', '\\\\').replace('"', '\\"') + '"')

        # Replace remaining markers with args
        for param, marker in markers.items():
            if param in param_map:
                arg = param_map[param]
                # For ## paste: if arg is empty, use space to prevent token merging
                if arg == "" and '##' in self.body:
                    temp = temp.replace(marker, ' ')
                else:
                    temp = temp.replace(marker, arg)

        return temp
