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

# Query multiple URL sources with aggregation.
@example_url_app.external
def query_oracle_url(request_key: pt.abi.DynamicBytes) -> pt.Expr:

    return pt.Seq(
        gora.query_oracle_urls(
            request_key, None, "handle_oracle_url", [
                {
                    "url": "https://coinmarketcap.com/currencies/bnb/",
                    "value_expr": "regex:>BNB is (?:up|down) ([.0-9]+)% in the last 24 hours",
                    "value_type": 1,
                },
                {
                    "url": "https://coinmarketcap.com/currencies/sol/",
                    "value_expr": "regex:>Solana is (?:up|down) ([.0-9]+)% in the last 24 hours",
                    "value_type": 1,
                },
            ]
        ),
    )

def demo() -> None:

    # Get Algorand API client instance to talk to local Algorand sandbox node.
    algod_client = bk.localnet.get_algod_client()

    # Pick a local account to use for asset creation and tests.
    account = bk.localnet.get_accounts()[0]
    print("Using local account", account.address)

    # Instantiate ApplicationClient to manage our app.
    app_client = bk.client.ApplicationClient(
        client=algod_client,
        app=example_url_app,
        signer=account.signer
    )

    # Deploy our app to the chain.
    print("Deploying the app...")
    app_id, app_addr, txid = app_client.create()
    print("Done, txn ID, app ID, app address:", txid, app_id, app_addr)

    # Supply the app with GORA tokens and ALGO.
    print("Initializing app for GORA...")
    app_client.fund(1000000)
    app_client.call(
        method=init_gora,
        token_ref=gora.token_asset_id,
        main_app_ref=gora.main_app_id,
    )
    gora.setup_algo_deposit(algod_client, account, app_addr)
    gora.setup_token_deposit(algod_client, account, app_addr)

    req_key = uuid.uuid4().bytes;
    box_name = gora.get_ora_box_name(req_key, app_addr)

    # Reset global storage variable that will be populated by the destination app.
    pt.App.globalPut(pt.Bytes("oracle_result"), pt.Bytes("")),

    print("Calling the app")
    result = app_client.call(
        method=query_oracle_url,
        request_key=req_key,
        foreign_apps=[ gora.main_app_id ],
        boxes=[ (gora.main_app_id, box_name) ],
    )

    print("Confirmed in round:", result.tx_info["confirmed-round"])
    print("Txn ID:", result.tx_id)

    inner_logs = [ base64.b64decode(x) for x in result.tx_info["inner-txns"][0]["logs"] ]
    request_id_msg = next(x for x in inner_logs if re.match(br"^req_id-", x))
    print("Request ID:", base64.b32encode(request_id_msg[7:]))

if __name__ == "__main__":
    demo()
