// This is minimal example program demonstrating the use of Gora off-chain
// computation API. It returns string "Hello Gora!" as the oracle value.

#include "gora_off_chain.h"

static char* basic_result = "Hello Gora!";

GORA_DECLARE_FUNC_MAIN
int gora_main(struct gora_context_t* gora_ctx) {

  gora_ctx->result = basic_result;
  return GORA_RC_SUCCESS;
}
