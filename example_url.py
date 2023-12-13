import pyteal as pt
import beaker as bk
import uuid
import base64
import re
import gora

class ExampleUrlState:
    last_oracle_value = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        descr="Last oracle value received"
    )

# How much to increase opcode budget in application test call.
# This many dummy methods will be defined and included in call txn group.
op_boost = 2

example_url_app = gora.Application("ExampleUrl", ExampleUrlState, op_boost)

# Response handler.
@example_url_app.gora_handler
def handle_oracle_url(request_id: pt.Bytes, requester_addr: pt.Bytes,
                          oracle_value: pt.Bytes, user_data: pt.Bytes,
                          error_code: pt.Int, source_errors: pt.Int):
    return pt.Seq(
        example_url_app.state.last_oracle_value.set(oracle_value),
    )

# Query a General URL source with regex parsing.
@example_url_app.external
def query_oracle_url(request_key: pt.abi.DynamicBytes) -> pt.Expr:

    return pt.Seq(
        gora.pt_query_general_url(
            request_key, None, "handle_oracle_url", [
                {
                    "url": "https://coinmarketcap.com/currencies/bnb/",
                    "value_expr": "regex:>BNB is (?:up|down) ([.0-9]+)% in the last 24 hours",
                    "value_type": 1,
                },
                {
                    "url": "https://coinmarketcap.com/currencies/solana/",
                    "value_expr": "regex:>Solana is (?:up|down) ([.0-9]+)% in the last 24 hours",
                    "value_type": 1,
                },
            ],
            2 # aggregate for maximum
        ),
    )

if __name__ == "__main__":
    gora.run_demo_app(example_url_app, query_oracle_url, True, op_boost)
