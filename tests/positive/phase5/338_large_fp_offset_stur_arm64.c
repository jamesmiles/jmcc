/* Regression: local zero-initialized variable at stack offset > 256 bytes
 * from the frame pointer causes jmcc to emit:
 *   stur xzr, [x29, #-N]   where N > 256
 * ARM64 error: "index must be an integer in range [-256, 255]"
 *
 * The STUR instruction uses a 9-bit signed immediate offset (-256..+255).
 * For variables deeper in the frame, jmcc must use:
 *   sub x9, x29, #N
 *   str xzr, [x9]
 *
 * Triggered by src/d_main.c: a function with many int locals followed by
 * a zero-initialized char array, placing the array at [x29, #-424].
 */

int deep_stur_test(void) {
    /* 48 int locals = 192 bytes; pushes the char array below to [x29, #-400+] */
    int a00=1,  a01=2,  a02=3,  a03=4,  a04=5,  a05=6,  a06=7,  a07=8;
    int a08=9,  a09=10, a10=11, a11=12, a12=13, a13=14, a14=15, a15=16;
    int a16=17, a17=18, a18=19, a19=20, a20=21, a21=22, a22=23, a23=24;
    int a24=25, a25=26, a26=27, a27=28, a28=29, a29=30, a30=31, a31=32;
    int a32=33, a33=34, a34=35, a35=36, a36=37, a37=38, a38=39, a39=40;
    int a40=41, a41=42, a42=43, a43=44, a44=45, a45=46, a46=47, a47=48;
    char name[32] = {0};  /* zero-init at deep FP offset — triggers stur xzr [x29, #-N] */
    name[0] = 'X';
    /* sum forces all locals to be live to prevent dead-code elimination */
    return a00+a01+a02+a03+a04+a05+a06+a07+a08+a09+a10+a11+a12+a13+a14+a15+
           a16+a17+a18+a19+a20+a21+a22+a23+a24+a25+a26+a27+a28+a29+a30+a31+
           a32+a33+a34+a35+a36+a37+a38+a39+a40+a41+a42+a43+a44+a45+a46+a47+
           (int)name[0]; /* 1+2+...+48 = 1176 plus 'X'=88 = 1264 */
}

int main(void) {
    return deep_stur_test() == 1264 ? 0 : 1;
}
