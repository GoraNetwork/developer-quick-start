import pyteal as pt
import beaker as bk
import uuid
import base64
import re
import gora

class ExampleConstState:
    last_oracle_value = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        descr="Last oracle value received"
    )

example_const_app = bk.Application("ExampleConst", state=ExampleConstState)

# Opt in to Gora token asset, necessary to make oracle requests.
@example_const_app.external
def init_gora(token_ref: pt.abi.Asset, main_app_ref: pt.abi.Application):
    return gora.pt_init_gora()

# Response handler.
@example_const_app.external
def handle_oracle_const(resp_type: pt.abi.Uint32,
                        resp_body_bytes: pt.abi.DynamicBytes):
    return pt.Seq(
        gora.pt_auth_dest_call(),
        gora.pt_smart_assert(resp_type.get() == pt.Int(1)),
        (resp_body := pt.abi.make(gora.ResponseBody)).decode(resp_body_bytes.get()),
        resp_body.oracle_value.store_into(
            oracle_value := pt.abi.make(pt.abi.DynamicArray[pt.abi.Byte])
        ),
        example_const_app.state.last_oracle_value.set(oracle_value.encode()),
    )

# Query a test oracle source that always returns 1.
@example_const_app.external
def query_oracle_const(request_key: pt.abi.DynamicBytes) -> pt.Expr:

    return pt.Seq(
        # Type of oracle request, see Gora documentation for available types.
        (request_type := pt.abi.Uint64()).set(pt.Int(1)),

        # ID of the oracle source being queried. For this basic test, we are
        # querying a special test source #1.
        (source_id := pt.abi.Uint32()).set(pt.Int(1)),

        # Arguments to pass to the source. This one takes no arguments.
        (source_args := pt.abi.make(pt.abi.DynamicArray[pt.abi.DynamicBytes])).set([]),

        # Maximum age in seconds an oracle source response can have before being
        # discarded as outdated. Set to 0 if not using this feature.
        (max_age := pt.abi.Uint32()).set(pt.Int(0)),

        # Source specification is the structure combining the above elements.
        (source_spec := pt.abi.make(gora.SourceSpec)).set(
            source_id, source_args, max_age
        ),

        # Source specification array needs to be built from it albeit with a
        # single element because Gora supports multiple sources per request.
        (source_spec_arr := pt.abi.make(pt.abi.DynamicArray[gora.SourceSpec])).set(
            [ source_spec ]
        ),

        # Result aggregation method. Set to 0 if unused, see Gora documentation
        # for other valid values.
        (aggr_method := pt.abi.Uint32()).set(pt.Int(0)),

        # Arbitrary user-supplied byte string passed to the destination smart
        # contract along with the response to this oracle request. Can be used,
        # for example, to instruct the destination method on how to handle the
        # response. To keep this example simple, we pass nothing.
        (user_data := pt.abi.DynamicBytes()).set([]),

        # Request specification is the structure describing an oracle request of
        # the chosen type which we now build based on the data above. It then
        # needs to be packed as bytes because specifications for different
        # request types must be handled transparrently ABI type differences.
        (request_spec := pt.abi.make(gora.RequestSpec)).set(
            source_spec_arr, aggr_method, user_data
        ),
        (request_spec_packed := pt.abi.DynamicBytes()).set(request_spec.encode()),

        # Destination smart contract specification, consisting of its app ID and
        # ABI method selector. For simplicity, we will use a method in this same
        # app that makes the request, but it can be any smart contract app.
        (dest_app_id := pt.abi.Uint64()).set(pt.Global.current_application_id()),
        (dest_method_sig := pt.abi.DynamicBytes()).set(pt.Bytes("handle_oracle_const")),
        (dest := pt.abi.make(gora.DestinationSpec)).set(dest_app_id, dest_method_sig),
        (dest_packed := pt.abi.DynamicBytes()).set(dest.encode()),

        # Algorand object references for Gora to include with call to the
        # destination smart contract. In this basic case none are needed.
        (asset_refs := pt.abi.make(pt.abi.DynamicArray[pt.abi.Uint64])).set([]),
        (account_refs := pt.abi.make(pt.abi.DynamicArray[pt.abi.Address])).set([]),
        (app_refs := pt.abi.make(pt.abi.DynamicArray[pt.abi.Uint64])).set([]),
        (box_refs := pt.abi.make(pt.abi.DynamicArray[gora.BoxType])).set([]),

        # Call Gora main smart contract and submit the oracle request.
        pt.InnerTxnBuilder.Begin(),
        pt.InnerTxnBuilder.MethodCall(
            app_id=pt.Int(gora.main_app_id),
            method_signature="request" + gora.request_method_spec,
            args=[ request_spec_packed, dest_packed, request_type, request_key,
                   app_refs, asset_refs, account_refs, box_refs ],
        ),
        pt.InnerTxnBuilder.Submit(),
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
        app=example_const_app,
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
        method=query_oracle_const,
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
