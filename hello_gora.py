import pyteal as pt
import beaker as bk
import algosdk as asdk
import hashlib
import uuid

# Application ID of the main Gora smart contract that will be called to
# submit oracle requests. Depends on the Algorand network (mainnet, testnet, etc.)
gora_token_asset_id = 838
gora_main_app_id = 840
gora_token_deposit_amount = 10_000_000_000
gora_algo_deposit_amount = 10_000_000_000

gora_main_abi_spec = open("./main-contract.json", "r").read()
gora_main_app = asdk.abi.Contract.from_json(gora_main_abi_spec)

# TODO remove the below and use gora_main_app above instead
# ABI method argument specs to build signatures for oracle method calls.
gora_request_method_spec = "(byte[],byte[],uint64,byte[],uint64[],uint64[],address[],(byte[],uint64)[])void"
gora_response_method_spec = "(uint32[],byte[])void"

# Definitions of structured data types based on Algorand ABI types that are
# used by the oracle.

# Oracle source specification.
class SourceSpec(pt.abi.NamedTuple):
    source_id: pt.abi.Field[pt.abi.Uint32]
    source_arg_list: pt.abi.Field[pt.abi.DynamicArray[pt.abi.DynamicBytes]]
    max_age: pt.abi.Field[pt.abi.Uint64]

# Oracle request specification.
class RequestSpec(pt.abi.NamedTuple):
    source_specs: pt.abi.Field[pt.abi.DynamicArray[SourceSpec]]
    aggregation: pt.abi.Field[pt.abi.Uint32]
    user_data: pt.abi.Field[pt.abi.DynamicBytes]

# Specification of destination called by the oracle when returning data.
class DestinationSpec(pt.abi.NamedTuple):
    app_id: pt.abi.Field[pt.abi.Uint64]
    method: pt.abi.Field[pt.abi.DynamicBytes]

# Oracle response body.
class ResponseBody(pt.abi.NamedTuple):
    request_id: pt.abi.Field[pt.abi.DynamicArray[pt.abi.Byte]]
    requester_address: pt.abi.Field[pt.abi.Address]
    oracle_return_value: pt.abi.Field[pt.abi.DynamicArray[pt.abi.Byte]]
    user_data: pt.abi.Field[pt.abi.DynamicArray[pt.abi.Byte]]
    error_code: pt.abi.Field[pt.abi.Uint32]
    source_failures: pt.abi.Field[pt.abi.Uint64]

#TODO explain
class BoxType(pt.abi.NamedTuple):
    key: pt.abi.Field[pt.abi.DynamicBytes]
    app_id: pt.abi.Field[pt.abi.Uint64]

hello_gora_app = bk.Application("HelloGora")

# Opt in to Gora token asset, necessary to make oracle requests.
@hello_gora_app.external
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
@hello_gora_app.external
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
        (source_spec := pt.abi.make(SourceSpec)).set(source_id, source_args, max_age),
        
        # Gora supports multiple source specifications per request, but here we
        # use one. Hence we must put it as the only element into an array.
        (source_spec_arr := pt.abi.make(pt.abi.DynamicArray[SourceSpec])).set(
            [ source_spec ]
        ),
        
        # No aggregation of results is required. Anyhow, it is only applicable
        # when using multiple sources.
        (aggr_method := pt.abi.Uint32()).set(pt.Int(0)),
        
        # Any byte string can be passed to the destination smart contract along
        # with an oracle request. To keep this example simple, we pass nothing.
        (user_data := pt.abi.DynamicBytes()).set([]),
        
        # Create a request specification based on the above.
        (request_spec := pt.abi.make(RequestSpec)).set(
            source_spec_arr, aggr_method, user_data
        ),
        (request_spec_packed := pt.abi.DynamicBytes()).set(
            request_spec.encode()
        ),
        
        # Any smart contract can be called when returning an oracle response,
        # but for simplicity we will call the same one, just a different method.
        (dest_app_id := pt.abi.Uint64()).set(pt.Global.current_application_id()),
        (dest_method_sig := pt.abi.DynamicBytes()).set(
            pt.Bytes("oracle_response" + gora_response_method_spec)
        ),
        (destination := pt.abi.make(DestinationSpec)).set(
            dest_app_id, dest_method_sig
        ),
        (destination_packed := pt.abi.DynamicBytes()).set(
            destination.encode()
        ),
        
        # Use current txn ID as the unique request key.
        #DB (request_key := pt.abi.DynamicBytes()).set(pt.Txn.tx_id()),

        # TODO explain or remove these args
        (asset_refs := pt.abi.make(pt.abi.DynamicArray[pt.abi.Uint64])).set([]),
        (account_refs := pt.abi.make(pt.abi.DynamicArray[pt.abi.Address])).set([]),
        (app_refs := pt.abi.make(pt.abi.DynamicArray[pt.abi.Uint64])).set([]),
        (box_refs := pt.abi.make(pt.abi.DynamicArray[BoxType])).set([]),

        # Call Gora main smart contract to submit the oracle request.
        pt.InnerTxnBuilder.Begin(),
        pt.InnerTxnBuilder.MethodCall(
            app_id=pt.Int(gora_main_app_id),
            method_signature="request" + gora_request_method_spec,
            args=[ request_spec_packed, destination_packed, request_type,
                   request_key, app_refs, asset_refs, account_refs, box_refs ],
        ),
        pt.InnerTxnBuilder.Submit(),
    )

