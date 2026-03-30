// TEST: global_2d_array
// DESCRIPTION: Global multi-dimensional arrays must be allocated ROWS*COLS*sizeof(elem) bytes
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
//
// BUG REPORT (codegen.py ~line 293):
//
//   When emitting .bss for a global array with no initialiser, the code only
//   multiplies by the *first* dimension:
//
//       size = decl.type_spec.size_bytes()   # e.g. 4 (int)
//       first = decl.type_spec.array_sizes[0]
//       size *= first.value                  # 4 * 5 = 20  ← wrong for int[5][5]
//
//   For a multi-dimensional array all dimensions must be multiplied:
//
//       for dim in decl.type_spec.array_sizes:
//           size *= dim.value                # 4 * 5 * 5 = 100  ← correct
//
//   Because only 20 bytes are reserved instead of 100, accesses to any row
//   beyond row 0 (e.g. grid[1][c]) overflow into the next global's storage,
//   silently corrupting data.  The local-array allocation path in the same
//   file already loops over all dimensions correctly; the global path needs
//   the same treatment.

int grid[5][5];
int result[5][5];

int main(void) {
    /* Write to every row; rows 1-4 overflow if only 20 bytes are allocated. */
    grid[0][0] = 1;
    grid[1][1] = 2;
    grid[2][2] = 3;
    grid[3][3] = 4;
    grid[4][4] = 5;

    /* Copy to a second global 2-D array to exercise both read and write. */
    int r, c;
    for (r = 0; r < 5; r++) {
        for (c = 0; c < 5; c++) {
            result[r][c] = grid[r][c];
        }
    }

    /* Verify diagonal values survived the round-trip. */
    if (result[0][0] != 1) return 1;
    if (result[1][1] != 2) return 2;
    if (result[2][2] != 3) return 3;
    if (result[3][3] != 4) return 4;
    if (result[4][4] != 5) return 5;

    /* Verify off-diagonal entries are still zero (no corruption). */
    if (grid[0][1] != 0) return 6;
    if (grid[1][0] != 0) return 7;

    return 0;
}
