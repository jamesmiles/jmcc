# Rosetta Code Test Tracking

C programs from [Rosetta Code](https://rosettacode.org/wiki/Category:C) used as integration tests for jmcc.

Status is based on a full scan against the current jmcc build.

## Status Categories

- **implemented** — test file exists in `tests/external/rosettacode/` (passes jmcc)
- **passes jmcc** — scan confirms jmcc output matches gcc (no test added; self-contained simple enough)
- **breaks jmcc** — compiles with gcc but fails with jmcc (candidate for a future test)
- **skipped** — not a fair jmcc test (external deps, non-deterministic, interactive, argv-dependent, etc.)
- **fetch error** — Rosetta Code page missing, no C section, subpage, etc.

## Summary

| Category | Count |
|----------|-------|
| Total tasks | 1341 |
| Implemented as test | 48 |
| Passes jmcc (no test) | 410 |
| Breaks jmcc | 47 |
| Skipped | 641 |
| Fetch/parse error | 195 |

### Break breakdown

| Type | Count |
|------|-------|
| compile | 25 |
| wrong_output | 12 |
| runtime | 5 |
| exit | 2 |
| SIGSEGV | 2 |
| link | 1 |

### Skip breakdown

| Reason | Count |
|--------|-------|
| requires_math | 169 |
| gcc_compile_fail | 86 |
| non_deterministic | 85 |
| interactive | 68 |
| requires_unistd | 46 |
| requires_gmp | 36 |
| argv0_dependent | 34 |
| requires_file_io | 32 |
| gcc_timeout | 21 |
| requires_pthread | 8 |
| gcc_exit_1 | 8 |
| requires_openssl | 7 |
| windows_only | 7 |
| requires_curl | 7 |
| gcc_exit_-11 | 4 |
| requires_wchar | 4 |
| requires_x11 | 4 |
| requires_opengl | 3 |
| requires_socket | 2 |
| requires_sdl | 2 |
| requires_regex | 2 |
| gcc_exit_-6 | 1 |
| requires_complex | 1 |
| gcc_exit_255 | 1 |
| gcc_exit_-8 | 1 |
| gcc_exit_11 | 1 |
| requires_ncurses | 1 |

## Tasks

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | 100 doors | passes jmcc |  |
| 2 | 100 prisoners | skipped | argv0_dependent |
| 3 | 10001th prime | passes jmcc |  |
| 4 | 15 puzzle game | skipped | non_deterministic |
| 5 | 15 puzzle solver | skipped | requires_math |
| 6 | 2048 | skipped | requires_unistd |
| 7 | 21 game | skipped | non_deterministic |
| 8 | 24 game | skipped | non_deterministic |
| 9 | 24 game/Solve | breaks jmcc | compile: 86:2: error: expected declaration, got ';' |
| 10 | 4-rings or 4-squares puzzle | breaks jmcc | compile: 98:1: error: expected declaration, got 'main' |
| 11 | 9 billion names of God the integer | skipped | requires_gmp |
| 12 | 99 bottles of beer | passes jmcc |  |
| 13 | A* search algorithm | skipped | requires_math |
| 14 | A+B | fetch_error | page_missing |
| 15 | Abbreviations, automatic | skipped | interactive |
| 16 | Abbreviations, easy | implemented | abbreviations_easy.c |
| 17 | Abbreviations, simple | passes jmcc |  |
| 18 | ABC correlation | passes jmcc |  |
| 19 | ABC problem | passes jmcc |  |
| 20 | ABC words | skipped | interactive |
| 21 | Abelian sandpile model | skipped | argv0_dependent |
| 22 | Abstract type | fetch_error | no_main |
| 23 | Abundant odd numbers | skipped | requires_math |
| 24 | Abundant, deficient and perfect number classifications | passes jmcc |  |
| 25 | Accumulator factory | implemented | accumulator_factory.c |
| 26 | Achilles numbers | skipped | requires_math |
| 27 | Ackermann function | skipped | gcc_timeout |
| 28 | Active Directory/Connect | fetch_error | no_main |
| 29 | Active Directory/Search for a user | fetch_error | no_main |
| 30 | Active object | skipped | requires_pthread |
| 31 | Addition chains | skipped | gcc_timeout |
| 32 | Addition-chain exponentiation | skipped | gcc_compile_fail |
| 33 | Additive primes | implemented | additive_primes.c |
| 34 | Address of a variable | fetch_error | no_c_section |
| 35 | Air mass | skipped | requires_math |
| 36 | AKS test for primes | passes jmcc |  |
| 37 | Align columns | fetch_error | no_code_block |
| 38 | Aliquot sequence classifications | skipped | argv0_dependent |
| 39 | Almost prime | implemented | almost_prime.c |
| 40 | Alternade words | skipped | interactive |
| 41 | Amb | skipped | gcc_compile_fail |
| 42 | Amicable pairs | skipped | gcc_exit_-11 |
| 43 | Anadromes | skipped | interactive |
| 44 | Anagrams | skipped | interactive |
| 45 | Anagrams/Deranged anagrams | skipped | requires_unistd |
| 46 | Angle difference between two bearings | skipped | requires_math |
| 47 | Angles (geometric), normalization and conversion | fetch_error | no_main |
| 48 | Animate a pendulum | skipped | requires_opengl |
| 49 | Animated Spinners | skipped | gcc_compile_fail |
| 50 | Animation | skipped | gcc_compile_fail |
| 51 | Anonymous recursion | breaks jmcc | compile: 24:28: error: expected ';', got '{' (LBRACE) |
| 52 | Anti-primes | passes jmcc |  |
| 53 | Append a record to the end of a text file | skipped | interactive |
| 54 | Append numbers at same position in strings | passes jmcc |  |
| 55 | Apply a callback to an array | fetch_error | no_main |
| 56 | Apply a digital filter (direct form II transposed) | skipped | argv0_dependent |
| 57 | Approximate equality | skipped | requires_math |
| 58 | Arbitrary-precision integers (included) | skipped | requires_gmp |
| 59 | Archimedean spiral | skipped | requires_math |
| 60 | Arena storage pool | fetch_error | no_main |
| 61 | Arithmetic derivative | breaks jmcc | wrong_output: 1562b vs 1562b |
| 62 | Arithmetic evaluation | fetch_error | no_code_block |
| 63 | Arithmetic numbers | passes jmcc |  |
| 64 | Arithmetic-geometric mean | skipped | requires_math |
| 65 | Arithmetic-geometric mean/Calculate Pi | skipped | gcc_compile_fail |
| 66 | Arithmetic/Complex | fetch_error | no_main |
| 67 | Arithmetic/Integer | skipped | gcc_exit_1 |
| 68 | Arithmetic/Rational | breaks jmcc | compile: 69:96: error: expected declaration, got ';' |
| 69 | Array concatenation | skipped | gcc_compile_fail |
| 70 | Array length | passes jmcc |  |
| 71 | Arrays | fetch_error | no_main |
| 72 | Ascending primes | skipped | requires_math |
| 73 | ASCII art diagram converter | passes jmcc |  |
| 74 | ASCII control characters | fetch_error | no_c_section |
| 75 | Aspect oriented programming | fetch_error | no_main |
| 76 | Assertions | skipped | gcc_exit_-6 |
| 77 | Associative array/Creation | fetch_error | no_code_block |
| 78 | Associative array/Iteration | fetch_error | no_code_block |
| 79 | Atomic updates | skipped | requires_pthread |
| 80 | Attractive numbers | passes jmcc |  |
| 81 | Average loop length | skipped | requires_math |
| 82 | Averages/Arithmetic mean | passes jmcc |  |
| 83 | Averages/Mean angle | skipped | requires_math |
| 84 | Averages/Mean time of day | skipped | requires_math |
| 85 | Averages/Median | implemented | averages_median.c |
| 86 | Averages/Mode | passes jmcc |  |
| 87 | Averages/Pythagorean means | skipped | requires_math |
| 88 | Averages/Root mean square | skipped | requires_math |
| 89 | Averages/Simple moving average | fetch_error | no_main |
| 90 | AVL tree | fetch_error | no_c_section |
| 91 | Babbage problem | passes jmcc |  |
| 92 | Bacon cipher | passes jmcc |  |
| 93 | Balanced brackets | skipped | non_deterministic |
| 94 | Balanced ternary | passes jmcc |  |
| 95 | Banker's algorithm | skipped | interactive |
| 96 | Barnsley fern | skipped | non_deterministic |
| 97 | Base 16 numbers needing a to f | passes jmcc |  |
| 98 | Base64 decode data | passes jmcc |  |
| 99 | Base64 encode data | skipped | requires_unistd |
| 100 | Bell numbers | passes jmcc |  |
| 101 | Benford's law | skipped | requires_math |
| 102 | Bernoulli numbers | skipped | requires_gmp |
| 103 | Bernoulli's triangle | passes jmcc |  |
| 104 | Bernstein basis polynomials | passes jmcc |  |
| 105 | Best shuffle | passes jmcc |  |
| 106 | Bilinear interpolation | fetch_error | no_main |
| 107 | Bin given limits | passes jmcc |  |
| 108 | Binary digits | skipped | gcc_compile_fail |
| 109 | Binary search | passes jmcc |  |
| 110 | Binary strings | passes jmcc |  |
| 111 | Binomial transform | passes jmcc |  |
| 112 | Bioinformatics/Base count | passes jmcc |  |
| 113 | Bioinformatics/Sequence mutation | skipped | argv0_dependent |
| 114 | Biorhythms | skipped | requires_math |
| 115 | Birthday problem | skipped | requires_math |
| 116 | Bitcoin/address validation | skipped | requires_openssl |
| 117 | Bitcoin/public point to address | skipped | requires_openssl |
| 118 | Bitmap | fetch_error | no_main |
| 119 | Bitmap/Bresenham's line algorithm | fetch_error | no_main |
| 120 | Bitmap/Bézier curves/Cubic | fetch_error | fetch_error |
| 121 | Bitmap/Bézier curves/Quadratic | fetch_error | fetch_error |
| 122 | Bitmap/Flood fill | skipped | interactive |
| 123 | Bitmap/Histogram | fetch_error | no_main |
| 124 | Bitmap/Midpoint circle algorithm | fetch_error | no_main |
| 125 | Bitmap/PPM conversion through a pipe | fetch_error | no_main |
| 126 | Bitmap/Read a PPM file | fetch_error | no_main |
| 127 | Bitmap/Read an image through a pipe | fetch_error | no_main |
| 128 | Bitmap/Write a PPM file | skipped | requires_file_io |
| 129 | Bitwise IO | skipped | requires_file_io |
| 130 | Bitwise operations | fetch_error | no_main |
| 131 | Blum integer | passes jmcc |  |
| 132 | Boids | fetch_error | no_code_block |
| 133 | Boolean values | fetch_error | no_code_block |
| 134 | Box the compass | passes jmcc |  |
| 135 | Brace expansion | passes jmcc |  |
| 136 | Brazilian numbers | breaks jmcc | runtime: timeout |
| 137 | Brownian tree | skipped | requires_math |
| 138 | Bulls and cows | fetch_error | no_main |
| 139 | Bulls and cows/Player | skipped | non_deterministic |
| 140 | Burrows–Wheeler transform | fetch_error | fetch_error |
| 141 | Bézier curves/Intersections | fetch_error | fetch_error |
| 142 | Caesar cipher | skipped | gcc_compile_fail |
| 143 | Calculating the value of e | skipped | requires_math |
| 144 | Calendar | skipped | interactive |
| 145 | Calendar - for "REAL" programmers | fetch_error | no_main |
| 146 | Call a foreign-language function | skipped | gcc_compile_fail |
| 147 | Call a function | skipped | gcc_compile_fail |
| 148 | Call a function in a shared library | passes jmcc |  |
| 149 | Call an object method | skipped | argv0_dependent |
| 150 | Calmo numbers | passes jmcc |  |
| 151 | CalmoSoft primes | skipped | requires_gmp |
| 152 | Canny edge detector | skipped | requires_math |
| 153 | Canonicalize CIDR | skipped | interactive |
| 154 | Cantor set | passes jmcc |  |
| 155 | Card shuffles | skipped | non_deterministic |
| 156 | Carmichael 3 strong pseudoprimes | passes jmcc |  |
| 157 | Cartesian product of two or more lists | skipped | argv0_dependent |
| 158 | Case-sensitivity of identifiers | passes jmcc |  |
| 159 | Casting out nines | skipped | requires_math |
| 160 | Catalan numbers | passes jmcc |  |
| 161 | Catalan numbers/Pascal's triangle | passes jmcc |  |
| 162 | Catamorphism | passes jmcc |  |
| 163 | Catmull–Clark subdivision surface | fetch_error | fetch_error |
| 164 | Centroid of a set of N-dimensional points | implemented | centroid.c |
| 165 | Change e letters to i in words | skipped | interactive |
| 166 | Changeable words | skipped | interactive |
| 167 | Chaocipher | passes jmcc |  |
| 168 | Chaos game | skipped | requires_math |
| 169 | Character codes | passes jmcc |  |
| 170 | Chat server | skipped | requires_socket |
| 171 | Chebyshev coefficients | skipped | requires_math |
| 172 | Check if a polygon overlaps with a rectangle | passes jmcc |  |
| 173 | Check if two polygons overlap | implemented | check_polygon_overlap.c |
| 174 | Check input device is a terminal | skipped | requires_unistd |
| 175 | Check output device is a terminal | skipped | requires_unistd |
| 176 | Check that file exists | skipped | requires_unistd |
| 177 | Checkpoint synchronization | skipped | requires_unistd |
| 178 | Chemical calculator | passes jmcc |  |
| 179 | Chernick's Carmichael numbers | skipped | requires_gmp |
| 180 | Cheryl's birthday | passes jmcc |  |
| 181 | Chinese remainder theorem | passes jmcc |  |
| 182 | Chinese zodiac | skipped | requires_math |
| 183 | User:Chkas | fetch_error | no_c_section |
| 184 | Cholesky decomposition | skipped | requires_math |
| 185 | Chowla numbers | skipped | gcc_timeout |
| 186 | Cipolla's algorithm | skipped | non_deterministic |
| 187 | Circles of given radius through two points | skipped | requires_math |
| 188 | Circular primes | skipped | requires_gmp |
| 189 | Cistercian numerals | skipped | requires_file_io |
| 190 | Classes | fetch_error | no_main |
| 191 | Closest-pair problem | fetch_error | no_code_block |
| 192 | Closures/Value capture | passes jmcc |  |
| 193 | Code Golf | breaks jmcc | compile: 1:1: error: expected declaration, got 'main' |
| 194 | Collections | fetch_error | no_main |
| 195 | Color Difference CIE ΔE2000 | fetch_error | fetch_error |
| 196 | Color of a screen pixel | fetch_error | no_main |
| 197 | Color quantization | fetch_error | no_main |
| 198 | Color wheel | skipped | requires_math |
| 199 | Colorful numbers | skipped | non_deterministic |
| 200 | Colour bars/Display | skipped | gcc_compile_fail |
| 201 | Colour pinstripe/Display | skipped | gcc_compile_fail |
| 202 | Combinations | passes jmcc |  |
| 203 | Combinations and permutations | skipped | requires_gmp |
| 204 | Combinations with repetitions | implemented | combinations_with_repetitions.c |
| 205 | Comma quibbling | passes jmcc |  |
| 206 | Command-line arguments | skipped | argv0_dependent |
| 207 | Comments | fetch_error | no_main |
| 208 | Common sorted list | passes jmcc |  |
| 209 | Compare a list of strings | fetch_error | no_main |
| 210 | Compare length of two strings | passes jmcc |  |
| 211 | Compare sorting algorithms' performance | fetch_error | no_main |
| 212 | Compile-time calculation | skipped | gcc_compile_fail |
| 213 | Compiler/AST interpreter | skipped | requires_file_io |
| 214 | Compiler/code generator | skipped | requires_file_io |
| 215 | Compiler/lexical analyzer | skipped | requires_file_io |
| 216 | Compiler/Simple file inclusion pre processor | skipped | interactive |
| 217 | Compiler/syntax analyzer | skipped | requires_file_io |
| 218 | Compiler/Verifying syntax | breaks jmcc | compile: 1593:34: error: unterminated character literal |
| 219 | Compiler/virtual machine interpreter | skipped | requires_file_io |
| 220 | Composite numbers k with no single digit factors whose factors are all substrings of k | skipped | gcc_timeout |
| 221 | Compound data type | fetch_error | no_main |
| 222 | Concatenate two primes is also prime | passes jmcc |  |
| 223 | Concurrent computing | skipped | requires_pthread |
| 224 | Conditional structures | fetch_error | no_code_block |
| 225 | Conjugate transpose | skipped | requires_complex |
| 226 | Consecutive primes with ascending or descending differences | passes jmcc |  |
| 227 | Consistent overhead byte stuffing | fetch_error | no_c_section |
| 228 | Constrained random points on a circle | skipped | non_deterministic |
| 229 | Continued fraction | implemented | continued_fraction.c |
| 230 | Continued fraction/Arithmetic/Construct from rational number | passes jmcc |  |
| 231 | Continued fraction/Arithmetic/G(matrix ng, continued fraction n) | skipped | gcc_compile_fail |
| 232 | Continued fraction/Arithmetic/G(matrix ng, continued fraction n1, continued fraction n2) | skipped | requires_math |
| 233 | Convert day count to ordinal date | passes jmcc |  |
| 234 | Convert decimal number to rational | skipped | requires_math |
| 235 | Convert seconds to compound duration | skipped | interactive |
| 236 | Convex hull | passes jmcc |  |
| 237 | Conway's Game of Life | skipped | requires_unistd |
| 238 | Coprime triplets | passes jmcc |  |
| 239 | Coprimes | passes jmcc |  |
| 240 | Copy a string | passes jmcc |  |
| 241 | Copy stdin to stdout | skipped | interactive |
| 242 | CORDIC | skipped | requires_math |
| 243 | Count how many vowels and consonants occur in a string | passes jmcc |  |
| 244 | Count in factors | skipped | gcc_timeout |
| 245 | Count in octal | skipped | gcc_timeout |
| 246 | Count occurrences of a substring | passes jmcc |  |
| 247 | Count the coins | skipped | gcc_exit_-11 |
| 248 | Count the occurrence of each digit in e | passes jmcc |  |
| 249 | Cousin primes | breaks jmcc | wrong_output: 495b vs 506b |
| 250 | Cramer's rule | skipped | requires_math |
| 251 | CRC-32 | skipped | gcc_compile_fail |
| 252 | Create a file | skipped | requires_file_io |
| 253 | Create a file on magnetic tape | skipped | requires_file_io |
| 254 | Create a two-dimensional array at runtime | skipped | interactive |
| 255 | Create an HTML table | skipped | non_deterministic |
| 256 | Create an object at a given address | skipped | non_deterministic |
| 257 | CSV data manipulation | skipped | interactive |
| 258 | CSV to HTML translation | passes jmcc |  |
| 259 | Cuban primes | skipped | requires_math |
| 260 | Cubic special primes | skipped | requires_math |
| 261 | Cumulative standard deviation | fetch_error | no_main |
| 262 | Currency | fetch_error | no_main |
| 263 | Currying | implemented | currying.c |
| 264 | Curzon numbers | passes jmcc |  |
| 265 | CUSIP | skipped | argv0_dependent |
| 266 | Cut a rectangle | implemented | cut_a_rectangle.c |
| 267 | Cycle detection | passes jmcc |  |
| 268 | Damm algorithm | passes jmcc |  |
| 269 | Data Encryption Standard | breaks jmcc | compile: 270:27: error: expected ';', got '[' (LBRACKET) |
| 270 | Date format | skipped | non_deterministic |
| 271 | Date manipulation | passes jmcc |  |
| 272 | Day of the week | passes jmcc |  |
| 273 | Day of the week of Christmas and New Year | passes jmcc |  |
| 274 | Days between dates | skipped | interactive |
| 275 | De Polignac numbers | passes jmcc |  |
| 276 | Deal cards for FreeCell | implemented | deal_cards_freecell.c |
| 277 | Death Star | skipped | requires_unistd |
| 278 | Deceptive numbers | passes jmcc |  |
| 279 | Decision tables | skipped | interactive |
| 280 | Deconvolution/1D | skipped | requires_math |
| 281 | Deconvolution/2D+ | fetch_error | page_missing |
| 282 | Decorate-sort-undecorate idiom | implemented | decorate_sort_undecorate.c |
| 283 | Deepcopy | implemented | deepcopy.c |
| 284 | Delegates | implemented | delegates.c |
| 285 | Delete a file | passes jmcc |  |
| 286 | Department numbers | passes jmcc |  |
| 287 | Descending primes | passes jmcc |  |
| 288 | Detect division by zero | breaks jmcc | compile: 1635:25: error: expected type specifier |
| 289 | Determinant and permanent | implemented | determinant_and_permanent.c |
| 290 | Determine if a string has all the same characters | passes jmcc |  |
| 291 | Determine if a string has all unique characters | passes jmcc |  |
| 292 | Determine if a string is collapsible | skipped | argv0_dependent |
| 293 | Determine if a string is numeric | fetch_error | no_main |
| 294 | Determine if a string is squeezable | skipped | argv0_dependent |
| 295 | Determine if only one instance is running | skipped | requires_unistd |
| 296 | Determine if two triangles overlap | implemented | determine_triangle_overlap.c |
| 297 | Dice game probabilities | passes jmcc |  |
| 298 | Digit fifth powers | skipped | requires_math |
| 299 | Digital root | passes jmcc |  |
| 300 | Digital root/Multiplicative digital root | passes jmcc |  |
| 301 | Dijkstra's algorithm | passes jmcc |  |
| 302 | Dinesman's multiple-dwelling problem | breaks jmcc | compile: 64:49: error: expected declaration, got ';' |
| 303 | Dining philosophers | skipped | requires_pthread |
| 304 | Diophantine linear system solving | skipped | requires_math |
| 305 | Disarium numbers | skipped | requires_math |
| 306 | Discordian date | passes jmcc |  |
| 307 | Discrete Fourier transform | skipped | requires_math |
| 308 | Display a linear combination | skipped | requires_math |
| 309 | Distance and Bearing | skipped | requires_math |
| 310 | Distinct power numbers | skipped | requires_math |
| 311 | Distributed programming | skipped | non_deterministic |
| 312 | Diversity prediction theorem | skipped | non_deterministic |
| 313 | DNS query | skipped | requires_socket |
| 314 | Documentation | fetch_error | no_main |
| 315 | Doomsday rule | passes jmcc |  |
| 316 | Dot product | skipped | requires_file_io |
| 317 | Double twin primes | passes jmcc |  |
| 318 | Doubly-linked list/Definition | fetch_error | no_main |
| 319 | Doubly-linked list/Element definition | fetch_error | no_main |
| 320 | Doubly-linked list/Element insertion | fetch_error | no_main |
| 321 | Doubly-linked list/Traversal | passes jmcc |  |
| 322 | Dragon curve | skipped | requires_math |
| 323 | Draw a clock | skipped | requires_math |
| 324 | Draw a cuboid | skipped | requires_math |
| 325 | Draw a pixel | skipped | gcc_compile_fail |
| 326 | Draw a rotating cube | skipped | gcc_compile_fail |
| 327 | Draw a sphere | skipped | requires_math |
| 328 | Draw pixel 2 | skipped | non_deterministic |
| 329 | Dutch national flag problem | skipped | non_deterministic |
| 330 | Eban numbers | breaks jmcc | runtime: timeout |
| 331 | Echo server | skipped | requires_unistd |
| 332 | Egyptian division | passes jmcc |  |
| 333 | EKG sequence convergence | passes jmcc |  |
| 334 | Element-wise operations | fetch_error | no_main |
| 335 | Elementary cellular automaton | skipped | gcc_timeout |
| 336 | Elementary cellular automaton/Random number generator | passes jmcc |  |
| 337 | Elliptic curve arithmetic | skipped | requires_math |
| 338 | Elliptic Curve Digital Signature Algorithm | skipped | non_deterministic |
| 339 | Emirp primes | passes jmcc |  |
| 340 | Empty directory | skipped | gcc_exit_255 |
| 341 | Empty program | breaks jmcc | compile: 1:1: error: expected declaration, got 'main' |
| 342 | Empty string | fetch_error | no_main |
| 343 | Endless maze | skipped | non_deterministic |
| 344 | Enforced immutability | fetch_error | no_main |
| 345 | Entropy | skipped | requires_math |
| 346 | Entropy/Narcissist | skipped | requires_math |
| 347 | Enumerations | fetch_error | no_main |
| 348 | Environment variables | passes jmcc |  |
| 349 | Equilibrium index | passes jmcc |  |
| 350 | Erdős-Nicolas numbers | fetch_error | fetch_error |
| 351 | Erdős-primes | fetch_error | fetch_error |
| 352 | Esthetic numbers | breaks jmcc | wrong_output: 4296b vs 4326b |
| 353 | Ethiopian multiplication | passes jmcc |  |
| 354 | Euler method | skipped | requires_math |
| 355 | Euler's constant 0.5772... | skipped | requires_math |
| 356 | Euler's identity | skipped | requires_math |
| 357 | Euler's sum of powers conjecture | skipped | non_deterministic |
| 358 | Evaluate binomial coefficients | passes jmcc |  |
| 359 | Even or odd | fetch_error | no_main |
| 360 | Events | skipped | requires_unistd |
| 361 | Evolutionary algorithm | skipped | non_deterministic |
| 362 | Exactly three adjacent 3 in lists | passes jmcc |  |
| 363 | Exceptions | fetch_error | no_main |
| 364 | Exceptions/Catch an exception thrown in a nested call | passes jmcc |  |
| 365 | Executable library | fetch_error | no_main |
| 366 | Execute a Markov algorithm | skipped | requires_unistd |
| 367 | Execute a system command | passes jmcc |  |
| 368 | Execute Brain**** | fetch_error | no_code_block |
| 369 | Execute Computer/Zero | skipped | gcc_compile_fail |
| 370 | Execute HQ9+ | fetch_error | page_missing |
| 371 | Execute SNUSP | fetch_error | no_code_block |
| 372 | Experimental Verification of the NKT Law: Interpolating the Masses of 8 Planets Using NASA Data as of 30–31/12/2024 | fetch_error | fetch_error |
| 373 | Exponentiation operator | passes jmcc |  |
| 374 | Exponentiation order | skipped | requires_math |
| 375 | Extend your language | fetch_error | no_main |
| 376 | Extensible prime generator | skipped | requires_math |
| 377 | Extra primes | passes jmcc |  |
| 378 | Extract file extension | passes jmcc |  |
| 379 | Extreme floating point values | implemented | extreme_floating_point.c |
| 380 | Extreme primes | skipped | requires_gmp |
| 381 | Factorial | fetch_error | no_main |
| 382 | Factorions | passes jmcc |  |
| 383 | Factors of a Mersenne number | breaks jmcc | compile: 12:1: error: expected declaration, got 'main' |
| 384 | Factors of an integer | passes jmcc |  |
| 385 | Fairshare between two and more | skipped | gcc_compile_fail |
| 386 | Farey sequence | implemented | farey_sequence.c |
| 387 | Fast Fourier transform | skipped | requires_math |
| 388 | FASTA format | skipped | requires_file_io |
| 389 | Faulhaber's formula | skipped | requires_gmp |
| 390 | Faulhaber's triangle | passes jmcc |  |
| 391 | Feigenbaum constant calculation | passes jmcc |  |
| 392 | Fermat numbers | skipped | requires_gmp |
| 393 | Fibonacci n-step number sequences | passes jmcc |  |
| 394 | Fibonacci sequence | fetch_error | no_main |
| 395 | Fibonacci word | skipped | requires_math |
| 396 | Fibonacci word/fractal | passes jmcc |  |
| 397 | File extension is in extensions list | skipped | interactive |
| 398 | File input/output | skipped | requires_file_io |
| 399 | File modification time | skipped | non_deterministic |
| 400 | File size | skipped | requires_file_io |
| 401 | File size distribution | skipped | windows_only |
| 402 | Filter | passes jmcc |  |
| 403 | Find adjacent primes which differ by a square integer | passes jmcc |  |
| 404 | Find common directory path | passes jmcc |  |
| 405 | Find first and last set bit of a long integer | skipped | gcc_compile_fail |
| 406 | Find if a point is within a triangle | skipped | requires_math |
| 407 | Find largest left truncatable prime in a given base | skipped | requires_gmp |
| 408 | Find limit of recursion | skipped | gcc_exit_-11 |
| 409 | Find minimum number of coins that make a given value | passes jmcc |  |
| 410 | Find palindromic numbers in both binary and ternary bases | skipped | gcc_timeout |
| 411 | Find prime n such that reversed n is also prime | passes jmcc |  |
| 412 | Find prime numbers of the form n*n*n+2 | fetch_error | page_missing |
| 413 | Find square difference | passes jmcc |  |
| 414 | Find squares n where n+1 is prime | fetch_error | page_missing |
| 415 | Find the intersection of a line with a plane | skipped | interactive |
| 416 | Find the intersection of two lines | skipped | requires_math |
| 417 | Find the last Sunday of each month | skipped | gcc_exit_1 |
| 418 | Find the missing permutation | passes jmcc |  |
| 419 | Find words which contain all the vowels | skipped | interactive |
| 420 | Find words which contains more than 3 e vowels | skipped | interactive |
| 421 | Find words whose first and last three letters are equal | skipped | interactive |
| 422 | Find words with alternating vowels and consonants | skipped | interactive |
| 423 | Finite state machine | skipped | interactive |
| 424 | First 9 prime Fibonacci number | passes jmcc |  |
| 425 | First class environments | passes jmcc |  |
| 426 | First perfect square in base n with n unique digits | skipped | gcc_compile_fail |
| 427 | First power of 2 that has leading decimal digits of 12 | skipped | requires_math |
| 428 | First-class functions | skipped | requires_math |
| 429 | Five weekends | passes jmcc |  |
| 430 | Fivenum | passes jmcc |  |
| 431 | FizzBuzz | fetch_error | no_main |
| 432 | Flatten a list | passes jmcc |  |
| 433 | Flipping bits game | skipped | non_deterministic |
| 434 | Flow-control structures | skipped | gcc_compile_fail |
| 435 | Floyd's triangle | passes jmcc |  |
| 436 | Floyd-Warshall algorithm | skipped | interactive |
| 437 | Forbidden numbers | skipped | requires_math |
| 438 | Forest fire | skipped | requires_pthread |
| 439 | Fork | skipped | requires_unistd |
| 440 | Formal power series | skipped | requires_math |
| 441 | Formatted numeric output | breaks jmcc | compile: 21:1: error: expected declaration, got 'main' |
| 442 | Fortunate numbers | skipped | requires_gmp |
| 443 | Forward difference | passes jmcc |  |
| 444 | Four bit adder | passes jmcc |  |
| 445 | Four is magic | skipped | gcc_compile_fail |
| 446 | Four is the number of letters in the ... | skipped | gcc_compile_fail |
| 447 | Four sides of square | passes jmcc |  |
| 448 | Fractal tree | skipped | requires_sdl |
| 449 | Fraction reduction | skipped | gcc_timeout |
| 450 | Fractran | skipped | requires_gmp |
| 451 | Frobenius numbers | skipped | requires_math |
| 452 | FTP | skipped | gcc_compile_fail |
| 453 | Function composition | skipped | requires_math |
| 454 | Function definition | fetch_error | no_main |
| 455 | Function frequency | skipped | requires_unistd |
| 456 | Function prototype | fetch_error | no_main |
| 457 | Fusc sequence | skipped | gcc_timeout |
| 458 | Galton box animation | skipped | non_deterministic |
| 459 | Gamma function | skipped | requires_math |
| 460 | Gapful numbers | passes jmcc |  |
| 461 | Gauss-Jordan matrix inversion | fetch_error | no_main |
| 462 | Gaussian elimination | skipped | requires_math |
| 463 | Gaussian primes | skipped | requires_file_io |
| 464 | General FizzBuzz | passes jmcc |  |
| 465 | Generate Chess960 starting position | skipped | requires_wchar |
| 466 | Generate lower case ASCII alphabet | passes jmcc |  |
| 467 | Generate random chess position | skipped | requires_math |
| 468 | Generator/Exponential | skipped | gcc_compile_fail |
| 469 | Generic swap | fetch_error | no_main |
| 470 | Get system command output | skipped | requires_file_io |
| 471 | Getting the number of decimal places | passes jmcc |  |
| 472 | Globally replace text in several files | skipped | requires_unistd |
| 473 | Go Fish | fetch_error | no_code_block |
| 474 | Golden ratio/Convergence | skipped | requires_math |
| 475 | Gotchas | fetch_error | no_main |
| 476 | Gray code | fetch_error | no_main |
| 477 | Grayscale image | fetch_error | no_main |
| 478 | Greatest common divisor | fetch_error | no_main |
| 479 | Greatest element of a list | fetch_error | no_main |
| 480 | Greatest subsequential sum | passes jmcc |  |
| 481 | Greedy algorithm for Egyptian fractions | passes jmcc |  |
| 482 | Greyscale bars/Display | skipped | gcc_compile_fail |
| 483 | Guess the number | skipped | non_deterministic |
| 484 | Guess the number/With feedback | skipped | non_deterministic |
| 485 | Guess the number/With feedback (player) | skipped | interactive |
| 486 | GUI component interaction | fetch_error | no_main |
| 487 | GUI enabling/disabling of controls | fetch_error | no_main |
| 488 | GUI/Maximum window dimensions | skipped | windows_only |
| 489 | Hailstone sequence | passes jmcc |  |
| 490 | Halt and catch fire | skipped | gcc_exit_-8 |
| 491 | Hamming numbers | implemented | hamming_numbers.c |
| 492 | Handle a signal | skipped | requires_unistd |
| 493 | Happy numbers | passes jmcc |  |
| 494 | Harmonic series | passes jmcc |  |
| 495 | Harshad or Niven series | passes jmcc |  |
| 496 | Hash from two arrays | skipped | gcc_compile_fail |
| 497 | Haversine formula | skipped | requires_math |
| 498 | Hello world/Graphical | skipped | gcc_compile_fail |
| 499 | Hello world/Line printer | skipped | requires_file_io |
| 500 | Hello world/Newbie | fetch_error | no_code_block |
| 501 | Hello world/Newline omission | passes jmcc |  |
| 502 | Hello world/Standard error | passes jmcc |  |
| 503 | Hello world/Text | passes jmcc |  |
| 504 | Hello world/Web server | skipped | requires_unistd |
| 505 | Heronian triangles | skipped | requires_math |
| 506 | Hex dump | skipped | argv0_dependent |
| 507 | Hickerson series of almost integers | skipped | gcc_compile_fail |
| 508 | Higher-order functions | fetch_error | no_main |
| 509 | Hilbert curve | passes jmcc |  |
| 510 | History variables | breaks jmcc | compile: 120:2: error: expression is not an lvalue |
| 511 | Hofstadter Figure-Figure sequences | passes jmcc |  |
| 512 | Hofstadter Q sequence | passes jmcc |  |
| 513 | Hofstadter-Conway $10,000 sequence | fetch_error | no_main |
| 514 | Holidays related to Easter | breaks jmcc | compile: 107:22: error: expression is not an lvalue |
| 515 | Honaker primes | passes jmcc |  |
| 516 | Honeycombs | skipped | requires_math |
| 517 | Horizontal sundial calculations | skipped | requires_math |
| 518 | Horner's rule for polynomial evaluation | passes jmcc |  |
| 519 | Host introspection | passes jmcc |  |
| 520 | Hostname | fetch_error | no_c_section |
| 521 | Hough transform | fetch_error | no_code_block |
| 522 | HTTP | skipped | requires_curl |
| 523 | HTTPS | skipped | requires_curl |
| 524 | HTTPS/Authenticated | skipped | gcc_compile_fail |
| 525 | Huffman coding | passes jmcc |  |
| 526 | Humble numbers | skipped | gcc_compile_fail |
| 527 | Hunt the Wumpus | skipped | non_deterministic |
| 528 | I before E except after C | skipped | gcc_compile_fail |
| 529 | IBAN | passes jmcc |  |
| 530 | Iccanobif primes | skipped | requires_gmp |
| 531 | Identity matrix | skipped | gcc_exit_1 |
| 532 | Idiomatically determine all the lowercase and uppercase letters | passes jmcc |  |
| 533 | Idoneal numbers | passes jmcc |  |
| 534 | Image convolution | fetch_error | no_main |
| 535 | Image noise | skipped | requires_sdl |
| 536 | Imaginary base numbers | skipped | requires_math |
| 537 | Implicit type conversion | breaks jmcc | compile: 21:1: error: expected declaration, got 'main' |
| 538 | Include a file | fetch_error | no_c_section |
| 539 | Increasing gaps between consecutive Niven numbers | skipped | gcc_compile_fail |
| 540 | Increment a numerical string | passes jmcc |  |
| 541 | Infinity | skipped | requires_math |
| 542 | Inheritance/Multiple | fetch_error | no_main |
| 543 | Inheritance/Single | fetch_error | no_code_block |
| 544 | Input loop | passes jmcc |  |
| 545 | Input/Output for lines of text | skipped | interactive |
| 546 | Input/Output for pairs of numbers | skipped | interactive |
| 547 | Integer comparison | skipped | interactive |
| 548 | Integer overflow | breaks jmcc | exit: gcc=0 jmcc=-8 |
| 549 | Integer roots | skipped | requires_math |
| 550 | Integer sequence | skipped | gcc_timeout |
| 551 | Intersecting number wheels | passes jmcc |  |
| 552 | Introspection | fetch_error | no_main |
| 553 | Inverted index | skipped | interactive |
| 554 | Inverted syntax | breaks jmcc | compile: 43:1: error: expected declaration, got 'main' |
| 555 | IPC via named pipe | skipped | requires_pthread |
| 556 | ISBN13 check digit | passes jmcc |  |
| 557 | Isqrt (integer square root) of X | passes jmcc |  |
| 558 | Iterated digits squaring | passes jmcc |  |
| 559 | Iterators | passes jmcc |  |
| 560 | Jacobi symbol | passes jmcc |  |
| 561 | Jacobsthal numbers | skipped | requires_gmp |
| 562 | Jaro similarity | implemented | jaro_similarity.c |
| 563 | Jensen's Device | implemented | jensens_device.c |
| 564 | Jewels and stones | passes jmcc |  |
| 565 | Jordan-Pólya numbers | fetch_error | fetch_error |
| 566 | JortSort | passes jmcc |  |
| 567 | Josephus problem | passes jmcc |  |
| 568 | Joystick position | skipped | gcc_timeout |
| 569 | JSON | skipped | requires_file_io |
| 570 | Julia set | skipped | requires_math |
| 571 | Jump anywhere | fetch_error | no_main |
| 572 | Just in time processing on a character stream | skipped | requires_file_io |
| 573 | K-d tree | skipped | requires_math |
| 574 | K-means++ clustering | fetch_error | page_missing |
| 575 | Kahan summation | implemented | kahan_summation.c |
| 576 | Kaprekar numbers | passes jmcc |  |
| 577 | Kernighans large earthquake problem | skipped | requires_file_io |
| 578 | Keyboard input/Flush the keyboard buffer | skipped | interactive |
| 579 | Keyboard input/Keypress check | skipped | requires_unistd |
| 580 | Keyboard input/Obtain a Y or N response | skipped | requires_unistd |
| 581 | Keyboard macros | skipped | requires_x11 |
| 582 | Klarner-Rado sequence | passes jmcc |  |
| 583 | Knapsack problem/0-1 | implemented | knapsack_0_1.c |
| 584 | Knapsack problem/Bounded | passes jmcc |  |
| 585 | Knapsack problem/Continuous | passes jmcc |  |
| 586 | Knapsack problem/Unbounded | passes jmcc |  |
| 587 | Knight's tour | skipped | requires_unistd |
| 588 | Knuth shuffle | fetch_error | no_main |
| 589 | Knuth's algorithm S | skipped | non_deterministic |
| 590 | Koch curve | skipped | requires_math |
| 591 | Kolakoski sequence | passes jmcc |  |
| 592 | Kronecker product | skipped | interactive |
| 593 | Kronecker product based fractals | skipped | interactive |
| 594 | Lah numbers | passes jmcc |  |
| 595 | Langton's ant | skipped | requires_unistd |
| 596 | Largest difference between adjacent primes | passes jmcc |  |
| 597 | Largest five adjacent number | skipped | non_deterministic |
| 598 | Largest int from concatenated ints | passes jmcc |  |
| 599 | Largest number divisible by its digits | passes jmcc |  |
| 600 | Largest palindrome product | skipped | gcc_compile_fail |
| 601 | Largest prime factor | passes jmcc |  |
| 602 | Largest product in a grid | passes jmcc |  |
| 603 | Largest proper divisor of n | passes jmcc |  |
| 604 | Last Friday of each month | skipped | gcc_exit_1 |
| 605 | Last letter-first letter | passes jmcc |  |
| 606 | Last list item | passes jmcc |  |
| 607 | Law of cosines - triples | skipped | requires_math |
| 608 | Leap year | passes jmcc |  |
| 609 | Least common multiple | passes jmcc |  |
| 610 | Least m such that n! + m is prime | fetch_error | page_missing |
| 611 | Left factorials | skipped | requires_gmp |
| 612 | Legendre prime counting function | skipped | requires_math |
| 613 | Length of an arc between two angles | skipped | gcc_exit_11 |
| 614 | Leonardo numbers | skipped | interactive |
| 615 | Letter frequency | fetch_error | no_main |
| 616 | Levenshtein distance | passes jmcc |  |
| 617 | Levenshtein distance/Alignment | passes jmcc |  |
| 618 | Line circle intersection | skipped | requires_math |
| 619 | Linear congruential generator | skipped | non_deterministic |
| 620 | Linux CPU utilization | skipped | requires_unistd |
| 621 | List comprehensions | passes jmcc |  |
| 622 | List rooted trees | passes jmcc |  |
| 623 | Literals/Floating point | fetch_error | no_code_block |
| 624 | Literals/Integer | passes jmcc |  |
| 625 | Literals/String | fetch_error | no_main |
| 626 | Logical operations | fetch_error | no_main |
| 627 | Logistic curve fitting in epidemiology | skipped | requires_math |
| 628 | Long multiplication | passes jmcc |  |
| 629 | Long primes | passes jmcc |  |
| 630 | Long stairs | skipped | non_deterministic |
| 631 | Long year | skipped | requires_math |
| 632 | Longest common prefix | implemented | longest_common_prefix.c |
| 633 | Longest common subsequence | fetch_error | no_main |
| 634 | Longest common substring | skipped | gcc_compile_fail |
| 635 | Longest common suffix | skipped | gcc_compile_fail |
| 636 | Longest increasing subsequence | passes jmcc |  |
| 637 | Longest string challenge | skipped | interactive |
| 638 | Longest substrings without repeating characters | passes jmcc |  |
| 639 | Look-and-say sequence | skipped | gcc_timeout |
| 640 | Loop over multiple arrays simultaneously | passes jmcc |  |
| 641 | Loops/Break | skipped | non_deterministic |
| 642 | Loops/Continue | fetch_error | no_main |
| 643 | Loops/Do-while | fetch_error | no_main |
| 644 | Loops/Downward for | fetch_error | no_main |
| 645 | Loops/For | fetch_error | no_main |
| 646 | Loops/For with a specified step | fetch_error | no_main |
| 647 | Loops/Foreach | fetch_error | no_main |
| 648 | Loops/Increment loop index within loop body | breaks jmcc | wrong_output: 1176b vs 1176b |
| 649 | Loops/Infinite | fetch_error | no_main |
| 650 | Loops/N plus one half | passes jmcc |  |
| 651 | Loops/Nested | skipped | non_deterministic |
| 652 | Loops/While | fetch_error | no_main |
| 653 | Loops/With multiple ranges | breaks jmcc | compile: 1696:18: error: expected type specifier |
| 654 | Loops/Wrong ranges | passes jmcc |  |
| 655 | LU decomposition | skipped | requires_math |
| 656 | Lucas-Lehmer test | skipped | requires_gmp |
| 657 | Lucky and even lucky numbers | skipped | gcc_exit_1 |
| 658 | Ludic numbers | passes jmcc |  |
| 659 | Luhn test of credit card numbers | passes jmcc |  |
| 660 | LZW compression | skipped | requires_unistd |
| 661 | MAC vendor lookup | skipped | requires_curl |
| 662 | Machine code | skipped | non_deterministic |
| 663 | Mad Libs | skipped | interactive |
| 664 | Magic 8-ball | skipped | non_deterministic |
| 665 | Magic constant | skipped | requires_math |
| 666 | Magic squares of doubly even order | skipped | argv0_dependent |
| 667 | Magic squares of odd order | skipped | gcc_exit_1 |
| 668 | Magic squares of singly even order | skipped | argv0_dependent |
| 669 | Magnanimous numbers | passes jmcc |  |
| 670 | Main step of GOST 28147-89 | fetch_error | no_main |
| 671 | Make directory path | skipped | argv0_dependent |
| 672 | Man or boy test | implemented | man_or_boy_test.c |
| 673 | Mandelbrot set | skipped | requires_math |
| 674 | Map range | breaks jmcc | compile: 31:43: error: expected ')', got '1' (INT_LITERAL) |
| 675 | Matrix chain multiplication | passes jmcc |  |
| 676 | Matrix digital rain | skipped | requires_unistd |
| 677 | Matrix multiplication | implemented | matrix_multiplication.c |
| 678 | Matrix transposition | implemented | matrix_transposition.c |
| 679 | Matrix with two diagonals | passes jmcc |  |
| 680 | Matrix-exponentiation operator | skipped | requires_math |
| 681 | Maximum difference between adjacent elements of list | skipped | requires_math |
| 682 | Maximum triangle path sum | skipped | requires_math |
| 683 | Mayan numerals | skipped | gcc_exit_1 |
| 684 | Maze generation | skipped | non_deterministic |
| 685 | Maze solving | fetch_error | no_code_block |
| 686 | McNuggets problem | passes jmcc |  |
| 687 | MD4 | fetch_error | no_main |
| 688 | MD5 | skipped | requires_openssl |
| 689 | MD5/Implementation | fetch_error | no_code_block |
| 690 | Median filter | skipped | requires_unistd |
| 691 | Memory allocation | passes jmcc |  |
| 692 | Memory layout of a data structure | fetch_error | no_c_section |
| 693 | Menu | skipped | interactive |
| 694 | Mersenne primes | passes jmcc |  |
| 695 | Mertens function | passes jmcc |  |
| 696 | Metaprogramming | passes jmcc |  |
| 697 | Metered concurrency | skipped | requires_pthread |
| 698 | Metronome | skipped | requires_unistd |
| 699 | Mian-Chowla sequence | skipped | non_deterministic |
| 700 | Middle three digits | passes jmcc |  |
| 701 | Miller-Rabin primality test | fetch_error | no_main |
| 702 | Mind boggling card trick | skipped | non_deterministic |
| 703 | Minesweeper game | skipped | windows_only |
| 704 | Minimum multiple of m where digital sum equals m | passes jmcc |  |
| 705 | Minimum number of cells after, before, above and below NxN squares | passes jmcc |  |
| 706 | Minimum numbers of three lists | passes jmcc |  |
| 707 | Minimum positive multiple in base 10 using only 0 and 1 | breaks jmcc | compile: 2325:1: error: expected declaration, got '__int128' |
| 708 | Minimum primes | passes jmcc |  |
| 709 | Modular arithmetic | passes jmcc |  |
| 710 | Modular exponentiation | skipped | requires_gmp |
| 711 | Modular inverse | passes jmcc |  |
| 712 | Modulinos | skipped | gcc_compile_fail |
| 713 | Monads/List monad | passes jmcc |  |
| 714 | Monads/Maybe monad | passes jmcc |  |
| 715 | Monte Carlo methods | skipped | requires_math |
| 716 | Montgomery reduction | passes jmcc |  |
| 717 | Monty Hall problem | skipped | requires_math |
| 718 | Morpion solitaire | skipped | requires_unistd |
| 719 | Morse code | skipped | interactive |
| 720 | Mosaic matrix | passes jmcc |  |
| 721 | Motor | fetch_error | no_main |
| 722 | Motzkin numbers | passes jmcc |  |
| 723 | Mouse position | skipped | requires_x11 |
| 724 | Move-to-front algorithm | passes jmcc |  |
| 725 | Multi-dimensional array | fetch_error | no_main |
| 726 | Multifactorial | passes jmcc |  |
| 727 | Multiline shebang | fetch_error | no_code_block |
| 728 | Multiple distinct objects | fetch_error | no_main |
| 729 | Multiple regression | skipped | gcc_compile_fail |
| 730 | Multiplication tables | passes jmcc |  |
| 731 | Multiplicative order | skipped | gcc_compile_fail |
| 732 | Multiplicatively perfect numbers | passes jmcc |  |
| 733 | Multisplit | passes jmcc |  |
| 734 | Munchausen numbers | skipped | requires_math |
| 735 | Munching squares | skipped | requires_math |
| 736 | Musical scale | skipped | requires_math |
| 737 | Mutex | fetch_error | no_main |
| 738 | Mutual recursion | passes jmcc |  |
| 739 | Möbius function | fetch_error | fetch_error |
| 740 | N'th | passes jmcc |  |
| 741 | N-body problem | skipped | requires_math |
| 742 | N-grams | passes jmcc |  |
| 743 | N-queens problem | skipped | argv0_dependent |
| 744 | N-smooth numbers | skipped | requires_gmp |
| 745 | Named parameters | passes jmcc |  |
| 746 | Naming conventions | fetch_error | no_main |
| 747 | Narcissist | skipped | interactive |
| 748 | Narcissistic decimal number | skipped | requires_gmp |
| 749 | Native shebang | skipped | requires_unistd |
| 750 | Natural sorting | skipped | requires_wchar |
| 751 | Nautical bell | skipped | requires_unistd |
| 752 | Negative base numbers | breaks jmcc | wrong_output: 388b vs 388b |
| 753 | Nested function | breaks jmcc | compile: 46:17: error: expected ';', got '{' (LBRACE) |
| 754 | Nested templated data | implemented | nested_templated_data.c |
| 755 | Next highest int from digits | passes jmcc |  |
| 756 | Next special primes | passes jmcc |  |
| 757 | Nice primes | passes jmcc |  |
| 758 | Nim game | skipped | interactive |
| 759 | Nimber arithmetic | passes jmcc |  |
| 760 | Non-continuous subsequences | passes jmcc |  |
| 761 | Non-decimal radices/Convert | breaks jmcc | wrong_output: 118b vs 35b |
| 762 | Non-decimal radices/Input | skipped | interactive |
| 763 | Non-decimal radices/Output | passes jmcc |  |
| 764 | Nonoblock | passes jmcc |  |
| 765 | Nth root | passes jmcc |  |
| 766 | Null object | passes jmcc |  |
| 767 | Number names | implemented | number_names.c |
| 768 | Number reversal game | fetch_error | no_main |
| 769 | Numbers divisible by their individual digits, but not by the product of their digits | passes jmcc |  |
| 770 | Numbers in base 10 that are palindromic in bases 2, 4, and 16 | passes jmcc |  |
| 771 | Numbers in base-16 representation that cannot be written with decimal digits | passes jmcc |  |
| 772 | Numbers k whose divisor sum is equal to the divisor sum of k + 1 | fetch_error | page_missing |
| 773 | Numbers which are the cube roots of the product of their proper divisors | passes jmcc |  |
| 774 | Numbers whose binary and ternary digit sums are prime | passes jmcc |  |
| 775 | Numbers whose count of divisors is prime | skipped | gcc_compile_fail |
| 776 | Numbers with equal rises and falls | passes jmcc |  |
| 777 | Numbers with prime digits whose sum is 13 | passes jmcc |  |
| 778 | Numbers with same digit set in base 10 and base 16 | passes jmcc |  |
| 779 | Numeric error propagation | skipped | requires_math |
| 780 | Numeric separator syntax | passes jmcc |  |
| 781 | Numerical integration | fetch_error | no_main |
| 782 | Numerical integration/Adaptive Simpson's method | skipped | requires_math |
| 783 | Numerical integration/Gauss-Legendre Quadrature | skipped | requires_math |
| 784 | Numerical integration/Tanh-Sinh Quadrature | skipped | requires_math |
| 785 | O'Halloran numbers | passes jmcc |  |
| 786 | Odd and square numbers | skipped | requires_math |
| 787 | Odd word problem | passes jmcc |  |
| 788 | Old lady swallowed a fly | passes jmcc |  |
| 789 | Old Russian measure of length | skipped | non_deterministic |
| 790 | One of n lines in a file | skipped | non_deterministic |
| 791 | One-dimensional cellular automata | passes jmcc |  |
| 792 | One-time pad | skipped | non_deterministic |
| 793 | One-two primes | skipped | requires_gmp |
| 794 | OpenGL | skipped | requires_opengl |
| 795 | OpenGL pixel shader | skipped | requires_opengl |
| 796 | OpenGL/Utah teapot | skipped | gcc_compile_fail |
| 797 | Operator precedence | fetch_error | no_code_block |
| 798 | Optional parameters | skipped | requires_file_io |
| 799 | Orbital elements | skipped | requires_math |
| 800 | Order by pair comparisons | skipped | interactive |
| 801 | Order two numerical lists | fetch_error | no_main |
| 802 | Ordered partitions | skipped | gcc_exit_1 |
| 803 | Ordered words | skipped | interactive |
| 804 | Ormiston pairs | skipped | gcc_timeout |
| 805 | Ormiston triples | skipped | gcc_timeout |
| 806 | Own digits power sum | skipped | requires_math |
| 807 | P-value correction | skipped | requires_math |
| 808 | Padovan n-step number sequences | passes jmcc |  |
| 809 | Padovan sequence | skipped | requires_math |
| 810 | Pairs with common factors | passes jmcc |  |
| 811 | Palindrome dates | skipped | non_deterministic |
| 812 | Palindrome detection | fetch_error | no_main |
| 813 | Palindromic gapful numbers | breaks jmcc | SIGSEGV |
| 814 | Palindromic primes | skipped | gcc_compile_fail |
| 815 | Pan base non-primes | passes jmcc |  |
| 816 | Pancake numbers | passes jmcc |  |
| 817 | Pandigital prime | skipped | requires_math |
| 818 | Pangram checker | passes jmcc |  |
| 819 | Paraffins | passes jmcc |  |
| 820 | Parallel brute force | skipped | requires_openssl |
| 821 | Parallel calculations | skipped | gcc_compile_fail |
| 822 | Parameterized SQL statement | skipped | gcc_compile_fail |
| 823 | Parametric polymorphism | skipped | non_deterministic |
| 824 | Parse an IP Address | fetch_error | no_main |
| 825 | Parse command-line arguments | skipped | argv0_dependent |
| 826 | Parsing/RPN calculator algorithm | skipped | requires_math |
| 827 | Parsing/RPN to infix conversion | skipped | argv0_dependent |
| 828 | Parsing/Shunting-yard algorithm | skipped | requires_regex |
| 829 | Partial function application | skipped | requires_unistd |
| 830 | Partition an integer x into n primes | passes jmcc |  |
| 831 | Partition function P | skipped | requires_gmp |
| 832 | Pascal matrix generation | passes jmcc |  |
| 833 | Pascal's triangle | passes jmcc |  |
| 834 | Pascal's triangle/Puzzle | skipped | requires_math |
| 835 | Password generator | skipped | non_deterministic |
| 836 | Pathological floating point problems | skipped | requires_gmp |
| 837 | Peaceful chess queen armies | skipped | requires_math |
| 838 | Peano curve | skipped | gcc_compile_fail |
| 839 | Pell's equation | skipped | requires_math |
| 840 | Penney's game | skipped | non_deterministic |
| 841 | Penta-power prime seeds | skipped | requires_gmp |
| 842 | Pentagram | skipped | requires_math |
| 843 | Percentage difference between images | skipped | requires_math |
| 844 | Percolation/Bond percolation | skipped | non_deterministic |
| 845 | Percolation/Mean cluster density | skipped | non_deterministic |
| 846 | Percolation/Mean run density | skipped | non_deterministic |
| 847 | Percolation/Site percolation | skipped | non_deterministic |
| 848 | Perfect numbers | skipped | gcc_compile_fail |
| 849 | Perfect shuffle | skipped | gcc_compile_fail |
| 850 | Perfect totient numbers | skipped | argv0_dependent |
| 851 | Periodic table | fetch_error | no_main |
| 852 | Perlin noise | skipped | requires_math |
| 853 | Permutation test | passes jmcc |  |
| 854 | Permutations | passes jmcc |  |
| 855 | Permutations by swapping | skipped | argv0_dependent |
| 856 | Permutations with repetitions | passes jmcc |  |
| 857 | Permutations/Derangements | passes jmcc |  |
| 858 | Permutations/Rank of a permutation | passes jmcc |  |
| 859 | Permuted multiples | passes jmcc |  |
| 860 | Pernicious numbers | passes jmcc |  |
| 861 | Phrase reversals | passes jmcc |  |
| 862 | User:Phunanon | fetch_error | no_c_section |
| 863 | Pi | skipped | requires_gmp |
| 864 | Pick random element | skipped | non_deterministic |
| 865 | Pierpont primes | skipped | gcc_compile_fail |
| 866 | Pig the dice game | skipped | non_deterministic |
| 867 | Pig the dice game/Player | skipped | non_deterministic |
| 868 | Pinstripe/Display | skipped | gcc_compile_fail |
| 869 | Piprimes | passes jmcc |  |
| 870 | Plasma effect | skipped | windows_only |
| 871 | Play recorded sounds | fetch_error | no_main |
| 872 | Playing cards | skipped | non_deterministic |
| 873 | Plot coordinate pairs | skipped | requires_math |
| 874 | Pointers and references | fetch_error | no_c_section |
| 875 | Poker hand analyser | breaks jmcc | wrong_output: 269b vs 259b |
| 876 | Pollard's rho algorithm | skipped | requires_math |
| 877 | Polymorphic copy | passes jmcc |  |
| 878 | Polymorphism | fetch_error | no_code_block |
| 879 | Polynomial long division | fetch_error | no_main |
| 880 | Polynomial regression | fetch_error | no_main |
| 881 | Polyspiral | skipped | requires_math |
| 882 | Population count | breaks jmcc | link: undef ref  to `__builtin_popcountll' |
| 883 | Power set | passes jmcc |  |
| 884 | Pragmatic directives | passes jmcc |  |
| 885 | Price fraction | breaks jmcc | exit: gcc=0 jmcc=-6 |
| 886 | Primality by trial division | fetch_error | no_main |
| 887 | Primality by Wilson's theorem | passes jmcc |  |
| 888 | Prime conspiracy | passes jmcc |  |
| 889 | Prime decomposition | skipped | requires_file_io |
| 890 | Prime groups | passes jmcc |  |
| 891 | Prime numbers whose neighboring pairs are tetraprimes | skipped | gcc_compile_fail |
| 892 | Prime reciprocal sum | skipped | requires_gmp |
| 893 | Prime triangle | skipped | non_deterministic |
| 894 | Primes - allocate descendants to their ancestors | skipped | requires_math |
| 895 | Primes whose first and last number is 3 | skipped | requires_math |
| 896 | Primes whose sum of digits is 25 | passes jmcc |  |
| 897 | Primorial numbers | skipped | requires_math |
| 898 | Print debugging statement | passes jmcc |  |
| 899 | Priority queue | passes jmcc |  |
| 900 | Probabilistic choice | skipped | non_deterministic |
| 901 | Problem of Apollonius | skipped | gcc_compile_fail |
| 902 | Product of divisors | skipped | requires_math |
| 903 | Product of min and max prime factors | passes jmcc |  |
| 904 | Program name | skipped | argv0_dependent |
| 905 | Program termination | skipped | gcc_compile_fail |
| 906 | Proper divisors | passes jmcc |  |
| 907 | Pseudo-random numbers/Combined recursive generator MRG32k3a | skipped | requires_math |
| 908 | Pseudo-random numbers/Middle-square method | passes jmcc |  |
| 909 | Pseudo-random numbers/PCG32 | skipped | requires_math |
| 910 | Pseudo-random numbers/Splitmix64 | skipped | requires_math |
| 911 | Pseudo-random numbers/Xorshift star | skipped | requires_math |
| 912 | Punched cards | breaks jmcc | compile: 82:6: error: unterminated character literal |
| 913 | User:PureFox | fetch_error | no_c_section |
| 914 | User:Pwmiller74 | fetch_error | no_c_section |
| 915 | Pythagoras tree | skipped | non_deterministic |
| 916 | Pythagorean quadruples | skipped | requires_math |
| 917 | Pythagorean triples | skipped | gcc_compile_fail |
| 918 | QR decomposition | skipped | requires_math |
| 919 | Quad-power prime seeds | skipped | requires_gmp |
| 920 | Quaternion | skipped | gcc_compile_fail |
| 921 | Queue/Definition | fetch_error | no_main |
| 922 | Queue/Usage | skipped | gcc_compile_fail |
| 923 | Quickselect algorithm | passes jmcc |  |
| 924 | Quine | passes jmcc |  |
| 925 | Radical of an integer | skipped | gcc_timeout |
| 926 | Rainbow | passes jmcc |  |
| 927 | Ramer-Douglas-Peucker line simplification | skipped | requires_math |
| 928 | Ramsey's theorem | passes jmcc |  |
| 929 | Random Latin squares | skipped | non_deterministic |
| 930 | Random number generator (device) | skipped | requires_file_io |
| 931 | Random number generator (included) | skipped | non_deterministic |
| 932 | Random numbers | skipped | requires_math |
| 933 | Range consolidation | passes jmcc |  |
| 934 | Range expansion | passes jmcc |  |
| 935 | Range extraction | passes jmcc |  |
| 936 | Ranking methods | skipped | interactive |
| 937 | Rate counter | skipped | non_deterministic |
| 938 | Rational calculator | skipped | interactive |
| 939 | Ray-casting algorithm | skipped | requires_math |
| 940 | RCRPG | fetch_error | no_code_block |
| 941 | Read a configuration file | skipped | gcc_compile_fail |
| 942 | Read a file character by character/UTF8 | skipped | requires_wchar |
| 943 | Read a file line by line | skipped | interactive |
| 944 | Read a specific line from a file | fetch_error | no_main |
| 945 | Read entire file | skipped | requires_file_io |
| 946 | Readline interface | skipped | gcc_compile_fail |
| 947 | Real constants and functions | fetch_error | no_main |
| 948 | Recaman's sequence | skipped | gcc_compile_fail |
| 949 | Record sound | skipped | requires_unistd |
| 950 | Reduced row echelon form | breaks jmcc | SIGSEGV |
| 951 | Regular expressions | implemented | regular_expressions.c |
| 952 | Remote agent/Agent interface | fetch_error | no_code_block |
| 953 | Remote agent/Agent logic | fetch_error | no_code_block |
| 954 | Remote agent/Simulation | fetch_error | no_code_block |
| 955 | Remove duplicate elements | passes jmcc |  |
| 956 | Remove lines from a file | skipped | argv0_dependent |
| 957 | Remove vowels from a string | passes jmcc |  |
| 958 | Rename a file | passes jmcc |  |
| 959 | Rendezvous | skipped | requires_pthread |
| 960 | Rep-string | passes jmcc |  |
| 961 | Repeat | passes jmcc |  |
| 962 | Repeat a string | passes jmcc |  |
| 963 | Resistor mesh | passes jmcc |  |
| 964 | Retrieve and search chat history | skipped | requires_curl |
| 965 | Return multiple values | implemented | return_multiple_values.c |
| 966 | Reverse a string | implemented | reverse_a_string.c |
| 967 | Reverse words in a string | passes jmcc |  |
| 968 | RIPEMD-160 | fetch_error | no_main |
| 969 | User:Roboticist-Tav | fetch_error | no_c_section |
| 970 | Rock-paper-scissors | skipped | non_deterministic |
| 971 | Rodrigues’ rotation formula | fetch_error | fetch_error |
| 972 | Roman numerals/Decode | passes jmcc |  |
| 973 | Roman numerals/Encode | skipped | interactive |
| 974 | Roots of a function | skipped | requires_math |
| 975 | Roots of a quadratic function | skipped | requires_math |
| 976 | Roots of unity | skipped | requires_math |
| 977 | Rosetta Code/Rank languages by popularity | skipped | requires_file_io |
| 978 | Rot-13 | skipped | requires_file_io |
| 979 | RPG attributes generator | skipped | non_deterministic |
| 980 | RSA code | skipped | requires_gmp |
| 981 | Rule30 | passes jmcc |  |
| 982 | Run as a daemon or service | skipped | requires_unistd |
| 983 | Run-length encoding | skipped | requires_file_io |
| 984 | Runge-Kutta method | skipped | requires_math |
| 985 | S-expressions | breaks jmcc | wrong_output: 350b vs 107b |
| 986 | Safe addition | skipped | gcc_compile_fail |
| 987 | Safe and Sophie Germain primes | passes jmcc |  |
| 988 | Safe primes and unsafe primes | breaks jmcc | runtime: timeout |
| 989 | Sailors, coconuts and a monkey problem | breaks jmcc | runtime: timeout |
| 990 | Same fringe | skipped | gcc_compile_fail |
| 991 | Sattolo cycle | skipped | argv0_dependent |
| 992 | Scope modifiers | fetch_error | no_main |
| 993 | Scope/Function names and labels | skipped | interactive |
| 994 | Sealed classes and methods | passes jmcc |  |
| 995 | Search a list | passes jmcc |  |
| 996 | Search a list of records | implemented | search_a_list_of_records.c |
| 997 | Search in paragraph's text | skipped | requires_file_io |
| 998 | Secure temporary file | skipped | requires_file_io |
| 999 | SEDOLs | skipped | interactive |
| 1000 | Selectively replace multiple instances of a character within a string | passes jmcc |  |
| 1001 | Self numbers | skipped | non_deterministic |
| 1002 | Self-contained numbers | passes jmcc |  |
| 1003 | Self-describing numbers | skipped | gcc_compile_fail |
| 1004 | Semaphore | fetch_error | no_main |
| 1005 | Semiprime | passes jmcc |  |
| 1006 | Semordnilap | skipped | interactive |
| 1007 | SEND + MORE = MONEY | fetch_error | page_missing |
| 1008 | Send email | skipped | requires_curl |
| 1009 | Sequence of non-squares | skipped | requires_math |
| 1010 | Sequence of primes by trial division | skipped | interactive |
| 1011 | Sequence of primorial primes | skipped | requires_gmp |
| 1012 | Sequence: nth number with exactly n divisors | skipped | requires_math |
| 1013 | Sequence: smallest number greater than previous term with exactly n divisors | passes jmcc |  |
| 1014 | Sequence: smallest number with exactly n divisors | passes jmcc |  |
| 1015 | Set | passes jmcc |  |
| 1016 | Set consolidation | passes jmcc |  |
| 1017 | Set of real numbers | skipped | requires_math |
| 1018 | Set puzzle | skipped | non_deterministic |
| 1019 | Seven-sided dice from five-sided dice | skipped | non_deterministic |
| 1020 | Sexy primes | passes jmcc |  |
| 1021 | User:SGTMcClain | fetch_error | no_c_section |
| 1022 | SHA-1 | skipped | requires_openssl |
| 1023 | SHA-256 | skipped | requires_openssl |
| 1024 | SHA-256 Merkle tree | skipped | argv0_dependent |
| 1025 | Shell one-liner | skipped | gcc_compile_fail |
| 1026 | Shift list elements to left by 3 | passes jmcc |  |
| 1027 | Shoelace formula for polygonal area | skipped | requires_math |
| 1028 | Short-circuit evaluation | implemented | short_circuit_evaluation.c |
| 1029 | Shortest common supersequence | implemented | shortest_common_supersequence.c |
| 1030 | Show ASCII table | passes jmcc |  |
| 1031 | Show the (decimal) value of a number of 1s appended with a 3, then squared | passes jmcc |  |
| 1032 | Show the epoch | passes jmcc |  |
| 1033 | Sierpinski arrowhead curve | skipped | requires_math |
| 1034 | Sierpinski carpet | passes jmcc |  |
| 1035 | Sierpinski pentagon | skipped | requires_math |
| 1036 | Sierpinski triangle | passes jmcc |  |
| 1037 | Sierpinski triangle/Graphical | skipped | requires_math |
| 1038 | Sieve of Eratosthenes | fetch_error | no_main |
| 1039 | Sign of an integer (signum) | skipped | requires_math |
| 1040 | Simple database | skipped | argv0_dependent |
| 1041 | Simple windowed application | skipped | gcc_compile_fail |
| 1042 | Simulate input/Keyboard | skipped | requires_x11 |
| 1043 | Simulate input/Mouse | skipped | windows_only |
| 1044 | Simulated annealing | skipped | requires_unistd |
| 1045 | Sine wave | skipped | requires_math |
| 1046 | Singleton | fetch_error | no_main |
| 1047 | Singly-linked list/Element definition | fetch_error | no_main |
| 1048 | Singly-linked list/Element insertion | fetch_error | no_main |
| 1049 | Singly-linked list/Element removal | skipped | argv0_dependent |
| 1050 | Singly-linked list/Reversal | fetch_error | no_main |
| 1051 | Singly-linked list/Traversal | fetch_error | no_main |
| 1052 | Singular value decomposition | skipped | gcc_compile_fail |
| 1053 | Sleep | skipped | requires_unistd |
| 1054 | Sleeping Beauty problem | skipped | non_deterministic |
| 1055 | Smallest multiple | passes jmcc |  |
| 1056 | Smallest power of 6 whose decimal expansion contains n | skipped | requires_gmp |
| 1057 | Smallest square that begins with n | passes jmcc |  |
| 1058 | Smarandache prime-digital sequence | passes jmcc |  |
| 1059 | Smarandache-Wellin primes | skipped | requires_gmp |
| 1060 | Smith numbers | passes jmcc |  |
| 1061 | Snake | skipped | requires_ncurses |
| 1062 | Snake and ladder | skipped | non_deterministic |
| 1063 | SOAP | skipped | requires_curl |
| 1064 | Sockets | skipped | requires_unistd |
| 1065 | Sokoban | skipped | requires_unistd |
| 1066 | Soloway's recurring rainfall | skipped | interactive |
| 1067 | Solve a Hidato puzzle | implemented | solve_a_hidato_puzzle.c |
| 1068 | Solve the no connection puzzle | skipped | requires_math |
| 1069 | Sort a list of object identifiers | passes jmcc |  |
| 1070 | Sort an array of composite structures | passes jmcc |  |
| 1071 | Sort an integer array | passes jmcc |  |
| 1072 | Sort disjoint sublist | passes jmcc |  |
| 1073 | Sort numbers lexicographically | skipped | requires_math |
| 1074 | Sort stability | fetch_error | no_code_block |
| 1075 | Sort the letters of string in alphabetical order | implemented | sort_letters_alphabetical.c |
| 1076 | Sort three variables | skipped | interactive |
| 1077 | Sort using a custom comparator | passes jmcc |  |
| 1078 | Sorting algorithms/Bead sort | passes jmcc |  |
| 1079 | Sorting algorithms/Bogosort | skipped | non_deterministic |
| 1080 | Sorting algorithms/Bubble sort | passes jmcc |  |
| 1081 | Sorting algorithms/Circle sort | passes jmcc |  |
| 1082 | Sorting algorithms/Cocktail sort | passes jmcc |  |
| 1083 | Sorting algorithms/Cocktail sort with shifting bounds | passes jmcc |  |
| 1084 | Sorting algorithms/Comb sort | fetch_error | no_main |
| 1085 | Sorting algorithms/Counting sort | fetch_error | no_main |
| 1086 | Sorting algorithms/Cycle sort | passes jmcc |  |
| 1087 | Sorting algorithms/Gnome sort | fetch_error | no_main |
| 1088 | Sorting algorithms/Heapsort | passes jmcc |  |
| 1089 | Sorting algorithms/Insertion sort | passes jmcc |  |
| 1090 | Sorting algorithms/Merge sort | passes jmcc |  |
| 1091 | Sorting algorithms/Pancake sort | fetch_error | no_main |
| 1092 | Sorting algorithms/Patience sort | skipped | gcc_exit_-11 |
| 1093 | Sorting algorithms/Permutation sort | passes jmcc |  |
| 1094 | Sorting algorithms/Quicksort | passes jmcc |  |
| 1095 | Sorting algorithms/Radix sort | skipped | non_deterministic |
| 1096 | Sorting algorithms/Selection sort | passes jmcc |  |
| 1097 | Sorting algorithms/Shell sort | passes jmcc |  |
| 1098 | Sorting algorithms/Sleep sort | skipped | requires_unistd |
| 1099 | Sorting algorithms/Stooge sort | passes jmcc |  |
| 1100 | Sorting algorithms/Strand sort | implemented | strand_sort.c |
| 1101 | Sorting algorithms/Tree sort on a linked list | skipped | non_deterministic |
| 1102 | Soundex | passes jmcc |  |
| 1103 | Sparkline in unicode | skipped | requires_math |
| 1104 | Special characters | fetch_error | no_code_block |
| 1105 | Special divisors | passes jmcc |  |
| 1106 | Special factorials | skipped | requires_math |
| 1107 | Special neighbor primes | passes jmcc |  |
| 1108 | Special variables | fetch_error | no_code_block |
| 1109 | Speech synthesis | skipped | requires_unistd |
| 1110 | Spelling of ordinal numbers | skipped | gcc_compile_fail |
| 1111 | Sphenic numbers | skipped | requires_math |
| 1112 | Spinning rod animation/Text | skipped | gcc_timeout |
| 1113 | Spiral matrix | passes jmcc |  |
| 1114 | Split a character string based on change of character | passes jmcc |  |
| 1115 | Spoof game | skipped | non_deterministic |
| 1116 | SQL-based authentication | skipped | requires_openssl |
| 1117 | Square but not cube | skipped | requires_math |
| 1118 | Square form factorization | skipped | requires_math |
| 1119 | Square-free integers | skipped | requires_math |
| 1120 | Stable marriage problem | implemented | stable_marriage.c |
| 1121 | Stack | passes jmcc |  |
| 1122 | Stack traces | skipped | requires_unistd |
| 1123 | Stair-climbing puzzle | fetch_error | no_main |
| 1124 | Start from a main routine | passes jmcc |  |
| 1125 | State name puzzle | implemented | state_name_puzzle.c |
| 1126 | Statistics/Basic | skipped | requires_math |
| 1127 | Statistics/Normal distribution | skipped | requires_math |
| 1128 | Steady squares | passes jmcc |  |
| 1129 | Steffensen's method | skipped | requires_math |
| 1130 | Stem-and-leaf plot | passes jmcc |  |
| 1131 | Stern-Brocot sequence | passes jmcc |  |
| 1132 | Stirling numbers of the first kind | passes jmcc |  |
| 1133 | Stirling numbers of the second kind | passes jmcc |  |
| 1134 | Straddling checkerboard | skipped | gcc_compile_fail |
| 1135 | Strange numbers | passes jmcc |  |
| 1136 | Strange plus numbers | passes jmcc |  |
| 1137 | Strange unique prime triplets | passes jmcc |  |
| 1138 | Stream merge | skipped | interactive |
| 1139 | String append | passes jmcc |  |
| 1140 | String case | passes jmcc |  |
| 1141 | String comparison | fetch_error | no_main |
| 1142 | String concatenation | passes jmcc |  |
| 1143 | String interpolation (included) | passes jmcc |  |
| 1144 | String length | passes jmcc |  |
| 1145 | String matching | passes jmcc |  |
| 1146 | String prepend | passes jmcc |  |
| 1147 | Strip a set of characters from a string | passes jmcc |  |
| 1148 | Strip block comments | skipped | requires_file_io |
| 1149 | Strip comments from a string | skipped | interactive |
| 1150 | Strip control codes and extended characters from a string | skipped | non_deterministic |
| 1151 | Strip whitespace from a string/Top and tail | passes jmcc |  |
| 1152 | Strong and weak primes | passes jmcc |  |
| 1153 | Subleq | skipped | argv0_dependent |
| 1154 | Subset sum problem | skipped | gcc_timeout |
| 1155 | Substitution cipher | skipped | requires_wchar |
| 1156 | Substring | skipped | gcc_compile_fail |
| 1157 | Substring/Top and tail | passes jmcc |  |
| 1158 | Subtractive generator | skipped | non_deterministic |
| 1159 | Successive prime differences | passes jmcc |  |
| 1160 | Sudan function | passes jmcc |  |
| 1161 | Sudoku | fetch_error | no_c_section |
| 1162 | Sum and product of an array | skipped | requires_file_io |
| 1163 | Sum and product puzzle | passes jmcc |  |
| 1164 | Sum data type | skipped | non_deterministic |
| 1165 | Sum digits of an integer | passes jmcc |  |
| 1166 | Sum multiples of 3 and 5 | passes jmcc |  |
| 1167 | Sum of a series | passes jmcc |  |
| 1168 | Sum of divisors | passes jmcc |  |
| 1169 | Sum of elements below main diagonal of matrix | skipped | argv0_dependent |
| 1170 | Sum of first n cubes | passes jmcc |  |
| 1171 | Sum of primes in odd positions is prime | passes jmcc |  |
| 1172 | Sum of square and cube digits of an integer are primes | passes jmcc |  |
| 1173 | Sum of squares | implemented | sum_of_squares.c |
| 1174 | Sum of the digits of n is substring of n | passes jmcc |  |
| 1175 | Sum of two adjacent numbers are primes | skipped | requires_math |
| 1176 | Sum to 100 | passes jmcc |  |
| 1177 | Summarize and say sequence | skipped | gcc_compile_fail |
| 1178 | Summarize primes | passes jmcc |  |
| 1179 | Summation of primes | passes jmcc |  |
| 1180 | Sunflower fractal | skipped | requires_math |
| 1181 | Super-d numbers | skipped | requires_gmp |
| 1182 | Superellipse | skipped | requires_math |
| 1183 | Superpermutation minimisation | passes jmcc |  |
| 1184 | Sutherland-Hodgman polygon clipping | skipped | requires_math |
| 1185 | Symmetric difference | implemented | symmetric_difference.c |
| 1186 | Synchronous concurrency | skipped | requires_file_io |
| 1187 | System time | skipped | non_deterministic |
| 1188 | Table creation | skipped | gcc_compile_fail |
| 1189 | Table creation/Postal addresses | skipped | gcc_compile_fail |
| 1190 | Take notes on the command line | skipped | non_deterministic |
| 1191 | Tarjan | fetch_error | no_c_section |
| 1192 | Tau function | passes jmcc |  |
| 1193 | Tau number | passes jmcc |  |
| 1194 | Taxicab numbers | implemented | taxicab_numbers.c |
| 1195 | Teacup rim text | skipped | argv0_dependent |
| 1196 | Temperature conversion | passes jmcc |  |
| 1197 | Terminal control/Clear the screen | fetch_error | no_c_section |
| 1198 | Terminal control/Coloured text | passes jmcc |  |
| 1199 | Terminal control/Cursor movement | skipped | gcc_compile_fail |
| 1200 | Terminal control/Cursor positioning | fetch_error | no_c_section |
| 1201 | Terminal control/Dimensions | skipped | requires_unistd |
| 1202 | Terminal control/Display an extended character | implemented | terminal_extended_char.c |
| 1203 | Terminal control/Hiding the cursor | skipped | gcc_compile_fail |
| 1204 | Terminal control/Inverse video | passes jmcc |  |
| 1205 | Terminal control/Positional read | skipped | windows_only |
| 1206 | Terminal control/Preserve screen | skipped | requires_unistd |
| 1207 | Terminal control/Ringing the terminal bell | passes jmcc |  |
| 1208 | Terminal control/Unicode output | implemented | unicode_output.c |
| 1209 | Ternary logic | passes jmcc |  |
| 1210 | Test a function | skipped | gcc_compile_fail |
| 1211 | Test integerness | skipped | requires_math |
| 1212 | Tetris | fetch_error | no_code_block |
| 1213 | Text between | fetch_error | no_main |
| 1214 | Text processing/1 | skipped | interactive |
| 1215 | Text processing/2 | skipped | requires_unistd |
| 1216 | Text processing/Max licenses in use | skipped | interactive |
| 1217 | Textonyms | skipped | argv0_dependent |
| 1218 | The ISAAC cipher | passes jmcc |  |
| 1219 | The Name Game | passes jmcc |  |
| 1220 | The sieve of Sundaram | skipped | requires_math |
| 1221 | The Twelve Days of Christmas | passes jmcc |  |
| 1222 | Thiele's interpolation formula | skipped | requires_math |
| 1223 | Three word location | passes jmcc |  |
| 1224 | Thue-Morse | passes jmcc |  |
| 1225 | Tic-tac-toe | skipped | non_deterministic |
| 1226 | Time a function | skipped | non_deterministic |
| 1227 | Tokenize a string | passes jmcc |  |
| 1228 | Tokenize a string with escaping | passes jmcc |  |
| 1229 | Tonelli-Shanks algorithm | breaks jmcc | wrong_output: 208b vs 188b |
| 1230 | Top rank per group | passes jmcc |  |
| 1231 | Topological sort | breaks jmcc | wrong_output: 197b vs 15b |
| 1232 | Topological sort/Extracted top item | skipped | gcc_compile_fail |
| 1233 | Topswops | passes jmcc |  |
| 1234 | Total circles area | skipped | requires_math |
| 1235 | Totient function | passes jmcc |  |
| 1236 | Towers of Hanoi | passes jmcc |  |
| 1237 | Trabb Pardo–Knuth algorithm | fetch_error | fetch_error |
| 1238 | Tree traversal | passes jmcc |  |
| 1239 | Trigonometric functions | skipped | requires_math |
| 1240 | Triplet of three numbers | skipped | requires_math |
| 1241 | Truncatable primes | passes jmcc |  |
| 1242 | Truncate a file | skipped | windows_only |
| 1243 | Truth table | skipped | interactive |
| 1244 | Twin primes | skipped | gcc_timeout |
| 1245 | Two bullet roulette | skipped | non_deterministic |
| 1246 | Two identical strings | passes jmcc |  |
| 1247 | Two sum | passes jmcc |  |
| 1248 | Two's complement | fetch_error | no_main |
| 1249 | Type detection | skipped | non_deterministic |
| 1250 | Ulam numbers | skipped | non_deterministic |
| 1251 | Ulam spiral (for primes) | skipped | requires_math |
| 1252 | User:Uli Bellgardt | fetch_error | no_c_section |
| 1253 | Ultra useful primes | skipped | requires_gmp |
| 1254 | Unbias a random generator | skipped | non_deterministic |
| 1255 | Undefined values | breaks jmcc | wrong_output: 22b vs 18b |
| 1256 | Unicode strings | breaks jmcc | wrong_output: 27b vs 25b |
| 1257 | Unicode variable names | passes jmcc |  |
| 1258 | Unique characters | passes jmcc |  |
| 1259 | Universal Lambda Machine | skipped | interactive |
| 1260 | Universal Turing machine | passes jmcc |  |
| 1261 | Unix/ls | skipped | requires_unistd |
| 1262 | Unprimeable numbers | passes jmcc |  |
| 1263 | Untouchable numbers | skipped | gcc_timeout |
| 1264 | Untrusted environment | fetch_error | no_code_block |
| 1265 | UPC | passes jmcc |  |
| 1266 | Update a configuration file | skipped | interactive |
| 1267 | URL decoding | skipped | interactive |
| 1268 | URL encoding | passes jmcc |  |
| 1269 | Use another language to call a function | skipped | gcc_compile_fail |
| 1270 | Useless instructions | breaks jmcc | compile: 29:5: error: unexpected token 'auto' |
| 1271 | User input/Graphical | skipped | gcc_compile_fail |
| 1272 | User input/Text | skipped | interactive |
| 1273 | UTF-8 encode and decode | breaks jmcc | compile: 2747:18: error: expected '}', got 'b00111111' (IDENTIFIER) |
| 1274 | Validate International Securities Identification Number | passes jmcc |  |
| 1275 | Vampire number | skipped | requires_math |
| 1276 | Van der Corput sequence | passes jmcc |  |
| 1277 | Van Eck sequence | passes jmcc |  |
| 1278 | Variable declaration reset | passes jmcc |  |
| 1279 | Variable size/Get | fetch_error | no_main |
| 1280 | Variable size/Set | fetch_error | no_main |
| 1281 | Variable-length quantity | passes jmcc |  |
| 1282 | Variables | fetch_error | no_main |
| 1283 | Variadic function | fetch_error | no_main |
| 1284 | Vector | skipped | gcc_compile_fail |
| 1285 | Vector products | skipped | gcc_compile_fail |
| 1286 | Verhoeff algorithm | implemented | verhoeff_algorithm.c |
| 1287 | Verify distribution uniformity/Chi-squared test | fetch_error | no_main |
| 1288 | Verify distribution uniformity/Naive | skipped | requires_math |
| 1289 | Vibrating rectangles | skipped | requires_math |
| 1290 | Vigenère cipher | fetch_error | fetch_error |
| 1291 | Vigenère cipher/Cryptanalysis | fetch_error | fetch_error |
| 1292 | Vile and Dopey numbers | passes jmcc |  |
| 1293 | Visualize a tree | skipped | non_deterministic |
| 1294 | VList | skipped | gcc_compile_fail |
| 1295 | Vogel's approximation method | implemented | vogels_approximation.c |
| 1296 | Voronoi diagram | skipped | non_deterministic |
| 1297 | Wagstaff primes | skipped | requires_gmp |
| 1298 | Walk a directory/Non-recursively | skipped | requires_regex |
| 1299 | Walk a directory/Recursively | skipped | requires_unistd |
| 1300 | Water collected between towers | skipped | non_deterministic |
| 1301 | Wave function collapse | skipped | non_deterministic |
| 1302 | Web scraping | skipped | requires_curl |
| 1303 | Weird numbers | passes jmcc |  |
| 1304 | Welch's t-test | skipped | requires_math |
| 1305 | Wieferich primes | passes jmcc |  |
| 1306 | WiktionaryDumps to words | skipped | requires_unistd |
| 1307 | Wilson primes of order n | skipped | requires_gmp |
| 1308 | Window creation | skipped | gcc_compile_fail |
| 1309 | Window creation/X11 | skipped | requires_x11 |
| 1310 | Window management | fetch_error | no_main |
| 1311 | Wireworld | skipped | gcc_timeout |
| 1312 | Wolstenholme numbers | skipped | requires_gmp |
| 1313 | Word frequency | skipped | argv0_dependent |
| 1314 | Word wheel | skipped | interactive |
| 1315 | Word wrap | breaks jmcc | compile: 145:55: error: expected ';', got '{' (LBRACE) |
| 1316 | Wordle comparison | passes jmcc |  |
| 1317 | Words containing "the" substring | skipped | interactive |
| 1318 | Words from neighbour ones | skipped | interactive |
| 1319 | World Cup group stage | passes jmcc |  |
| 1320 | Write entire file | passes jmcc |  |
| 1321 | Write float arrays to a text file | skipped | requires_math |
| 1322 | Write language name in 3D ASCII | passes jmcc |  |
| 1323 | Write to Windows event log | skipped | argv0_dependent |
| 1324 | Xiaolin Wu's line algorithm | fetch_error | no_main |
| 1325 | XML validation | skipped | argv0_dependent |
| 1326 | XML/DOM serialization | skipped | gcc_compile_fail |
| 1327 | XML/Input | skipped | gcc_compile_fail |
| 1328 | XML/Output | skipped | gcc_compile_fail |
| 1329 | XML/XPath | skipped | argv0_dependent |
| 1330 | User:Xorph | fetch_error | no_c_section |
| 1331 | XXXX redacted | passes jmcc |  |
| 1332 | Y combinator | passes jmcc |  |
| 1333 | Yellowstone sequence | skipped | gcc_compile_fail |
| 1334 | Yin and yang | passes jmcc |  |
| 1335 | Zebra puzzle | breaks jmcc | compile: 215:20: error: expected ')', got 'b11111' (IDENTIFIER) |
| 1336 | Zeckendorf arithmetic | skipped | gcc_compile_fail |
| 1337 | Zeckendorf number representation | passes jmcc |  |
| 1338 | Zero to the zero power | skipped | requires_math |
| 1339 | Zhang-Suen thinning algorithm | skipped | interactive |
| 1340 | Zig-zag matrix | passes jmcc |  |
| 1341 | Zsigmondy numbers | breaks jmcc | runtime: timeout |
