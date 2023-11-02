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

example_url_app = bk.Application("ExampleUrl", state=ExampleUrlState)

# Opt in to Gora token asset, necessary to make oracle requests.
@example_url_app.external
def init_gora(token_ref: pt.abi.Asset, main_app_ref: pt.abi.Application):
    return gora.pt_init_gora()

# Response handler.
@example_url_app.external
def handle_oracle_url(resp_type: pt.abi.Uint32,
                        resp_body_bytes: pt.abi.DynamicBytes):
    return pt.Seq(
        gora.pt_auth_dest_call(),
        gora.pt_smart_assert(resp_type.get() == pt.Int(1)),
        (resp_body := pt.abi.make(gora.ResponseBody)).decode(resp_body_bytes.get()),
        resp_body.oracle_value.store_into(
            oracle_value := pt.abi.make(pt.abi.DynamicArray[pt.abi.Byte])
        ),
        example_url_app.state.last_oracle_value.set(oracle_value.encode()),
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
            ]
        ),
    )

if __name__ == "__main__":
    gora.run_demo_app(example_url_app, query_oracle_url)
