import pyteal as pt
import beaker as bk
import gora

class ExampleClassicState:
    last_oracle_value = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        descr="Last oracle value received"
    )

example_classic_app = bk.Application("ExampleClassic", state=ExampleClassicState)

# Opt in to Gora token asset, necessary to make oracle requests.
@example_classic_app.external
def init_gora(token_ref: pt.abi.Asset, main_app_ref: pt.abi.Application):
    return gora.pt_init_gora()

# Response handler.
@example_classic_app.external
def handle_oracle_classic(resp_type: pt.abi.Uint32,
                        resp_body_bytes: pt.abi.DynamicBytes):
    return pt.Seq(
        gora.pt_auth_dest_call(),
        gora.pt_smart_assert(resp_type.get() == pt.Int(1)),
        (resp_body := pt.abi.make(gora.ResponseBody)).decode(resp_body_bytes.get()),
        resp_body.oracle_value.store_into(
            oracle_value := pt.abi.make(pt.abi.DynamicArray[pt.abi.Byte])
        ),
        example_classic_app.state.last_oracle_value.set(oracle_value.encode()),
    )

# Query multiple classic sources with aggregation.
@example_classic_app.external
def query_oracle_classic(request_key: pt.abi.DynamicBytes) -> pt.Expr:

    return pt.Seq(
        gora.pt_query_classic(
            request_key, None, "handle_oracle_classic", [
                { "id": 7, "args": [ "##signKey", "btc", "usd" ] },
                { "id": 7, "args": [ "##signKey", "eth", "usd" ] },
            ],
            2, # return maximum value
        ),
    )

if __name__ == "__main__":
    gora.run_demo_app(example_classic_app, query_oracle_classic)
