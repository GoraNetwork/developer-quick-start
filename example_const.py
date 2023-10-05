import pyteal as pt
import beaker as bk
import gora
import uuid

example_const_app = bk.Application("ExampleConst")

# Opt in to Gora token asset, necessary to make oracle requests.
@example_const_app.external
def opt_in_gora(token_ref: pt.abi.Asset, main_app_ref: pt.abi.Application):
    return pt.Seq(
        pt.Assert(pt.Txn.sender() == pt.Global.creator_address()),
        pt.InnerTxnBuilder.Begin(),
        pt.InnerTxnBuilder.SetFields({
            pt.TxnField.type_enum: pt.TxnType.AssetTransfer,
            pt.TxnField.xfer_asset: pt.Txn.assets[0],
            pt.TxnField.asset_receiver: pt.Global.current_application_address(),
            pt.TxnField.asset_amount: pt.Int(0)
        }),
        pt.InnerTxnBuilder.Submit(),
        pt.InnerTxnBuilder.Begin(),
        (app_id := pt.abi.Uint64()).set(3),
        pt.InnerTxnBuilder.SetFields({
            pt.TxnField.type_enum: pt.TxnType.ApplicationCall,
            pt.TxnField.application_id: pt.Txn.applications[1],
            pt.TxnField.on_completion: pt.OnComplete.OptIn,
        }),
        pt.InnerTxnBuilder.Submit(),
    )

# Query a test oracle source that always returns 1.
@example_const_app.external
def query_oracle_const(request_key: pt.abi.DynamicBytes) -> pt.Expr:

    return pt.Seq(
        # Oracle requests can be of different types, see documentation for details.
        (request_type := pt.abi.Uint64()).set(pt.Int(1)),

        # The test oracle source that we are querying has the ID of 1.
        (source_id := pt.abi.Uint32()).set(pt.Int(1)),

        # This source takes no arguments, so set empty list as the argument array.
        (source_args := pt.abi.make(pt.abi.DynamicArray[pt.abi.DynamicBytes])).set([]),

        # Don't care about maximum response age.
        (max_age := pt.abi.Uint64()).set(pt.Int(0)),

        # Package the above into an oracle source specification.
        (source_spec := pt.abi.make(gora.SourceSpec)).set(
            source_id, source_args, max_age
        ),

        # Gora supports multiple source specifications per request, but here we
        # use one. Hence we must put it as the only element into an array.
        (source_spec_arr := pt.abi.make(pt.abi.DynamicArray[gora.SourceSpec])).set(
            [ source_spec ]
        ),

        # No aggregation of results is required. Anyhow, it is only applicable
        # when using multiple sources.
        (aggr_method := pt.abi.Uint32()).set(pt.Int(0)),

        # Any byte string can be passed to the destination smart contract along
        # with an oracle request. To keep this example simple, we pass nothing.
        (user_data := pt.abi.DynamicBytes()).set([]),

        # Create a request specification based on the above.
        (request_spec := pt.abi.make(gora.RequestSpec)).set(
            source_spec_arr, aggr_method, user_data
        ),
        (request_spec_packed := pt.abi.DynamicBytes()).set(
            request_spec.encode()
        ),

        # Any smart contract can be called when returning an oracle response,
        # but for simplicity we will call the same one, just a different method.
        (dest_app_id := pt.abi.Uint64()).set(pt.Global.current_application_id()),
        (dest_method_sig := pt.abi.DynamicBytes()).set(
            pt.Bytes("oracle_response" + gora.response_method_spec)
        ),
        (destination := pt.abi.make(gora.DestinationSpec)).set(
            dest_app_id, dest_method_sig
        ),
        (destination_packed := pt.abi.DynamicBytes()).set(
            destination.encode()
        ),

        # TODO explain or remove these args
        (asset_refs := pt.abi.make(pt.abi.DynamicArray[pt.abi.Uint64])).set([]),
        (account_refs := pt.abi.make(pt.abi.DynamicArray[pt.abi.Address])).set([]),
        (app_refs := pt.abi.make(pt.abi.DynamicArray[pt.abi.Uint64])).set([]),
        (box_refs := pt.abi.make(pt.abi.DynamicArray[gora.BoxType])).set([]),

        # Call Gora main smart contract to submit the oracle request.
        pt.InnerTxnBuilder.Begin(),
        pt.InnerTxnBuilder.MethodCall(
            app_id=pt.Int(gora.main_app_id),
            method_signature="request" + gora.request_method_spec,
            args=[ request_spec_packed, destination_packed, request_type,
                   request_key, app_refs, asset_refs, account_refs, box_refs ],
        ),
        pt.InnerTxnBuilder.Submit(),
    )

def demo() -> None:

    # Get Algorand API client instance to talk to local Algorand sandbox node.
    algod_client = bk.localnet.get_algod_client()

    # Get a local account to use for asset creation and tests.
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
    print("Opting the app into GORA main app and token...")
    app_client.fund(1000000)
    app_client.call(
        method=opt_in_gora,
        token_ref=gora.token_asset_id,
        main_app_ref=gora.main_app_id,
    )
    print("Done")

    gora.setup_algo_deposit(algod_client, account, app_addr)
    gora.setup_token_deposit(algod_client, account, app_addr)

    req_key = uuid.uuid4().bytes;
    box_name = gora.get_ora_box_name(req_key, app_addr)

    print("Calling the app...")
    result = app_client.call(
        method=query_oracle_const,
        request_key=req_key,
        foreign_apps=[ gora.main_app_id ],
        boxes=[ (gora.main_app_id, box_name) ],
    )
    print("Done, result:", result.return_value)


if __name__ == "__main__":
    demo()
