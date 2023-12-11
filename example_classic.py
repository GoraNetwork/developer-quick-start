import pyteal as pt
import beaker as bk
import gora

class ExampleClassicState:
    last_oracle_value = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        descr="Last oracle value received"
    )

example_classic_app = gora.Application("ExampleClassic", state=ExampleClassicState)

# Response handler.
@example_classic_app.gora_handler
def handle_oracle_classic(request_id: pt.Bytes, requester_addr: pt.Bytes,
                          oracle_value: pt.Bytes, user_data: pt.Bytes,
                          error_code: pt.Int, source_errors: pt.Int):
    return pt.Seq(
        example_classic_app.state.last_oracle_value.set(oracle_value),
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
    gora.run_demo_app(example_classic_app, query_oracle_classic, True)
