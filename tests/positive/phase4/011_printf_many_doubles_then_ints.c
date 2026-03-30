// TEST: printf_many_doubles_then_ints
// DESCRIPTION: printf with 4 doubles then 3 ints assigns all ints to registers
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
//
// BUG REPORT (codegen.py gen_func_call argument distribution loop):
//
//   The loop that pops evaluated arguments from the stack into CPU registers
//   is bounded by min(num_args, 6):
//
//       for i in range(min(num_args, 6)):
//           if arg_is_float[i]: ...xmm_idx...  # (no int_idx after PR #2 fix)
//           else:               ...int_idx...
//
//   This processes only the first 6 arguments BY INDEX.  When floats appear
//   early in the argument list they no longer consume integer register slots
//   (fixed in PR #2), but the loop still exits after index 5.  Any integer
//   argument at index >= 6 is left on the stack even though there are still
//   free integer registers (%rdx, %rcx, %r8, %r9).
//
//   Example: printf(fmt, d0, d1, d2, d3, n0, n1, n2)  — 8 args (indices 0-7)
//     Processed (indices 0-5): fmt->rdi, d0->xmm0, d1->xmm1, d2->xmm2,
//                              d3->xmm3, n0->rsi
//     Left on stack (indices 6-7): n1, n2   <-- but rdx and rcx are free!
//   printf reads %d for n1 from %rdx (zero/unset) and prints 0.
//
//   Fix: the loop must continue past index 6 as long as there are still
//   integer register slots available (int_idx < 6) or XMM slots available
//   (xmm_idx < 8).  One approach: loop over all args and track register
//   availability independently of the argument index:
//
//       int_idx = 0; xmm_idx = 0
//       for i in range(num_args):
//           if arg_is_float[i]:
//               if xmm_idx < 8: pop -> xmm{xmm_idx++}
//               else:           leave on stack (already there)
//           else:
//               if int_idx < 6: pop -> ARG_REGS[int_idx++]
//               else:           leave on stack

#include <stdio.h>

double make_double(void) { return 1.0; }

int main(void) {
    double d0 = make_double();
    double d1 = make_double();
    double d2 = make_double();
    double d3 = make_double();
    int n0 = 10;
    int n1 = 20;
    int n2 = 30;

    char buf[128];
    /* 4 doubles followed by 3 ints: n1 and n2 land at arg indices 6 and 7,
       beyond the min(num_args,6) loop cut-off, so they get left on the stack
       while rdx and rcx remain zero. */
    sprintf(buf, "%.0f %.0f %.0f %.0f %d %d %d",
            d0, d1, d2, d3, n0, n1, n2);

    /* Expected: "1 1 1 1 10 20 30" */
    int ok = (buf[0]=='1' && buf[2]=='1' && buf[4]=='1' && buf[6]=='1' &&
              buf[8]=='1' && buf[9]=='0' &&
              buf[11]=='2' && buf[12]=='0' &&
              buf[14]=='3' && buf[15]=='0' &&
              buf[16]=='\0');
    return ok ? 0 : 1;
}
