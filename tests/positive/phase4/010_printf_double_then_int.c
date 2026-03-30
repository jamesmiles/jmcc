// TEST: printf_double_then_int
// DESCRIPTION: printf with double args followed by int args uses correct registers
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
//
// BUG REPORT (codegen.py ~line 1799):
//
//   When distributing arguments to a function call from the evaluation stack
//   into registers, floating-point (double) arguments are placed in BOTH an
//   XMM register AND an integer register:
//
//       if arg_is_float[i]:
//           self.emit(f"    movq %rax, %xmm{xmm_idx}")
//           xmm_idx += 1
//           self.emit(f"    movq %rax, {ARG_REGS_64[int_idx]}")  # ← wrong
//           int_idx += 1                                          # ← wrong
//
//   According to the System V AMD64 ABI, floating-point arguments are passed
//   ONLY in XMM registers; they do NOT consume an integer register slot.
//   Doing so displaces subsequent integer arguments into the wrong registers.
//
//   For example, printf("%.0f %.0f %d\n", x, y, n):
//     Generated:  rdi=fmt, xmm0=x, rsi=x, xmm1=y, rdx=y, rcx=n
//     Correct:    rdi=fmt, xmm0=x,         xmm1=y,         rsi=n
//
//   printf reads %d from %rsi (the first integer variadic register after the
//   format string), which contains x's bit-pattern instead of n.  For x=3.0,
//   the lower 32 bits of the IEEE-754 representation are 0, so %d prints 0.
//
//   Fix: increment only xmm_idx (not int_idx) when the argument is a float:
//
//       if arg_is_float[i]:
//           self.emit(f"    movq %rax, %xmm{xmm_idx}")
//           xmm_idx += 1
//           # do NOT touch int_idx

#include <stdio.h>

double make_double(void) { return 3.0; }

int main(void) {
    double x = make_double();
    double y = make_double();
    int n = 7;

    /* With the bug, n is printed using bits from x (lower 32 bits of 3.0 = 0). */
    char buf[64];
    /* Use sprintf so we can compare without relying on printf itself. */
    sprintf(buf, "%.0f %.0f %d", x, y, n);

    /* Expected: "3 3 7" */
    int ok = (buf[0]=='3' && buf[1]==' ' &&
              buf[2]=='3' && buf[3]==' ' &&
              buf[4]=='7' && buf[5]=='\0');
    return ok ? 0 : 1;
}
