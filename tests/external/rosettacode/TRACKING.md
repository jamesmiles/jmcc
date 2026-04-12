# Rosetta Code Test Tracking

C programs from [Rosetta Code](https://rosettacode.org/wiki/Category:C) used as integration tests for jmcc.

## Status Key

- **not implemented** — not yet downloaded or converted to a test
- **implemented** — test added, passes with gcc and tracked against jmcc
- **breaks jmcc** — compiles with gcc but fails with jmcc (reason noted: compile error, SIGSEGV, wrong output, etc.)
- **skipped (reason)** — not suitable as a test, e.g.:
  - *already covered* — passes jmcc out of the box, no new coverage
  - *requires external lib* — depends on libraries beyond libc
  - *non-deterministic* — uses rand/time, output varies per run
  - *interactive* — requires user input
  - *too large* — multi-file or exceeds reasonable test size

## Summary

Total: 1341 | Implemented: 19 | Breaks jmcc: 121 | Skipped: 4 | Remaining: 1197

## Tasks

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | 100 doors | not implemented | |
| 2 | 100 prisoners | not implemented | |
| 3 | 10001th prime | not implemented | |
| 4 | 15 puzzle game | not implemented | |
| 5 | 15 puzzle solver | not implemented | |
| 6 | 2048 | not implemented | |
| 7 | 21 game | not implemented | |
| 8 | 24 game | not implemented | |
| 9 | 24 game/Solve | not implemented | |
| 10 | 4-rings or 4-squares puzzle | not implemented | |
| 11 | 9 billion names of God the integer | not implemented | |
| 12 | 99 bottles of beer | not implemented | |
| 13 | A* search algorithm | not implemented | |
| 14 | A+B | not implemented | |
| 15 | Abbreviations, automatic | not implemented | |
| 16 | Abbreviations, easy | implemented | FAILS jmcc - size_t not recognized |
| 17 | Abbreviations, simple | breaks jmcc | compile error: expected type specifier |
| 18 | ABC correlation | breaks jmcc | compile error: expected type specifier |
| 19 | ABC problem | not implemented | |
| 20 | ABC words | not implemented | |
| 21 | Abelian sandpile model | not implemented | |
| 22 | Abstract type | not implemented | |
| 23 | Abundant odd numbers | not implemented | |
| 24 | Abundant, deficient and perfect number classifications | not implemented | |
| 25 | Accumulator factory | breaks jmcc | compile error: unexpected token |
| 26 | Achilles numbers | not implemented | |
| 27 | Ackermann function | not implemented | |
| 28 | Active Directory/Connect | not implemented | |
| 29 | Active Directory/Search for a user | not implemented | |
| 30 | Active object | not implemented | |
| 31 | Addition chains | not implemented | |
| 32 | Addition-chain exponentiation | not implemented | |
| 33 | Additive primes | implemented | FAILS jmcc - wrong sieve output (88 vs 54 primes) |
| 34 | Address of a variable | not implemented | |
| 35 | Air mass | not implemented | |
| 36 | AKS test for primes | breaks jmcc | compile error: parse failure |
| 37 | Align columns | not implemented | |
| 38 | Aliquot sequence classifications | not implemented | |
| 39 | Almost prime | implemented | FAILS jmcc - comma in for-init parse error |
| 40 | Alternade words | not implemented | |
| 41 | Amb | not implemented | |
| 42 | Amicable pairs | not implemented | |
| 43 | Anadromes | not implemented | |
| 44 | Anagrams | not implemented | |
| 45 | Anagrams/Deranged anagrams | not implemented | |
| 46 | Angle difference between two bearings | not implemented | |
| 47 | Angles (geometric), normalization and conversion | not implemented | |
| 48 | Animate a pendulum | not implemented | |
| 49 | Animated Spinners | not implemented | |
| 50 | Animation | not implemented | |
| 51 | Anonymous recursion | not implemented | |
| 52 | Anti-primes | not implemented | |
| 53 | Append a record to the end of a text file | not implemented | |
| 54 | Append numbers at same position in strings | not implemented | |
| 55 | Apply a callback to an array | not implemented | |
| 56 | Apply a digital filter (direct form II transposed) | not implemented | |
| 57 | Approximate equality | not implemented | |
| 58 | Arbitrary-precision integers (included) | not implemented | |
| 59 | Archimedean spiral | not implemented | |
| 60 | Arena storage pool | not implemented | |
| 61 | Arithmetic derivative | not implemented | |
| 62 | Arithmetic evaluation | not implemented | |
| 63 | Arithmetic numbers | not implemented | |
| 64 | Arithmetic-geometric mean | not implemented | |
| 65 | Arithmetic-geometric mean/Calculate Pi | not implemented | |
| 66 | Arithmetic/Complex | not implemented | |
| 67 | Arithmetic/Integer | not implemented | |
| 68 | Arithmetic/Rational | not implemented | |
| 69 | Array concatenation | not implemented | |
| 70 | Array length | not implemented | |
| 71 | Arrays | not implemented | |
| 72 | Ascending primes | not implemented | |
| 73 | ASCII art diagram converter | breaks jmcc | compile error: parse failure |
| 74 | ASCII control characters | not implemented | |
| 75 | Aspect oriented programming | not implemented | |
| 76 | Assertions | breaks jmcc | wrong exit code |
| 77 | Associative array/Creation | not implemented | |
| 78 | Associative array/Iteration | not implemented | |
| 79 | Atomic updates | not implemented | |
| 80 | Attractive numbers | not implemented | |
| 81 | Average loop length | not implemented | |
| 82 | Averages/Arithmetic mean | breaks jmcc | SIGSEGV |
| 83 | Averages/Mean angle | not implemented | |
| 84 | Averages/Mean time of day | not implemented | |
| 85 | Averages/Median | breaks jmcc | SIGSEGV |
| 86 | Averages/Mode | breaks jmcc | SIGSEGV |
| 87 | Averages/Pythagorean means | not implemented | |
| 88 | Averages/Root mean square | not implemented | |
| 89 | Averages/Simple moving average | not implemented | |
| 90 | AVL tree | not implemented | |
| 91 | Babbage problem | not implemented | |
| 92 | Bacon cipher | not implemented | |
| 93 | Balanced brackets | not implemented | |
| 94 | Balanced ternary | breaks jmcc | compile error: parse failure |
| 95 | Banker's algorithm | not implemented | |
| 96 | Barnsley fern | not implemented | |
| 97 | Base 16 numbers needing a to f | not implemented | |
| 98 | Base64 decode data | not implemented | |
| 99 | Base64 encode data | not implemented | |
| 100 | Bell numbers | breaks jmcc | compile error: unexpected token |
| 101 | Benford's law | not implemented | |
| 102 | Bernoulli numbers | not implemented | |
| 103 | Bernoulli's triangle | not implemented | |
| 104 | Bernstein basis polynomials | not implemented | |
| 105 | Best shuffle | breaks jmcc | compile error: expected type specifier |
| 106 | Bilinear interpolation | not implemented | |
| 107 | Bin given limits | breaks jmcc | compile error: unexpected token |
| 108 | Binary digits | not implemented | |
| 109 | Binary search | not implemented | |
| 110 | Binary strings | not implemented | |
| 111 | Binomial transform | breaks jmcc | compile error: expected type specifier |
| 112 | Bioinformatics/Base count | not implemented | |
| 113 | Bioinformatics/Sequence mutation | not implemented | |
| 114 | Biorhythms | not implemented | |
| 115 | Birthday problem | not implemented | |
| 116 | Bitcoin/address validation | not implemented | |
| 117 | Bitcoin/public point to address | not implemented | |
| 118 | Bitmap | not implemented | |
| 119 | Bitmap/Bresenham's line algorithm | not implemented | |
| 120 | Bitmap/Bézier curves/Cubic | not implemented | |
| 121 | Bitmap/Bézier curves/Quadratic | not implemented | |
| 122 | Bitmap/Flood fill | not implemented | |
| 123 | Bitmap/Histogram | not implemented | |
| 124 | Bitmap/Midpoint circle algorithm | not implemented | |
| 125 | Bitmap/PPM conversion through a pipe | not implemented | |
| 126 | Bitmap/Read a PPM file | not implemented | |
| 127 | Bitmap/Read an image through a pipe | not implemented | |
| 128 | Bitmap/Write a PPM file | not implemented | |
| 129 | Bitwise IO | not implemented | |
| 130 | Bitwise operations | not implemented | |
| 131 | Blum integer | not implemented | |
| 132 | Boids | not implemented | |
| 133 | Boolean values | not implemented | |
| 134 | Box the compass | breaks jmcc | wrong output |
| 135 | Brace expansion | not implemented | |
| 136 | Brazilian numbers | not implemented | |
| 137 | Brownian tree | not implemented | |
| 138 | Bulls and cows | not implemented | |
| 139 | Bulls and cows/Player | not implemented | |
| 140 | Burrows–Wheeler transform | not implemented | |
| 141 | Bézier curves/Intersections | not implemented | |
| 142 | Caesar cipher | not implemented | |
| 143 | Calculating the value of e | not implemented | |
| 144 | Calendar | not implemented | |
| 145 | Calendar - for "REAL" programmers | not implemented | |
| 146 | Call a foreign-language function | not implemented | |
| 147 | Call a function | not implemented | |
| 148 | Call a function in a shared library | not implemented | |
| 149 | Call an object method | breaks jmcc | compile error: lvalue check |
| 150 | Calmo numbers | not implemented | |
| 151 | CalmoSoft primes | not implemented | |
| 152 | Canny edge detector | not implemented | |
| 153 | Canonicalize CIDR | not implemented | |
| 154 | Cantor set | not implemented | |
| 155 | Card shuffles | not implemented | |
| 156 | Carmichael 3 strong pseudoprimes | not implemented | |
| 157 | Cartesian product of two or more lists | breaks jmcc | wrong output |
| 158 | Case-sensitivity of identifiers | not implemented | |
| 159 | Casting out nines | not implemented | |
| 160 | Catalan numbers | not implemented | |
| 161 | Catalan numbers/Pascal's triangle | not implemented | |
| 162 | Catamorphism | not implemented | |
| 163 | Catmull–Clark subdivision surface | not implemented | |
| 164 | Centroid of a set of N-dimensional points | breaks jmcc | compile error: parse failure |
| 165 | Change e letters to i in words | not implemented | |
| 166 | Changeable words | not implemented | |
| 167 | Chaocipher | breaks jmcc | compile error: parse failure |
| 168 | Chaos game | not implemented | |
| 169 | Character codes | not implemented | |
| 170 | Chat server | not implemented | |
| 171 | Chebyshev coefficients | not implemented | |
| 172 | Check if a polygon overlaps with a rectangle | breaks jmcc | compile error: parse failure |
| 173 | Check if two polygons overlap | breaks jmcc | compile error: parse failure |
| 174 | Check input device is a terminal | not implemented | |
| 175 | Check output device is a terminal | not implemented | |
| 176 | Check that file exists | not implemented | |
| 177 | Checkpoint synchronization | not implemented | |
| 178 | Chemical calculator | breaks jmcc | compile error: expected type specifier |
| 179 | Chernick's Carmichael numbers | not implemented | |
| 180 | Cheryl's birthday | not implemented | |
| 181 | Chinese remainder theorem | breaks jmcc | compile error: parse failure |
| 182 | Chinese zodiac | not implemented | |
| 183 | User:Chkas | not implemented | |
| 184 | Cholesky decomposition | not implemented | |
| 185 | Chowla numbers | not implemented | |
| 186 | Cipolla's algorithm | not implemented | |
| 187 | Circles of given radius through two points | not implemented | |
| 188 | Circular primes | not implemented | |
| 189 | Cistercian numerals | not implemented | |
| 190 | Classes | not implemented | |
| 191 | Closest-pair problem | not implemented | |
| 192 | Closures/Value capture | not implemented | |
| 193 | Code Golf | not implemented | |
| 194 | Collections | not implemented | |
| 195 | Color Difference CIE ΔE2000 | not implemented | |
| 196 | Color of a screen pixel | not implemented | |
| 197 | Color quantization | not implemented | |
| 198 | Color wheel | not implemented | |
| 199 | Colorful numbers | not implemented | |
| 200 | Colour bars/Display | not implemented | |
| 201 | Colour pinstripe/Display | not implemented | |
| 202 | Combinations | not implemented | |
| 203 | Combinations and permutations | not implemented | |
| 204 | Combinations with repetitions | implemented | FAILS jmcc - C99 mixed declarations |
| 205 | Comma quibbling | breaks jmcc | compile error: expected type specifier |
| 206 | Command-line arguments | breaks jmcc | wrong output |
| 207 | Comments | not implemented | |
| 208 | Common sorted list | breaks jmcc | compile error: expected type specifier |
| 209 | Compare a list of strings | not implemented | |
| 210 | Compare length of two strings | not implemented | |
| 211 | Compare sorting algorithms' performance | not implemented | |
| 212 | Compile-time calculation | not implemented | |
| 213 | Compiler/AST interpreter | not implemented | |
| 214 | Compiler/code generator | not implemented | |
| 215 | Compiler/lexical analyzer | not implemented | |
| 216 | Compiler/Simple file inclusion pre processor | not implemented | |
| 217 | Compiler/syntax analyzer | not implemented | |
| 218 | Compiler/Verifying syntax | not implemented | |
| 219 | Compiler/virtual machine interpreter | not implemented | |
| 220 | Composite numbers k with no single digit factors whose factors are all substrings of k | not implemented | |
| 221 | Compound data type | not implemented | |
| 222 | Concatenate two primes is also prime | not implemented | |
| 223 | Concurrent computing | not implemented | |
| 224 | Conditional structures | not implemented | |
| 225 | Conjugate transpose | not implemented | |
| 226 | Consecutive primes with ascending or descending differences | not implemented | |
| 227 | Consistent overhead byte stuffing | not implemented | |
| 228 | Constrained random points on a circle | not implemented | |
| 229 | Continued fraction | breaks jmcc | wrong output |
| 230 | Continued fraction/Arithmetic/Construct from rational number | not implemented | |
| 231 | Continued fraction/Arithmetic/G(matrix ng, continued fraction n) | not implemented | |
| 232 | Continued fraction/Arithmetic/G(matrix ng, continued fraction n1, continued fraction n2) | not implemented | |
| 233 | Convert day count to ordinal date | not implemented | |
| 234 | Convert decimal number to rational | not implemented | |
| 235 | Convert seconds to compound duration | not implemented | |
| 236 | Convex hull | breaks jmcc | compile error: expected type specifier |
| 237 | Conway's Game of Life | not implemented | |
| 238 | Coprime triplets | not implemented | |
| 239 | Coprimes | not implemented | |
| 240 | Copy a string | not implemented | |
| 241 | Copy stdin to stdout | not implemented | |
| 242 | CORDIC | not implemented | |
| 243 | Count how many vowels and consonants occur in a string | not implemented | |
| 244 | Count in factors | not implemented | |
| 245 | Count in octal | not implemented | |
| 246 | Count occurrences of a substring | not implemented | |
| 247 | Count the coins | breaks jmcc | compile error: parse failure |
| 248 | Count the occurrence of each digit in e | not implemented | |
| 249 | Cousin primes | not implemented | |
| 250 | Cramer's rule | not implemented | |
| 251 | CRC-32 | not implemented | |
| 252 | Create a file | not implemented | |
| 253 | Create a file on magnetic tape | not implemented | |
| 254 | Create a two-dimensional array at runtime | not implemented | |
| 255 | Create an HTML table | not implemented | |
| 256 | Create an object at a given address | not implemented | |
| 257 | CSV data manipulation | not implemented | |
| 258 | CSV to HTML translation | not implemented | |
| 259 | Cuban primes | not implemented | |
| 260 | Cubic special primes | not implemented | |
| 261 | Cumulative standard deviation | not implemented | |
| 262 | Currency | not implemented | |
| 263 | Currying | breaks jmcc | compile error: parse failure |
| 264 | Curzon numbers | not implemented | |
| 265 | CUSIP | not implemented | |
| 266 | Cut a rectangle | breaks jmcc | compile error: parse failure |
| 267 | Cycle detection | breaks jmcc | compile error: lvalue check |
| 268 | Damm algorithm | not implemented | |
| 269 | Data Encryption Standard | breaks jmcc | compile error: parse failure |
| 270 | Date format | not implemented | |
| 271 | Date manipulation | not implemented | |
| 272 | Day of the week | not implemented | |
| 273 | Day of the week of Christmas and New Year | not implemented | |
| 274 | Days between dates | not implemented | |
| 275 | De Polignac numbers | not implemented | |
| 276 | Deal cards for FreeCell | breaks jmcc | compile error: parse failure |
| 277 | Death Star | not implemented | |
| 278 | Deceptive numbers | not implemented | |
| 279 | Decision tables | not implemented | |
| 280 | Deconvolution/1D | not implemented | |
| 281 | Deconvolution/2D+ | not implemented | |
| 282 | Decorate-sort-undecorate idiom | breaks jmcc | compile error: expected type specifier |
| 283 | Deepcopy | implemented | FAILS jmcc - nested struct float reads as 0.0 |
| 284 | Delegates | implemented | FAILS jmcc - SIGSEGV on typedef'd struct ptr with fn ptrs |
| 285 | Delete a file | not implemented | |
| 286 | Department numbers | not implemented | |
| 287 | Descending primes | not implemented | |
| 288 | Detect division by zero | not implemented | |
| 289 | Determinant and permanent | implemented | FAILS jmcc - SIGSEGV on VLA+double** |
| 290 | Determine if a string has all the same characters | not implemented | |
| 291 | Determine if a string has all unique characters | not implemented | |
| 292 | Determine if a string is collapsible | not implemented | |
| 293 | Determine if a string is numeric | not implemented | |
| 294 | Determine if a string is squeezable | not implemented | |
| 295 | Determine if only one instance is running | not implemented | |
| 296 | Determine if two triangles overlap | implemented | FAILS jmcc - wrong double comparison results |
| 297 | Dice game probabilities | not implemented | |
| 298 | Digit fifth powers | not implemented | |
| 299 | Digital root | not implemented | |
| 300 | Digital root/Multiplicative digital root | not implemented | |
| 301 | Dijkstra's algorithm | not implemented | |
| 302 | Dinesman's multiple-dwelling problem | not implemented | |
| 303 | Dining philosophers | not implemented | |
| 304 | Diophantine linear system solving | not implemented | |
| 305 | Disarium numbers | not implemented | |
| 306 | Discordian date | not implemented | |
| 307 | Discrete Fourier transform | not implemented | |
| 308 | Display a linear combination | not implemented | |
| 309 | Distance and Bearing | not implemented | |
| 310 | Distinct power numbers | not implemented | |
| 311 | Distributed programming | not implemented | |
| 312 | Diversity prediction theorem | not implemented | |
| 313 | DNS query | not implemented | |
| 314 | Documentation | not implemented | |
| 315 | Doomsday rule | not implemented | |
| 316 | Dot product | not implemented | |
| 317 | Double twin primes | not implemented | |
| 318 | Doubly-linked list/Definition | not implemented | |
| 319 | Doubly-linked list/Element definition | not implemented | |
| 320 | Doubly-linked list/Element insertion | not implemented | |
| 321 | Doubly-linked list/Traversal | not implemented | |
| 322 | Dragon curve | not implemented | |
| 323 | Draw a clock | not implemented | |
| 324 | Draw a cuboid | not implemented | |
| 325 | Draw a pixel | not implemented | |
| 326 | Draw a rotating cube | not implemented | |
| 327 | Draw a sphere | not implemented | |
| 328 | Draw pixel 2 | not implemented | |
| 329 | Dutch national flag problem | not implemented | |
| 330 | Eban numbers | skipped | timeout - correct output, just slow unoptimized |
| 331 | Echo server | not implemented | |
| 332 | Egyptian division | not implemented | |
| 333 | EKG sequence convergence | breaks jmcc | compile error: expected type specifier |
| 334 | Element-wise operations | not implemented | |
| 335 | Elementary cellular automaton | not implemented | |
| 336 | Elementary cellular automaton/Random number generator | not implemented | |
| 337 | Elliptic curve arithmetic | not implemented | |
| 338 | Elliptic Curve Digital Signature Algorithm | not implemented | |
| 339 | Emirp primes | breaks jmcc | compile error: parse failure |
| 340 | Empty directory | not implemented | |
| 341 | Empty program | not implemented | |
| 342 | Empty string | not implemented | |
| 343 | Endless maze | not implemented | |
| 344 | Enforced immutability | not implemented | |
| 345 | Entropy | not implemented | |
| 346 | Entropy/Narcissist | not implemented | |
| 347 | Enumerations | not implemented | |
| 348 | Environment variables | not implemented | |
| 349 | Equilibrium index | not implemented | |
| 350 | Erdős-Nicolas numbers | not implemented | |
| 351 | Erdős-primes | not implemented | |
| 352 | Esthetic numbers | not implemented | |
| 353 | Ethiopian multiplication | not implemented | |
| 354 | Euler method | not implemented | |
| 355 | Euler's constant 0.5772... | not implemented | |
| 356 | Euler's identity | not implemented | |
| 357 | Euler's sum of powers conjecture | not implemented | |
| 358 | Evaluate binomial coefficients | not implemented | |
| 359 | Even or odd | not implemented | |
| 360 | Events | not implemented | |
| 361 | Evolutionary algorithm | not implemented | |
| 362 | Exactly three adjacent 3 in lists | breaks jmcc | compile error: expected type specifier |
| 363 | Exceptions | not implemented | |
| 364 | Exceptions/Catch an exception thrown in a nested call | not implemented | |
| 365 | Executable library | not implemented | |
| 366 | Execute a Markov algorithm | not implemented | |
| 367 | Execute a system command | not implemented | |
| 368 | Execute Brain**** | not implemented | |
| 369 | Execute Computer/Zero | not implemented | |
| 370 | Execute HQ9+ | not implemented | |
| 371 | Execute SNUSP | not implemented | |
| 372 | Experimental Verification of the NKT Law: Interpolating the Masses of 8 Planets Using NASA Data as of 30–31/12/2024 | not implemented | |
| 373 | Exponentiation operator | breaks jmcc | wrong output |
| 374 | Exponentiation order | breaks jmcc | link error |
| 375 | Extend your language | not implemented | |
| 376 | Extensible prime generator | not implemented | |
| 377 | Extra primes | not implemented | |
| 378 | Extract file extension | breaks jmcc | compile error: parse failure |
| 379 | Extreme floating point values | breaks jmcc | wrong output |
| 380 | Extreme primes | not implemented | |
| 381 | Factorial | not implemented | |
| 382 | Factorions | not implemented | |
| 383 | Factors of a Mersenne number | not implemented | |
| 384 | Factors of an integer | not implemented | |
| 385 | Fairshare between two and more | not implemented | |
| 386 | Farey sequence | breaks jmcc | compile error: parse failure |
| 387 | Fast Fourier transform | not implemented | |
| 388 | FASTA format | not implemented | |
| 389 | Faulhaber's formula | not implemented | |
| 390 | Faulhaber's triangle | not implemented | |
| 391 | Feigenbaum constant calculation | not implemented | |
| 392 | Fermat numbers | not implemented | |
| 393 | Fibonacci n-step number sequences | not implemented | |
| 394 | Fibonacci sequence | not implemented | |
| 395 | Fibonacci word | not implemented | |
| 396 | Fibonacci word/fractal | not implemented | |
| 397 | File extension is in extensions list | not implemented | |
| 398 | File input/output | not implemented | |
| 399 | File modification time | not implemented | |
| 400 | File size | not implemented | |
| 401 | File size distribution | not implemented | |
| 402 | Filter | not implemented | |
| 403 | Find adjacent primes which differ by a square integer | not implemented | |
| 404 | Find common directory path | not implemented | |
| 405 | Find first and last set bit of a long integer | not implemented | |
| 406 | Find if a point is within a triangle | not implemented | |
| 407 | Find largest left truncatable prime in a given base | not implemented | |
| 408 | Find limit of recursion | not implemented | |
| 409 | Find minimum number of coins that make a given value | not implemented | |
| 410 | Find palindromic numbers in both binary and ternary bases | not implemented | |
| 411 | Find prime n such that reversed n is also prime | not implemented | |
| 412 | Find prime numbers of the form n*n*n+2 | not implemented | |
| 413 | Find square difference | not implemented | |
| 414 | Find squares n where n+1 is prime | not implemented | |
| 415 | Find the intersection of a line with a plane | not implemented | |
| 416 | Find the intersection of two lines | breaks jmcc | compile error |
| 417 | Find the last Sunday of each month | breaks jmcc | compile error: lvalue check |
| 418 | Find the missing permutation | breaks jmcc | wrong output |
| 419 | Find words which contain all the vowels | not implemented | |
| 420 | Find words which contains more than 3 e vowels | not implemented | |
| 421 | Find words whose first and last three letters are equal | not implemented | |
| 422 | Find words with alternating vowels and consonants | not implemented | |
| 423 | Finite state machine | not implemented | |
| 424 | First 9 prime Fibonacci number | not implemented | |
| 425 | First class environments | breaks jmcc | wrong output |
| 426 | First perfect square in base n with n unique digits | not implemented | |
| 427 | First power of 2 that has leading decimal digits of 12 | not implemented | |
| 428 | First-class functions | not implemented | |
| 429 | Five weekends | not implemented | |
| 430 | Fivenum | not implemented | |
| 431 | FizzBuzz | not implemented | |
| 432 | Flatten a list | not implemented | |
| 433 | Flipping bits game | not implemented | |
| 434 | Flow-control structures | not implemented | |
| 435 | Floyd's triangle | breaks jmcc | compile error: parse failure |
| 436 | Floyd-Warshall algorithm | not implemented | |
| 437 | Forbidden numbers | not implemented | |
| 438 | Forest fire | not implemented | |
| 439 | Fork | not implemented | |
| 440 | Formal power series | not implemented | |
| 441 | Formatted numeric output | not implemented | |
| 442 | Fortunate numbers | not implemented | |
| 443 | Forward difference | breaks jmcc | SIGSEGV |
| 444 | Four bit adder | not implemented | |
| 445 | Four is magic | not implemented | |
| 446 | Four is the number of letters in the ... | not implemented | |
| 447 | Four sides of square | not implemented | |
| 448 | Fractal tree | not implemented | |
| 449 | Fraction reduction | not implemented | |
| 450 | Fractran | not implemented | |
| 451 | Frobenius numbers | not implemented | |
| 452 | FTP | not implemented | |
| 453 | Function composition | not implemented | |
| 454 | Function definition | not implemented | |
| 455 | Function frequency | not implemented | |
| 456 | Function prototype | not implemented | |
| 457 | Fusc sequence | not implemented | |
| 458 | Galton box animation | not implemented | |
| 459 | Gamma function | not implemented | |
| 460 | Gapful numbers | not implemented | |
| 461 | Gauss-Jordan matrix inversion | not implemented | |
| 462 | Gaussian elimination | not implemented | |
| 463 | Gaussian primes | not implemented | |
| 464 | General FizzBuzz | skipped | false positive - passes jmcc, SIGPIPE from test harness |
| 465 | Generate Chess960 starting position | not implemented | |
| 466 | Generate lower case ASCII alphabet | not implemented | |
| 467 | Generate random chess position | not implemented | |
| 468 | Generator/Exponential | not implemented | |
| 469 | Generic swap | not implemented | |
| 470 | Get system command output | not implemented | |
| 471 | Getting the number of decimal places | not implemented | |
| 472 | Globally replace text in several files | not implemented | |
| 473 | Go Fish | not implemented | |
| 474 | Golden ratio/Convergence | not implemented | |
| 475 | Gotchas | not implemented | |
| 476 | Gray code | not implemented | |
| 477 | Grayscale image | not implemented | |
| 478 | Greatest common divisor | not implemented | |
| 479 | Greatest element of a list | not implemented | |
| 480 | Greatest subsequential sum | not implemented | |
| 481 | Greedy algorithm for Egyptian fractions | not implemented | |
| 482 | Greyscale bars/Display | not implemented | |
| 483 | Guess the number | not implemented | |
| 484 | Guess the number/With feedback | not implemented | |
| 485 | Guess the number/With feedback (player) | not implemented | |
| 486 | GUI component interaction | not implemented | |
| 487 | GUI enabling/disabling of controls | not implemented | |
| 488 | GUI/Maximum window dimensions | not implemented | |
| 489 | Hailstone sequence | not implemented | |
| 490 | Halt and catch fire | not implemented | |
| 491 | Hamming numbers | breaks jmcc | compile error: unexpected token |
| 492 | Handle a signal | not implemented | |
| 493 | Happy numbers | not implemented | |
| 494 | Harmonic series | not implemented | |
| 495 | Harshad or Niven series | not implemented | |
| 496 | Hash from two arrays | not implemented | |
| 497 | Haversine formula | not implemented | |
| 498 | Hello world/Graphical | not implemented | |
| 499 | Hello world/Line printer | not implemented | |
| 500 | Hello world/Newbie | not implemented | |
| 501 | Hello world/Newline omission | not implemented | |
| 502 | Hello world/Standard error | not implemented | |
| 503 | Hello world/Text | not implemented | |
| 504 | Hello world/Web server | not implemented | |
| 505 | Heronian triangles | not implemented | |
| 506 | Hex dump | not implemented | |
| 507 | Hickerson series of almost integers | not implemented | |
| 508 | Higher-order functions | not implemented | |
| 509 | Hilbert curve | not implemented | |
| 510 | History variables | not implemented | |
| 511 | Hofstadter Figure-Figure sequences | breaks jmcc | compile error: expected type specifier |
| 512 | Hofstadter Q sequence | not implemented | |
| 513 | Hofstadter-Conway $10,000 sequence | not implemented | |
| 514 | Holidays related to Easter | not implemented | |
| 515 | Honaker primes | not implemented | |
| 516 | Honeycombs | not implemented | |
| 517 | Horizontal sundial calculations | not implemented | |
| 518 | Horner's rule for polynomial evaluation | breaks jmcc | SIGSEGV |
| 519 | Host introspection | not implemented | |
| 520 | Hostname | not implemented | |
| 521 | Hough transform | not implemented | |
| 522 | HTTP | not implemented | |
| 523 | HTTPS | not implemented | |
| 524 | HTTPS/Authenticated | not implemented | |
| 525 | Huffman coding | not implemented | |
| 526 | Humble numbers | not implemented | |
| 527 | Hunt the Wumpus | not implemented | |
| 528 | I before E except after C | not implemented | |
| 529 | IBAN | breaks jmcc | compile error: parse failure |
| 530 | Iccanobif primes | not implemented | |
| 531 | Identity matrix | not implemented | |
| 532 | Idiomatically determine all the lowercase and uppercase letters | not implemented | |
| 533 | Idoneal numbers | not implemented | |
| 534 | Image convolution | not implemented | |
| 535 | Image noise | not implemented | |
| 536 | Imaginary base numbers | not implemented | |
| 537 | Implicit type conversion | not implemented | |
| 538 | Include a file | not implemented | |
| 539 | Increasing gaps between consecutive Niven numbers | not implemented | |
| 540 | Increment a numerical string | breaks jmcc | compile error: parse failure |
| 541 | Infinity | not implemented | |
| 542 | Inheritance/Multiple | not implemented | |
| 543 | Inheritance/Single | not implemented | |
| 544 | Input loop | not implemented | |
| 545 | Input/Output for lines of text | not implemented | |
| 546 | Input/Output for pairs of numbers | not implemented | |
| 547 | Integer comparison | not implemented | |
| 548 | Integer overflow | not implemented | |
| 549 | Integer roots | not implemented | |
| 550 | Integer sequence | not implemented | |
| 551 | Intersecting number wheels | not implemented | |
| 552 | Introspection | not implemented | |
| 553 | Inverted index | not implemented | |
| 554 | Inverted syntax | not implemented | |
| 555 | IPC via named pipe | not implemented | |
| 556 | ISBN13 check digit | not implemented | |
| 557 | Isqrt (integer square root) of X | not implemented | |
| 558 | Iterated digits squaring | not implemented | |
| 559 | Iterators | not implemented | |
| 560 | Jacobi symbol | not implemented | |
| 561 | Jacobsthal numbers | not implemented | |
| 562 | Jaro similarity | breaks jmcc | wrong output |
| 563 | Jensen's Device | breaks jmcc | wrong output |
| 564 | Jewels and stones | not implemented | |
| 565 | Jordan-Pólya numbers | not implemented | |
| 566 | JortSort | not implemented | |
| 567 | Josephus problem | not implemented | |
| 568 | Joystick position | not implemented | |
| 569 | JSON | not implemented | |
| 570 | Julia set | not implemented | |
| 571 | Jump anywhere | not implemented | |
| 572 | Just in time processing on a character stream | not implemented | |
| 573 | K-d tree | not implemented | |
| 574 | K-means++ clustering | not implemented | |
| 575 | Kahan summation | breaks jmcc | SIGSEGV |
| 576 | Kaprekar numbers | not implemented | |
| 577 | Kernighans large earthquake problem | not implemented | |
| 578 | Keyboard input/Flush the keyboard buffer | not implemented | |
| 579 | Keyboard input/Keypress check | not implemented | |
| 580 | Keyboard input/Obtain a Y or N response | not implemented | |
| 581 | Keyboard macros | not implemented | |
| 582 | Klarner-Rado sequence | not implemented | |
| 583 | Knapsack problem/0-1 | implemented | FAILS jmcc - wrong DP output |
| 584 | Knapsack problem/Bounded | not implemented | |
| 585 | Knapsack problem/Continuous | not implemented | |
| 586 | Knapsack problem/Unbounded | not implemented | |
| 587 | Knight's tour | not implemented | |
| 588 | Knuth shuffle | not implemented | |
| 589 | Knuth's algorithm S | not implemented | |
| 590 | Koch curve | not implemented | |
| 591 | Kolakoski sequence | not implemented | |
| 592 | Kronecker product | not implemented | |
| 593 | Kronecker product based fractals | not implemented | |
| 594 | Lah numbers | not implemented | |
| 595 | Langton's ant | not implemented | |
| 596 | Largest difference between adjacent primes | not implemented | |
| 597 | Largest five adjacent number | not implemented | |
| 598 | Largest int from concatenated ints | not implemented | |
| 599 | Largest number divisible by its digits | not implemented | |
| 600 | Largest palindrome product | not implemented | |
| 601 | Largest prime factor | not implemented | |
| 602 | Largest product in a grid | not implemented | |
| 603 | Largest proper divisor of n | not implemented | |
| 604 | Last Friday of each month | not implemented | |
| 605 | Last letter-first letter | not implemented | |
| 606 | Last list item | not implemented | |
| 607 | Law of cosines - triples | not implemented | |
| 608 | Leap year | not implemented | |
| 609 | Least common multiple | not implemented | |
| 610 | Least m such that n! + m is prime | not implemented | |
| 611 | Left factorials | not implemented | |
| 612 | Legendre prime counting function | not implemented | |
| 613 | Length of an arc between two angles | not implemented | |
| 614 | Leonardo numbers | not implemented | |
| 615 | Letter frequency | not implemented | |
| 616 | Levenshtein distance | not implemented | |
| 617 | Levenshtein distance/Alignment | not implemented | |
| 618 | Line circle intersection | not implemented | |
| 619 | Linear congruential generator | not implemented | |
| 620 | Linux CPU utilization | not implemented | |
| 621 | List comprehensions | not implemented | |
| 622 | List rooted trees | not implemented | |
| 623 | Literals/Floating point | not implemented | |
| 624 | Literals/Integer | not implemented | |
| 625 | Literals/String | not implemented | |
| 626 | Logical operations | not implemented | |
| 627 | Logistic curve fitting in epidemiology | not implemented | |
| 628 | Long multiplication | breaks jmcc | compile error: parse failure |
| 629 | Long primes | not implemented | |
| 630 | Long stairs | not implemented | |
| 631 | Long year | not implemented | |
| 632 | Longest common prefix | breaks jmcc | compile error: parse failure |
| 633 | Longest common subsequence | not implemented | |
| 634 | Longest common substring | not implemented | |
| 635 | Longest common suffix | not implemented | |
| 636 | Longest increasing subsequence | not implemented | |
| 637 | Longest string challenge | not implemented | |
| 638 | Longest substrings without repeating characters | breaks jmcc | compile error: expected type specifier |
| 639 | Look-and-say sequence | not implemented | |
| 640 | Loop over multiple arrays simultaneously | not implemented | |
| 641 | Loops/Break | not implemented | |
| 642 | Loops/Continue | not implemented | |
| 643 | Loops/Do-while | not implemented | |
| 644 | Loops/Downward for | not implemented | |
| 645 | Loops/For | not implemented | |
| 646 | Loops/For with a specified step | not implemented | |
| 647 | Loops/Foreach | not implemented | |
| 648 | Loops/Increment loop index within loop body | not implemented | |
| 649 | Loops/Infinite | not implemented | |
| 650 | Loops/N plus one half | not implemented | |
| 651 | Loops/Nested | not implemented | |
| 652 | Loops/While | not implemented | |
| 653 | Loops/With multiple ranges | not implemented | |
| 654 | Loops/Wrong ranges | not implemented | |
| 655 | LU decomposition | not implemented | |
| 656 | Lucas-Lehmer test | not implemented | |
| 657 | Lucky and even lucky numbers | not implemented | |
| 658 | Ludic numbers | breaks jmcc | compile error: parse failure |
| 659 | Luhn test of credit card numbers | not implemented | |
| 660 | LZW compression | not implemented | |
| 661 | MAC vendor lookup | not implemented | |
| 662 | Machine code | not implemented | |
| 663 | Mad Libs | not implemented | |
| 664 | Magic 8-ball | not implemented | |
| 665 | Magic constant | not implemented | |
| 666 | Magic squares of doubly even order | breaks jmcc | wrong output |
| 667 | Magic squares of odd order | not implemented | |
| 668 | Magic squares of singly even order | breaks jmcc | wrong output |
| 669 | Magnanimous numbers | not implemented | |
| 670 | Main step of GOST 28147-89 | not implemented | |
| 671 | Make directory path | breaks jmcc | link error |
| 672 | Man or boy test | implemented | FAILS jmcc - &(Type){...} compound literal not lvalue |
| 673 | Mandelbrot set | not implemented | |
| 674 | Map range | not implemented | |
| 675 | Matrix chain multiplication | not implemented | |
| 676 | Matrix digital rain | not implemented | |
| 677 | Matrix multiplication | breaks jmcc | SIGSEGV |
| 678 | Matrix transposition | implemented | FAILS jmcc - VLA pointer-to-array stride bug |
| 679 | Matrix with two diagonals | not implemented | |
| 680 | Matrix-exponentiation operator | not implemented | |
| 681 | Maximum difference between adjacent elements of list | not implemented | |
| 682 | Maximum triangle path sum | not implemented | |
| 683 | Mayan numerals | breaks jmcc | compile error: unexpected token |
| 684 | Maze generation | not implemented | |
| 685 | Maze solving | not implemented | |
| 686 | McNuggets problem | not implemented | |
| 687 | MD4 | not implemented | |
| 688 | MD5 | not implemented | |
| 689 | MD5/Implementation | not implemented | |
| 690 | Median filter | not implemented | |
| 691 | Memory allocation | not implemented | |
| 692 | Memory layout of a data structure | not implemented | |
| 693 | Menu | not implemented | |
| 694 | Mersenne primes | not implemented | |
| 695 | Mertens function | not implemented | |
| 696 | Metaprogramming | not implemented | |
| 697 | Metered concurrency | not implemented | |
| 698 | Metronome | not implemented | |
| 699 | Mian-Chowla sequence | breaks jmcc | wrong output |
| 700 | Middle three digits | not implemented | |
| 701 | Miller-Rabin primality test | not implemented | |
| 702 | Mind boggling card trick | not implemented | |
| 703 | Minesweeper game | not implemented | |
| 704 | Minimum multiple of m where digital sum equals m | not implemented | |
| 705 | Minimum number of cells after, before, above and below NxN squares | not implemented | |
| 706 | Minimum numbers of three lists | not implemented | |
| 707 | Minimum positive multiple in base 10 using only 0 and 1 | not implemented | |
| 708 | Minimum primes | not implemented | |
| 709 | Modular arithmetic | not implemented | |
| 710 | Modular exponentiation | not implemented | |
| 711 | Modular inverse | breaks jmcc | compile error: parse failure |
| 712 | Modulinos | not implemented | |
| 713 | Monads/List monad | breaks jmcc | SIGSEGV |
| 714 | Monads/Maybe monad | not implemented | |
| 715 | Monte Carlo methods | not implemented | |
| 716 | Montgomery reduction | not implemented | |
| 717 | Monty Hall problem | not implemented | |
| 718 | Morpion solitaire | not implemented | |
| 719 | Morse code | not implemented | |
| 720 | Mosaic matrix | not implemented | |
| 721 | Motor | not implemented | |
| 722 | Motzkin numbers | not implemented | |
| 723 | Mouse position | not implemented | |
| 724 | Move-to-front algorithm | breaks jmcc | SIGSEGV |
| 725 | Multi-dimensional array | not implemented | |
| 726 | Multifactorial | not implemented | |
| 727 | Multiline shebang | not implemented | |
| 728 | Multiple distinct objects | not implemented | |
| 729 | Multiple regression | not implemented | |
| 730 | Multiplication tables | not implemented | |
| 731 | Multiplicative order | not implemented | |
| 732 | Multiplicatively perfect numbers | not implemented | |
| 733 | Multisplit | not implemented | |
| 734 | Munchausen numbers | not implemented | |
| 735 | Munching squares | not implemented | |
| 736 | Musical scale | not implemented | |
| 737 | Mutex | not implemented | |
| 738 | Mutual recursion | not implemented | |
| 739 | Möbius function | not implemented | |
| 740 | N'th | breaks jmcc | compile error: expected type specifier |
| 741 | N-body problem | not implemented | |
| 742 | N-grams | not implemented | |
| 743 | N-queens problem | breaks jmcc | compile error: expected type specifier |
| 744 | N-smooth numbers | not implemented | |
| 745 | Named parameters | not implemented | |
| 746 | Naming conventions | not implemented | |
| 747 | Narcissist | not implemented | |
| 748 | Narcissistic decimal number | not implemented | |
| 749 | Native shebang | not implemented | |
| 750 | Natural sorting | not implemented | |
| 751 | Nautical bell | not implemented | |
| 752 | Negative base numbers | not implemented | |
| 753 | Nested function | not implemented | |
| 754 | Nested templated data | breaks jmcc | compile error |
| 755 | Next highest int from digits | not implemented | |
| 756 | Next special primes | not implemented | |
| 757 | Nice primes | not implemented | |
| 758 | Nim game | not implemented | |
| 759 | Nimber arithmetic | not implemented | |
| 760 | Non-continuous subsequences | not implemented | |
| 761 | Non-decimal radices/Convert | not implemented | |
| 762 | Non-decimal radices/Input | not implemented | |
| 763 | Non-decimal radices/Output | not implemented | |
| 764 | Nonoblock | not implemented | |
| 765 | Nth root | breaks jmcc | wrong output |
| 766 | Null object | not implemented | |
| 767 | Number names | breaks jmcc | compile error: parse failure |
| 768 | Number reversal game | not implemented | |
| 769 | Numbers divisible by their individual digits, but not by the product of their digits | not implemented | |
| 770 | Numbers in base 10 that are palindromic in bases 2, 4, and 16 | not implemented | |
| 771 | Numbers in base-16 representation that cannot be written with decimal digits | not implemented | |
| 772 | Numbers k whose divisor sum is equal to the divisor sum of k + 1 | not implemented | |
| 773 | Numbers which are the cube roots of the product of their proper divisors | not implemented | |
| 774 | Numbers whose binary and ternary digit sums are prime | not implemented | |
| 775 | Numbers whose count of divisors is prime | not implemented | |
| 776 | Numbers with equal rises and falls | not implemented | |
| 777 | Numbers with prime digits whose sum is 13 | not implemented | |
| 778 | Numbers with same digit set in base 10 and base 16 | not implemented | |
| 779 | Numeric error propagation | not implemented | |
| 780 | Numeric separator syntax | not implemented | |
| 781 | Numerical integration | not implemented | |
| 782 | Numerical integration/Adaptive Simpson's method | not implemented | |
| 783 | Numerical integration/Gauss-Legendre Quadrature | not implemented | |
| 784 | Numerical integration/Tanh-Sinh Quadrature | not implemented | |
| 785 | O'Halloran numbers | not implemented | |
| 786 | Odd and square numbers | not implemented | |
| 787 | Odd word problem | not implemented | |
| 788 | Old lady swallowed a fly | breaks jmcc | compile error: parse failure |
| 789 | Old Russian measure of length | not implemented | |
| 790 | One of n lines in a file | not implemented | |
| 791 | One-dimensional cellular automata | not implemented | |
| 792 | One-time pad | not implemented | |
| 793 | One-two primes | not implemented | |
| 794 | OpenGL | not implemented | |
| 795 | OpenGL pixel shader | not implemented | |
| 796 | OpenGL/Utah teapot | not implemented | |
| 797 | Operator precedence | not implemented | |
| 798 | Optional parameters | not implemented | |
| 799 | Orbital elements | not implemented | |
| 800 | Order by pair comparisons | not implemented | |
| 801 | Order two numerical lists | not implemented | |
| 802 | Ordered partitions | not implemented | |
| 803 | Ordered words | not implemented | |
| 804 | Ormiston pairs | not implemented | |
| 805 | Ormiston triples | not implemented | |
| 806 | Own digits power sum | not implemented | |
| 807 | P-value correction | not implemented | |
| 808 | Padovan n-step number sequences | breaks jmcc | compile error: expected type specifier |
| 809 | Padovan sequence | not implemented | |
| 810 | Pairs with common factors | not implemented | |
| 811 | Palindrome dates | not implemented | |
| 812 | Palindrome detection | not implemented | |
| 813 | Palindromic gapful numbers | not implemented | |
| 814 | Palindromic primes | not implemented | |
| 815 | Pan base non-primes | not implemented | |
| 816 | Pancake numbers | not implemented | |
| 817 | Pandigital prime | not implemented | |
| 818 | Pangram checker | not implemented | |
| 819 | Paraffins | not implemented | |
| 820 | Parallel brute force | not implemented | |
| 821 | Parallel calculations | not implemented | |
| 822 | Parameterized SQL statement | not implemented | |
| 823 | Parametric polymorphism | not implemented | |
| 824 | Parse an IP Address | not implemented | |
| 825 | Parse command-line arguments | not implemented | |
| 826 | Parsing/RPN calculator algorithm | not implemented | |
| 827 | Parsing/RPN to infix conversion | not implemented | |
| 828 | Parsing/Shunting-yard algorithm | not implemented | |
| 829 | Partial function application | not implemented | |
| 830 | Partition an integer x into n primes | not implemented | |
| 831 | Partition function P | not implemented | |
| 832 | Pascal matrix generation | not implemented | |
| 833 | Pascal's triangle | not implemented | |
| 834 | Pascal's triangle/Puzzle | not implemented | |
| 835 | Password generator | not implemented | |
| 836 | Pathological floating point problems | not implemented | |
| 837 | Peaceful chess queen armies | not implemented | |
| 838 | Peano curve | not implemented | |
| 839 | Pell's equation | not implemented | |
| 840 | Penney's game | not implemented | |
| 841 | Penta-power prime seeds | not implemented | |
| 842 | Pentagram | not implemented | |
| 843 | Percentage difference between images | not implemented | |
| 844 | Percolation/Bond percolation | not implemented | |
| 845 | Percolation/Mean cluster density | not implemented | |
| 846 | Percolation/Mean run density | not implemented | |
| 847 | Percolation/Site percolation | not implemented | |
| 848 | Perfect numbers | not implemented | |
| 849 | Perfect shuffle | not implemented | |
| 850 | Perfect totient numbers | not implemented | |
| 851 | Periodic table | not implemented | |
| 852 | Perlin noise | not implemented | |
| 853 | Permutation test | not implemented | |
| 854 | Permutations | not implemented | |
| 855 | Permutations by swapping | not implemented | |
| 856 | Permutations with repetitions | not implemented | |
| 857 | Permutations/Derangements | not implemented | |
| 858 | Permutations/Rank of a permutation | not implemented | |
| 859 | Permuted multiples | not implemented | |
| 860 | Pernicious numbers | breaks jmcc | compile error: parse failure |
| 861 | Phrase reversals | breaks jmcc | compile error: expected type specifier |
| 862 | User:Phunanon | not implemented | |
| 863 | Pi | not implemented | |
| 864 | Pick random element | not implemented | |
| 865 | Pierpont primes | not implemented | |
| 866 | Pig the dice game | not implemented | |
| 867 | Pig the dice game/Player | not implemented | |
| 868 | Pinstripe/Display | not implemented | |
| 869 | Piprimes | not implemented | |
| 870 | Plasma effect | not implemented | |
| 871 | Play recorded sounds | not implemented | |
| 872 | Playing cards | not implemented | |
| 873 | Plot coordinate pairs | not implemented | |
| 874 | Pointers and references | not implemented | |
| 875 | Poker hand analyser | not implemented | |
| 876 | Pollard's rho algorithm | not implemented | |
| 877 | Polymorphic copy | not implemented | |
| 878 | Polymorphism | not implemented | |
| 879 | Polynomial long division | not implemented | |
| 880 | Polynomial regression | not implemented | |
| 881 | Polyspiral | not implemented | |
| 882 | Population count | breaks jmcc | link error |
| 883 | Power set | not implemented | |
| 884 | Pragmatic directives | not implemented | |
| 885 | Price fraction | not implemented | |
| 886 | Primality by trial division | not implemented | |
| 887 | Primality by Wilson's theorem | not implemented | |
| 888 | Prime conspiracy | not implemented | |
| 889 | Prime decomposition | not implemented | |
| 890 | Prime groups | not implemented | |
| 891 | Prime numbers whose neighboring pairs are tetraprimes | not implemented | |
| 892 | Prime reciprocal sum | not implemented | |
| 893 | Prime triangle | breaks jmcc | wrong output |
| 894 | Primes - allocate descendants to their ancestors | not implemented | |
| 895 | Primes whose first and last number is 3 | not implemented | |
| 896 | Primes whose sum of digits is 25 | not implemented | |
| 897 | Primorial numbers | not implemented | |
| 898 | Print debugging statement | not implemented | |
| 899 | Priority queue | not implemented | |
| 900 | Probabilistic choice | not implemented | |
| 901 | Problem of Apollonius | not implemented | |
| 902 | Product of divisors | not implemented | |
| 903 | Product of min and max prime factors | breaks jmcc | wrong output |
| 904 | Program name | breaks jmcc | wrong output |
| 905 | Program termination | not implemented | |
| 906 | Proper divisors | not implemented | |
| 907 | Pseudo-random numbers/Combined recursive generator MRG32k3a | not implemented | |
| 908 | Pseudo-random numbers/Middle-square method | not implemented | |
| 909 | Pseudo-random numbers/PCG32 | not implemented | |
| 910 | Pseudo-random numbers/Splitmix64 | not implemented | |
| 911 | Pseudo-random numbers/Xorshift star | not implemented | |
| 912 | Punched cards | not implemented | |
| 913 | User:PureFox | not implemented | |
| 914 | User:Pwmiller74 | not implemented | |
| 915 | Pythagoras tree | not implemented | |
| 916 | Pythagorean quadruples | not implemented | |
| 917 | Pythagorean triples | not implemented | |
| 918 | QR decomposition | not implemented | |
| 919 | Quad-power prime seeds | not implemented | |
| 920 | Quaternion | not implemented | |
| 921 | Queue/Definition | not implemented | |
| 922 | Queue/Usage | not implemented | |
| 923 | Quickselect algorithm | not implemented | |
| 924 | Quine | not implemented | |
| 925 | Radical of an integer | not implemented | |
| 926 | Rainbow | breaks jmcc | wrong output |
| 927 | Ramer-Douglas-Peucker line simplification | not implemented | |
| 928 | Ramsey's theorem | not implemented | |
| 929 | Random Latin squares | not implemented | |
| 930 | Random number generator (device) | not implemented | |
| 931 | Random number generator (included) | not implemented | |
| 932 | Random numbers | not implemented | |
| 933 | Range consolidation | breaks jmcc | compile error: expected type specifier |
| 934 | Range expansion | not implemented | |
| 935 | Range extraction | breaks jmcc | compile error: unexpected token |
| 936 | Ranking methods | not implemented | |
| 937 | Rate counter | not implemented | |
| 938 | Rational calculator | not implemented | |
| 939 | Ray-casting algorithm | not implemented | |
| 940 | RCRPG | not implemented | |
| 941 | Read a configuration file | not implemented | |
| 942 | Read a file character by character/UTF8 | not implemented | |
| 943 | Read a file line by line | not implemented | |
| 944 | Read a specific line from a file | not implemented | |
| 945 | Read entire file | not implemented | |
| 946 | Readline interface | not implemented | |
| 947 | Real constants and functions | not implemented | |
| 948 | Recaman's sequence | not implemented | |
| 949 | Record sound | not implemented | |
| 950 | Reduced row echelon form | not implemented | |
| 951 | Regular expressions | breaks jmcc | SIGSEGV |
| 952 | Remote agent/Agent interface | not implemented | |
| 953 | Remote agent/Agent logic | not implemented | |
| 954 | Remote agent/Simulation | not implemented | |
| 955 | Remove duplicate elements | not implemented | |
| 956 | Remove lines from a file | not implemented | |
| 957 | Remove vowels from a string | not implemented | |
| 958 | Rename a file | not implemented | |
| 959 | Rendezvous | not implemented | |
| 960 | Rep-string | breaks jmcc | compile error: parse failure |
| 961 | Repeat | not implemented | |
| 962 | Repeat a string | breaks jmcc | compile error: parse failure |
| 963 | Resistor mesh | breaks jmcc | compile error: parse failure |
| 964 | Retrieve and search chat history | not implemented | |
| 965 | Return multiple values | implemented | FAILS jmcc - large struct return corrupts float |
| 966 | Reverse a string | breaks jmcc | SIGSEGV |
| 967 | Reverse words in a string | not implemented | |
| 968 | RIPEMD-160 | not implemented | |
| 969 | User:Roboticist-Tav | not implemented | |
| 970 | Rock-paper-scissors | not implemented | |
| 971 | Rodrigues’ rotation formula | not implemented | |
| 972 | Roman numerals/Decode | not implemented | |
| 973 | Roman numerals/Encode | not implemented | |
| 974 | Roots of a function | not implemented | |
| 975 | Roots of a quadratic function | not implemented | |
| 976 | Roots of unity | not implemented | |
| 977 | Rosetta Code/Rank languages by popularity | not implemented | |
| 978 | Rot-13 | not implemented | |
| 979 | RPG attributes generator | not implemented | |
| 980 | RSA code | not implemented | |
| 981 | Rule30 | not implemented | |
| 982 | Run as a daemon or service | not implemented | |
| 983 | Run-length encoding | not implemented | |
| 984 | Runge-Kutta method | not implemented | |
| 985 | S-expressions | not implemented | |
| 986 | Safe addition | not implemented | |
| 987 | Safe and Sophie Germain primes | not implemented | |
| 988 | Safe primes and unsafe primes | not implemented | |
| 989 | Sailors, coconuts and a monkey problem | not implemented | |
| 990 | Same fringe | not implemented | |
| 991 | Sattolo cycle | not implemented | |
| 992 | Scope modifiers | not implemented | |
| 993 | Scope/Function names and labels | not implemented | |
| 994 | Sealed classes and methods | not implemented | |
| 995 | Search a list | not implemented | |
| 996 | Search a list of records | implemented | FAILS jmcc - wrong search result |
| 997 | Search in paragraph's text | not implemented | |
| 998 | Secure temporary file | not implemented | |
| 999 | SEDOLs | not implemented | |
| 1000 | Selectively replace multiple instances of a character within a string | not implemented | |
| 1001 | Self numbers | skipped | timeout - 2GB alloc, perf issue not a bug |
| 1002 | Self-contained numbers | not implemented | |
| 1003 | Self-describing numbers | not implemented | |
| 1004 | Semaphore | not implemented | |
| 1005 | Semiprime | breaks jmcc | compile error: parse failure |
| 1006 | Semordnilap | not implemented | |
| 1007 | SEND + MORE = MONEY | not implemented | |
| 1008 | Send email | not implemented | |
| 1009 | Sequence of non-squares | not implemented | |
| 1010 | Sequence of primes by trial division | not implemented | |
| 1011 | Sequence of primorial primes | not implemented | |
| 1012 | Sequence: nth number with exactly n divisors | not implemented | |
| 1013 | Sequence: smallest number greater than previous term with exactly n divisors | not implemented | |
| 1014 | Sequence: smallest number with exactly n divisors | not implemented | |
| 1015 | Set | not implemented | |
| 1016 | Set consolidation | breaks jmcc | compile error: parse failure |
| 1017 | Set of real numbers | not implemented | |
| 1018 | Set puzzle | not implemented | |
| 1019 | Seven-sided dice from five-sided dice | not implemented | |
| 1020 | Sexy primes | not implemented | |
| 1021 | User:SGTMcClain | not implemented | |
| 1022 | SHA-1 | not implemented | |
| 1023 | SHA-256 | not implemented | |
| 1024 | SHA-256 Merkle tree | not implemented | |
| 1025 | Shell one-liner | not implemented | |
| 1026 | Shift list elements to left by 3 | breaks jmcc | compile error: expected type specifier |
| 1027 | Shoelace formula for polygonal area | not implemented | |
| 1028 | Short-circuit evaluation | implemented | FAILS jmcc - # stringify expands before stringifying |
| 1029 | Shortest common supersequence | breaks jmcc | compile error |
| 1030 | Show ASCII table | not implemented | |
| 1031 | Show the (decimal) value of a number of 1s appended with a 3, then squared | not implemented | |
| 1032 | Show the epoch | not implemented | |
| 1033 | Sierpinski arrowhead curve | not implemented | |
| 1034 | Sierpinski carpet | not implemented | |
| 1035 | Sierpinski pentagon | not implemented | |
| 1036 | Sierpinski triangle | not implemented | |
| 1037 | Sierpinski triangle/Graphical | not implemented | |
| 1038 | Sieve of Eratosthenes | not implemented | |
| 1039 | Sign of an integer (signum) | not implemented | |
| 1040 | Simple database | not implemented | |
| 1041 | Simple windowed application | not implemented | |
| 1042 | Simulate input/Keyboard | not implemented | |
| 1043 | Simulate input/Mouse | not implemented | |
| 1044 | Simulated annealing | not implemented | |
| 1045 | Sine wave | not implemented | |
| 1046 | Singleton | not implemented | |
| 1047 | Singly-linked list/Element definition | not implemented | |
| 1048 | Singly-linked list/Element insertion | not implemented | |
| 1049 | Singly-linked list/Element removal | not implemented | |
| 1050 | Singly-linked list/Reversal | not implemented | |
| 1051 | Singly-linked list/Traversal | not implemented | |
| 1052 | Singular value decomposition | not implemented | |
| 1053 | Sleep | not implemented | |
| 1054 | Sleeping Beauty problem | not implemented | |
| 1055 | Smallest multiple | not implemented | |
| 1056 | Smallest power of 6 whose decimal expansion contains n | not implemented | |
| 1057 | Smallest square that begins with n | not implemented | |
| 1058 | Smarandache prime-digital sequence | not implemented | |
| 1059 | Smarandache-Wellin primes | not implemented | |
| 1060 | Smith numbers | not implemented | |
| 1061 | Snake | not implemented | |
| 1062 | Snake and ladder | not implemented | |
| 1063 | SOAP | not implemented | |
| 1064 | Sockets | not implemented | |
| 1065 | Sokoban | not implemented | |
| 1066 | Soloway's recurring rainfall | not implemented | |
| 1067 | Solve a Hidato puzzle | breaks jmcc | compile error: parse failure |
| 1068 | Solve the no connection puzzle | not implemented | |
| 1069 | Sort a list of object identifiers | not implemented | |
| 1070 | Sort an array of composite structures | not implemented | |
| 1071 | Sort an integer array | not implemented | |
| 1072 | Sort disjoint sublist | not implemented | |
| 1073 | Sort numbers lexicographically | not implemented | |
| 1074 | Sort stability | not implemented | |
| 1075 | Sort the letters of string in alphabetical order | breaks jmcc | SIGSEGV |
| 1076 | Sort three variables | not implemented | |
| 1077 | Sort using a custom comparator | breaks jmcc | SIGSEGV |
| 1078 | Sorting algorithms/Bead sort | not implemented | |
| 1079 | Sorting algorithms/Bogosort | not implemented | |
| 1080 | Sorting algorithms/Bubble sort | not implemented | |
| 1081 | Sorting algorithms/Circle sort | breaks jmcc | compile error: parse failure |
| 1082 | Sorting algorithms/Cocktail sort | breaks jmcc | compile error: expected type specifier |
| 1083 | Sorting algorithms/Cocktail sort with shifting bounds | not implemented | |
| 1084 | Sorting algorithms/Comb sort | not implemented | |
| 1085 | Sorting algorithms/Counting sort | not implemented | |
| 1086 | Sorting algorithms/Cycle sort | breaks jmcc | compile error: expected type specifier |
| 1087 | Sorting algorithms/Gnome sort | not implemented | |
| 1088 | Sorting algorithms/Heapsort | not implemented | |
| 1089 | Sorting algorithms/Insertion sort | breaks jmcc | compile error: expected type specifier |
| 1090 | Sorting algorithms/Merge sort | not implemented | |
| 1091 | Sorting algorithms/Pancake sort | not implemented | |
| 1092 | Sorting algorithms/Patience sort | not implemented | |
| 1093 | Sorting algorithms/Permutation sort | breaks jmcc | compile error: expected type specifier |
| 1094 | Sorting algorithms/Quicksort | not implemented | |
| 1095 | Sorting algorithms/Radix sort | not implemented | |
| 1096 | Sorting algorithms/Selection sort | not implemented | |
| 1097 | Sorting algorithms/Shell sort | not implemented | |
| 1098 | Sorting algorithms/Sleep sort | not implemented | |
| 1099 | Sorting algorithms/Stooge sort | not implemented | |
| 1100 | Sorting algorithms/Strand sort | breaks jmcc | compile error: parse failure |
| 1101 | Sorting algorithms/Tree sort on a linked list | not implemented | |
| 1102 | Soundex | breaks jmcc | wrong output |
| 1103 | Sparkline in unicode | not implemented | |
| 1104 | Special characters | not implemented | |
| 1105 | Special divisors | not implemented | |
| 1106 | Special factorials | not implemented | |
| 1107 | Special neighbor primes | not implemented | |
| 1108 | Special variables | not implemented | |
| 1109 | Speech synthesis | not implemented | |
| 1110 | Spelling of ordinal numbers | not implemented | |
| 1111 | Sphenic numbers | not implemented | |
| 1112 | Spinning rod animation/Text | not implemented | |
| 1113 | Spiral matrix | not implemented | |
| 1114 | Split a character string based on change of character | not implemented | |
| 1115 | Spoof game | not implemented | |
| 1116 | SQL-based authentication | not implemented | |
| 1117 | Square but not cube | not implemented | |
| 1118 | Square form factorization | not implemented | |
| 1119 | Square-free integers | not implemented | |
| 1120 | Stable marriage problem | implemented | FAILS jmcc - SIGSEGV on enum-indexed 2D arrays |
| 1121 | Stack | not implemented | |
| 1122 | Stack traces | not implemented | |
| 1123 | Stair-climbing puzzle | not implemented | |
| 1124 | Start from a main routine | not implemented | |
| 1125 | State name puzzle | implemented | FAILS jmcc - SIGSEGV on qsort+sprintf |
| 1126 | Statistics/Basic | not implemented | |
| 1127 | Statistics/Normal distribution | not implemented | |
| 1128 | Steady squares | not implemented | |
| 1129 | Steffensen's method | not implemented | |
| 1130 | Stem-and-leaf plot | not implemented | |
| 1131 | Stern-Brocot sequence | not implemented | |
| 1132 | Stirling numbers of the first kind | not implemented | |
| 1133 | Stirling numbers of the second kind | not implemented | |
| 1134 | Straddling checkerboard | not implemented | |
| 1135 | Strange numbers | not implemented | |
| 1136 | Strange plus numbers | not implemented | |
| 1137 | Strange unique prime triplets | not implemented | |
| 1138 | Stream merge | not implemented | |
| 1139 | String append | not implemented | |
| 1140 | String case | not implemented | |
| 1141 | String comparison | not implemented | |
| 1142 | String concatenation | not implemented | |
| 1143 | String interpolation (included) | not implemented | |
| 1144 | String length | not implemented | |
| 1145 | String matching | breaks jmcc | compile error: parse failure |
| 1146 | String prepend | not implemented | |
| 1147 | Strip a set of characters from a string | not implemented | |
| 1148 | Strip block comments | not implemented | |
| 1149 | Strip comments from a string | not implemented | |
| 1150 | Strip control codes and extended characters from a string | not implemented | |
| 1151 | Strip whitespace from a string/Top and tail | not implemented | |
| 1152 | Strong and weak primes | not implemented | |
| 1153 | Subleq | not implemented | |
| 1154 | Subset sum problem | not implemented | |
| 1155 | Substitution cipher | not implemented | |
| 1156 | Substring | not implemented | |
| 1157 | Substring/Top and tail | not implemented | |
| 1158 | Subtractive generator | not implemented | |
| 1159 | Successive prime differences | not implemented | |
| 1160 | Sudan function | not implemented | |
| 1161 | Sudoku | skipped | already covered |
| 1162 | Sum and product of an array | not implemented | |
| 1163 | Sum and product puzzle | not implemented | |
| 1164 | Sum data type | not implemented | |
| 1165 | Sum digits of an integer | not implemented | |
| 1166 | Sum multiples of 3 and 5 | not implemented | |
| 1167 | Sum of a series | not implemented | |
| 1168 | Sum of divisors | not implemented | |
| 1169 | Sum of elements below main diagonal of matrix | not implemented | |
| 1170 | Sum of first n cubes | not implemented | |
| 1171 | Sum of primes in odd positions is prime | not implemented | |
| 1172 | Sum of square and cube digits of an integer are primes | not implemented | |
| 1173 | Sum of squares | implemented | FAILS jmcc - SIGSEGV on double arrays |
| 1174 | Sum of the digits of n is substring of n | not implemented | |
| 1175 | Sum of two adjacent numbers are primes | not implemented | |
| 1176 | Sum to 100 | not implemented | |
| 1177 | Summarize and say sequence | not implemented | |
| 1178 | Summarize primes | not implemented | |
| 1179 | Summation of primes | not implemented | |
| 1180 | Sunflower fractal | not implemented | |
| 1181 | Super-d numbers | not implemented | |
| 1182 | Superellipse | not implemented | |
| 1183 | Superpermutation minimisation | not implemented | |
| 1184 | Sutherland-Hodgman polygon clipping | not implemented | |
| 1185 | Symmetric difference | implemented | FAILS jmcc - wrong set diff output |
| 1186 | Synchronous concurrency | not implemented | |
| 1187 | System time | breaks jmcc | compile error: parse failure |
| 1188 | Table creation | not implemented | |
| 1189 | Table creation/Postal addresses | not implemented | |
| 1190 | Take notes on the command line | not implemented | |
| 1191 | Tarjan | not implemented | |
| 1192 | Tau function | not implemented | |
| 1193 | Tau number | not implemented | |
| 1194 | Taxicab numbers | implemented | FAILS jmcc - struct array decl parsed as subscript |
| 1195 | Teacup rim text | not implemented | |
| 1196 | Temperature conversion | not implemented | |
| 1197 | Terminal control/Clear the screen | not implemented | |
| 1198 | Terminal control/Coloured text | not implemented | |
| 1199 | Terminal control/Cursor movement | not implemented | |
| 1200 | Terminal control/Cursor positioning | not implemented | |
| 1201 | Terminal control/Dimensions | not implemented | |
| 1202 | Terminal control/Display an extended character | breaks jmcc | binary output |
| 1203 | Terminal control/Hiding the cursor | not implemented | |
| 1204 | Terminal control/Inverse video | not implemented | |
| 1205 | Terminal control/Positional read | not implemented | |
| 1206 | Terminal control/Preserve screen | not implemented | |
| 1207 | Terminal control/Ringing the terminal bell | not implemented | |
| 1208 | Terminal control/Unicode output | breaks jmcc | compile error: unicode escapes unsupported |
| 1209 | Ternary logic | not implemented | |
| 1210 | Test a function | not implemented | |
| 1211 | Test integerness | not implemented | |
| 1212 | Tetris | not implemented | |
| 1213 | Text between | not implemented | |
| 1214 | Text processing/1 | not implemented | |
| 1215 | Text processing/2 | not implemented | |
| 1216 | Text processing/Max licenses in use | not implemented | |
| 1217 | Textonyms | not implemented | |
| 1218 | The ISAAC cipher | not implemented | |
| 1219 | The Name Game | not implemented | |
| 1220 | The sieve of Sundaram | not implemented | |
| 1221 | The Twelve Days of Christmas | breaks jmcc | binary output |
| 1222 | Thiele's interpolation formula | not implemented | |
| 1223 | Three word location | not implemented | |
| 1224 | Thue-Morse | not implemented | |
| 1225 | Tic-tac-toe | not implemented | |
| 1226 | Time a function | not implemented | |
| 1227 | Tokenize a string | not implemented | |
| 1228 | Tokenize a string with escaping | not implemented | |
| 1229 | Tonelli-Shanks algorithm | not implemented | |
| 1230 | Top rank per group | not implemented | |
| 1231 | Topological sort | not implemented | |
| 1232 | Topological sort/Extracted top item | not implemented | |
| 1233 | Topswops | not implemented | |
| 1234 | Total circles area | not implemented | |
| 1235 | Totient function | not implemented | |
| 1236 | Towers of Hanoi | not implemented | |
| 1237 | Trabb Pardo–Knuth algorithm | not implemented | |
| 1238 | Tree traversal | not implemented | |
| 1239 | Trigonometric functions | not implemented | |
| 1240 | Triplet of three numbers | not implemented | |
| 1241 | Truncatable primes | not implemented | |
| 1242 | Truncate a file | not implemented | |
| 1243 | Truth table | not implemented | |
| 1244 | Twin primes | not implemented | |
| 1245 | Two bullet roulette | not implemented | |
| 1246 | Two identical strings | not implemented | |
| 1247 | Two sum | not implemented | |
| 1248 | Two's complement | not implemented | |
| 1249 | Type detection | not implemented | |
| 1250 | Ulam numbers | breaks jmcc | timeout |
| 1251 | Ulam spiral (for primes) | not implemented | |
| 1252 | User:Uli Bellgardt | not implemented | |
| 1253 | Ultra useful primes | not implemented | |
| 1254 | Unbias a random generator | not implemented | |
| 1255 | Undefined values | not implemented | |
| 1256 | Unicode strings | not implemented | |
| 1257 | Unicode variable names | not implemented | |
| 1258 | Unique characters | not implemented | |
| 1259 | Universal Lambda Machine | not implemented | |
| 1260 | Universal Turing machine | not implemented | |
| 1261 | Unix/ls | not implemented | |
| 1262 | Unprimeable numbers | not implemented | |
| 1263 | Untouchable numbers | not implemented | |
| 1264 | Untrusted environment | not implemented | |
| 1265 | UPC | not implemented | |
| 1266 | Update a configuration file | not implemented | |
| 1267 | URL decoding | not implemented | |
| 1268 | URL encoding | not implemented | |
| 1269 | Use another language to call a function | not implemented | |
| 1270 | Useless instructions | not implemented | |
| 1271 | User input/Graphical | not implemented | |
| 1272 | User input/Text | not implemented | |
| 1273 | UTF-8 encode and decode | not implemented | |
| 1274 | Validate International Securities Identification Number | not implemented | |
| 1275 | Vampire number | not implemented | |
| 1276 | Van der Corput sequence | not implemented | |
| 1277 | Van Eck sequence | not implemented | |
| 1278 | Variable declaration reset | not implemented | |
| 1279 | Variable size/Get | not implemented | |
| 1280 | Variable size/Set | not implemented | |
| 1281 | Variable-length quantity | not implemented | |
| 1282 | Variables | not implemented | |
| 1283 | Variadic function | not implemented | |
| 1284 | Vector | not implemented | |
| 1285 | Vector products | not implemented | |
| 1286 | Verhoeff algorithm | not implemented | |
| 1287 | Verify distribution uniformity/Chi-squared test | not implemented | |
| 1288 | Verify distribution uniformity/Naive | not implemented | |
| 1289 | Vibrating rectangles | not implemented | |
| 1290 | Vigenère cipher | not implemented | |
| 1291 | Vigenère cipher/Cryptanalysis | not implemented | |
| 1292 | Vile and Dopey numbers | not implemented | |
| 1293 | Visualize a tree | not implemented | |
| 1294 | VList | not implemented | |
| 1295 | Vogel's approximation method | breaks jmcc | wrong output |
| 1296 | Voronoi diagram | not implemented | |
| 1297 | Wagstaff primes | not implemented | |
| 1298 | Walk a directory/Non-recursively | not implemented | |
| 1299 | Walk a directory/Recursively | not implemented | |
| 1300 | Water collected between towers | not implemented | |
| 1301 | Wave function collapse | not implemented | |
| 1302 | Web scraping | not implemented | |
| 1303 | Weird numbers | breaks jmcc | compile error: expected type specifier |
| 1304 | Welch's t-test | not implemented | |
| 1305 | Wieferich primes | not implemented | |
| 1306 | WiktionaryDumps to words | not implemented | |
| 1307 | Wilson primes of order n | not implemented | |
| 1308 | Window creation | not implemented | |
| 1309 | Window creation/X11 | not implemented | |
| 1310 | Window management | not implemented | |
| 1311 | Wireworld | not implemented | |
| 1312 | Wolstenholme numbers | not implemented | |
| 1313 | Word frequency | not implemented | |
| 1314 | Word wheel | not implemented | |
| 1315 | Word wrap | not implemented | |
| 1316 | Wordle comparison | breaks jmcc | SIGSEGV |
| 1317 | Words containing "the" substring | not implemented | |
| 1318 | Words from neighbour ones | not implemented | |
| 1319 | World Cup group stage | breaks jmcc | compile error: parse failure |
| 1320 | Write entire file | not implemented | |
| 1321 | Write float arrays to a text file | not implemented | |
| 1322 | Write language name in 3D ASCII | not implemented | |
| 1323 | Write to Windows event log | breaks jmcc | wrong output |
| 1324 | Xiaolin Wu's line algorithm | not implemented | |
| 1325 | XML validation | not implemented | |
| 1326 | XML/DOM serialization | not implemented | |
| 1327 | XML/Input | not implemented | |
| 1328 | XML/Output | not implemented | |
| 1329 | XML/XPath | not implemented | |
| 1330 | User:Xorph | not implemented | |
| 1331 | XXXX redacted | not implemented | |
| 1332 | Y combinator | not implemented | |
| 1333 | Yellowstone sequence | not implemented | |
| 1334 | Yin and yang | not implemented | |
| 1335 | Zebra puzzle | not implemented | |
| 1336 | Zeckendorf arithmetic | not implemented | |
| 1337 | Zeckendorf number representation | breaks jmcc | compile error: parse failure |
| 1338 | Zero to the zero power | not implemented | |
| 1339 | Zhang-Suen thinning algorithm | not implemented | |
| 1340 | Zig-zag matrix | not implemented | |
| 1341 | Zsigmondy numbers | breaks jmcc | compile error: parse failure |