def setup_algo_deposit(algod_client, account, app_addr):
    print("Setting up Algo deposit...")
    composer = asdk.atomic_transaction_composer.AtomicTransactionComposer()
    unsigned_payment_txn = asdk.transaction.PaymentTxn(
        sender=account.address,
        sp=algod_client.suggested_params(),
        receiver=asdk.logic.get_application_address(gora_main_app_id),
        amt=gora_algo_deposit_amount,
    )
    signer = asdk.atomic_transaction_composer.AccountTransactionSigner(account.private_key)
    signed_payment_txn = asdk.atomic_transaction_composer.TransactionWithSigner(
        unsigned_payment_txn,
        signer
    )
    composer.add_method_call(
        app_id=gora_main_app_id,
        method=gora_main_app.get_method_by_name("deposit_algo"),
        sender=account.address,
        sp=algod_client.suggested_params(),
        signer=signer,
        method_args=[ signed_payment_txn, app_addr ]
    )
    composer.execute(algod_client, 4)
    print("Done:")

def setup_token_deposit(algod_client, account, app_addr):
    print("Setting up token deposit...")
    composer = asdk.atomic_transaction_composer.AtomicTransactionComposer()
    unsigned_transfer_txn = asdk.transaction.AssetTransferTxn(
        sender=account.address,
        sp=algod_client.suggested_params(),
        receiver=asdk.logic.get_application_address(gora_main_app_id),
        index=gora_token_asset_id,
        amt=gora_token_deposit_amount,
    )
    signer = asdk.atomic_transaction_composer.AccountTransactionSigner(account.private_key)
    signed_transfer_txn = asdk.atomic_transaction_composer.TransactionWithSigner(
        unsigned_transfer_txn,
        signer
    )
    composer.add_method_call(
        app_id=gora_main_app_id,
        method=gora_main_app.get_method_by_name("deposit_token"),
        sender=account.address,
        sp=algod_client.suggested_params(),
        signer=signer,
        method_args=[ signed_transfer_txn, gora_token_asset_id, app_addr ]
    )
    composer.execute(algod_client, 4)
    print("Done")

def get_ora_box_name(req_key, addr):
    pub_key = asdk.encoding.decode_address(addr)
    hash_src = pub_key + req_key
    name_hash = hashlib.new("sha512_256", hash_src)
    return name_hash.digest()

def demo() -> None:

    # Get Algorand API client instance to talk to local Algorand sandbox node.
    algod_client = bk.localnet.get_algod_client()

    # Get a local account to use for asset creation and tests.
    account = bk.localnet.get_accounts()[0]
    print("Using local account", account.address)

    # Instantiate ApplicationClient to manage our app.
    app_client = bk.client.ApplicationClient(
        client=algod_client,
        app=hello_gora_app,
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
        token_ref=gora_token_asset_id,
        main_app_ref=gora_main_app_id,
    )
    print("Done")

    setup_algo_deposit(algod_client, account, app_addr)
    setup_token_deposit(algod_client, account, app_addr)

    req_key = uuid.uuid4().bytes;
    box_name = get_ora_box_name(req_key, app_addr)

    print("Calling the app...")
    result = app_client.call(
        method=query_oracle_const,
        request_key=req_key,
        foreign_apps=[ gora_main_app_id ],
        boxes=[ (gora_main_app_id, box_name) ],
    )
    print("Done, result:", result.return_value)


if __name__ == "__main__":
    demo()
