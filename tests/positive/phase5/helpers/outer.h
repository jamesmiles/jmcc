#ifndef OUTER_H
#define OUTER_H

// This quoted include must search relative to THIS file's directory,
// not relative to the original .c file that included us.
#include "inner.h"

#define OUTER_VAL 100
#endif
