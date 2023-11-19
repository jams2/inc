#include "startup.h"
#include <stdio.h>

void print_ptr_rec(ptr x) {
  if ((x & fxmask) == fxtag) {
    printf("%ld", ((int64_t)x) >> fxshift);
  } else if (x == bool_f) {
    printf("#f");
  } else if (x == bool_t) {
    printf("#t");
  } else if (x == null) {
    printf("()");
  } else if ((x & chrmask) == chrtag) {
    int c = x >> chrshift;
    if (c == char_tab) {
      printf("#\\tab");
    } else if (c == char_return) {
      printf("#\\return");
    } else if (c == char_newline) {
      printf("#\\newline");
    } else if (c == char_ff) {
      printf("#\\ff");
    } else if (c == char_vt) {
      printf("#\\vt");
    } else if (c == char_space) {
      printf("#\\space");
    } else {
      printf("#\\%c", c);
    }
  }
}

void print_ptr(ptr x) {
  print_ptr_rec(x);
  printf("\n");
}

int main() {
  print_ptr(scheme_entry());
  return 0;
}
