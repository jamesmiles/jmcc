We’re going to write a C compiler.

1. You choose the language the compiler will be written in, however, choose something that prioritises speed of feedback - we don’t want to be wasting time waiting for your compiler to compile each time you make a change
2. Write a plan including
    1. designing an execution harnesses for both ‘freestanding’ and ‘hosted’ execution environments, these should allow you to execute and reliably capture outputs, logs & memory dumps of compiled programs safely (e.g. without crashing the host)
        1. Consider technologies like QEMU (freestanding emulation)
        2. Docker for user mode (hosted) execution environment
    2. acquiring the language standard, decompose it into a list of requirements
    3. Creating a test strategy which includes:
        1. creating programs that exercise aspects of the language standard 
            1. document the expected behaviour/output of each program inline
            2. acquire known working compilers (plural) and verify that these test programs compile
            3. execute the compiled programs (using the execution harness!), capture the ‘execution output’
            4. compare the actual output to the predicted output, if it differs, either:
                1. Your inline documentation / prediction was wrong: correct it
                2. Your inline documentation / prediction was insufficiently specified: improve it
                3. The sample compiler has a bug or undefined behaviour: document our compilers expected behaviour
        2. acquiring & integrating dedicated compiler test suites (like the GCC C Torture Test Suite) which actually separate standard-compliant C from GNU extensions
    4. creating ‘negative’ test cases, programs that shouldn’t compile, and ensuring our compiler doesn’t compile them
    5. your overall ‘reward signal’ should be calculated as the total number of passing tests / total number of tests
    6. Finally you’ll need to write the compiler (JMCC), design a process that provides rapid feedback/reward signal, e.g.
        1. Pick a feature from the standard
        2. Write/modify compiler
        3. Compile test programs
        4. Execute test programs using test harnesses
        5. Review output/logs/memory dumps of failing tests
            1. note: memory dumps and logs are for diagnostic purposes, not a reward signal
        6. If all tests pass 
            1. Check CI from previous commits/ and address any issues
            2. Push to main
            3. Add more tests following our defined test strategy & goto 3; or
            4. Goto 1
        7. Else (tests fail) goto 2
    7. Tests should run on GitHub Actions (CI) & locally
    8. Don’t stop until the compiler is complete
    9. Don’t cheat!
3. Push the plan to main
4. Start executing the plan and don’t crash the computer :)