/* Regression: arm64-apple-darwin target must predefine
 * __ENVIRONMENT_MAC_OS_X_VERSION_MIN_REQUIRED__ (which clang sets to the
 * deployment target, e.g. 150000 for macOS 15) so that AvailabilityMacros.h
 * can derive MAC_OS_X_VERSION_MIN_REQUIRED from it.
 *
 * Without this predefinition, SDL2's SDL_platform.h emits:
 *   #error SDL for Mac OS X only supports deploying on 10.7 and above.
 * blocking compilation of all SDL-using Chocolate Doom source files.
 *
 * clang -target arm64-apple-darwin automatically defines this macro;
 * jmcc must do the same.
 */

#include <AvailabilityMacros.h>

#ifndef MAC_OS_X_VERSION_MIN_REQUIRED
#error MAC_OS_X_VERSION_MIN_REQUIRED not defined - arm64-apple-darwin target missing deployment target predefined macros
#endif

#if MAC_OS_X_VERSION_MIN_REQUIRED < 1070
#error MAC_OS_X_VERSION_MIN_REQUIRED is less than 1070 (macOS 10.7)
#endif

int main(void) {
    return 0;
}
