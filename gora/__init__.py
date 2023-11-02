import sys
import os
import pyteal as pt
import beaker as bk
import algosdk as asdk
import hashlib
import uuid
import base64

from typing import Literal as L
from .inline import InlineAssembly

def get_env(var, defl=None):
    val = os.environ.get(var)
    if val is None:
        if defl is None:
            raise Exception("Required environment variable not set: " + var)
        else:
            val = defl
    return val

# Application ID of the main Gora smart contract that will be called to
# submit oracle requests. Depends on the Algorand network (mainnet, testnet, etc.)
token_asset_id = int(get_env("GORA_TOKEN_ASSET_ID"))
main_app_id = int(get_env("GORA_MAIN_APP_ID"))

main_app_addr = asdk.logic.get_application_address(main_app_id)
main_app_addr_bin = base64.b32decode(main_app_addr + "======")
main_app_addr_short_bin = main_app_addr_bin[:-4] # remove CRC

gora_token_deposit_amount = int(get_env("GORA_TOKEN_DEPOSIT_AMOUNT", 10_000_000_000))
gora_algo_deposit_amount = int(get_env("GORA_ALGO_DEPOSIT_AMOUNT", 10_000_000_000))

gora_main_abi_spec = open("./main-contract.json", "r").read()
gora_main_app = asdk.abi.Contract.from_json(gora_main_abi_spec)

# ABI method argument specs to build signatures for oracle method calls.
request_method_spec = "(byte[],byte[],uint64,byte[],uint64[],uint64[],address[],(byte[],uint64)[])void"
response_method_spec = "(uint32[],byte[])void"

# Definitions of structured data types based on Algorand ABI types that are
# used by the oracle.

# Oracle source specification.
class SourceSpec(pt.abi.NamedTuple):
    source_id: pt.abi.Field[pt.abi.Uint32]
    source_arg_list: pt.abi.Field[pt.abi.DynamicArray[pt.abi.DynamicBytes]]
    max_age: pt.abi.Field[pt.abi.Uint32]

# Oracle source specification for General URL (type #2) requests.
class SourceSpecUrl(pt.abi.NamedTuple):
    url: pt.abi.Field[pt.abi.DynamicBytes]
    auth_url: pt.abi.Field[pt.abi.DynamicBytes]
    value_expr: pt.abi.Field[pt.abi.DynamicBytes]
    timestamp_expr: pt.abi.Field[pt.abi.DynamicBytes]
    max_age: pt.abi.Field[pt.abi.Uint32]
    value_type: pt.abi.Field[pt.abi.Uint8]
    round_to: pt.abi.Field[pt.abi.Uint8]
    gateway_url: pt.abi.Field[pt.abi.DynamicBytes]
    reserved_0: pt.abi.Field[pt.abi.DynamicBytes]
    reserved_1: pt.abi.Field[pt.abi.DynamicBytes]
    reserved_2: pt.abi.Field[pt.abi.Uint32]
    reserved_3: pt.abi.Field[pt.abi.Uint32]

# Oracle request specification.
class RequestSpec(pt.abi.NamedTuple):
    source_specs: pt.abi.Field[pt.abi.DynamicArray[SourceSpec]]
    aggregation: pt.abi.Field[pt.abi.Uint32]
    user_data: pt.abi.Field[pt.abi.DynamicBytes]

# Oracle General URL (type #2) request specification.
class RequestSpecUrl(pt.abi.NamedTuple):
    source_specs: pt.abi.Field[pt.abi.DynamicArray[SourceSpecUrl]]
    aggregation: pt.abi.Field[pt.abi.Uint32]
    user_data: pt.abi.Field[pt.abi.DynamicBytes]

# Specification of destination called by the oracle when returning data.
class DestinationSpec(pt.abi.NamedTuple):
    app_id: pt.abi.Field[pt.abi.Uint64]
    method: pt.abi.Field[pt.abi.DynamicBytes]

# Oracle response body.
class ResponseBody(pt.abi.NamedTuple):
    request_id: pt.abi.Field[pt.abi.StaticBytes[L[32]]]
    requester_addr: pt.abi.Field[pt.abi.Address]
    oracle_value: pt.abi.Field[pt.abi.DynamicArray[pt.abi.Byte]]
    user_data: pt.abi.Field[pt.abi.DynamicArray[pt.abi.Byte]]
    error_code: pt.abi.Field[pt.abi.Uint32]
    source_errors: pt.abi.Field[pt.abi.Uint64]

# Storage box specification.
class BoxType(pt.abi.NamedTuple):
    key: pt.abi.Field[pt.abi.DynamicBytes]
    app_id: pt.abi.Field[pt.abi.Uint64]

"""
Setup an Algo deposit with Gora for a given account and app.
"""
def setup_algo_deposit(algod_client, account, app_addr):
    print("Setting up Algo deposit...")
    composer = asdk.atomic_transaction_composer.AtomicTransactionComposer()
    unsigned_payment_txn = asdk.transaction.PaymentTxn(
        sender=account.address,
        sp=algod_client.suggested_params(),
        receiver=asdk.logic.get_application_address(main_app_id),
        amt=gora_algo_deposit_amount,
    )
    signer = asdk.atomic_transaction_composer.AccountTransactionSigner(account.private_key)
    signed_payment_txn = asdk.atomic_transaction_composer.TransactionWithSigner(
        unsigned_payment_txn,
        signer
    )
    composer.add_method_call(
        app_id=main_app_id,
        method=gora_main_app.get_method_by_name("deposit_algo"),
        sender=account.address,
        sp=algod_client.suggested_params(),
        signer=signer,
        method_args=[ signed_payment_txn, app_addr ]
    )
    composer.execute(algod_client, 4)

"""
Setup a token deposit with Gora for a given account and app.
"""
def setup_token_deposit(algod_client, account, app_addr):
    print("Setting up token deposit...")
    composer = asdk.atomic_transaction_composer.AtomicTransactionComposer()
    unsigned_transfer_txn = asdk.transaction.AssetTransferTxn(
        sender=account.address,
        sp=algod_client.suggested_params(),
        receiver=asdk.logic.get_application_address(main_app_id),
        index=token_asset_id,
        amt=gora_token_deposit_amount,
    )
    signer = asdk.atomic_transaction_composer.AccountTransactionSigner(account.private_key)
    signed_transfer_txn = asdk.atomic_transaction_composer.TransactionWithSigner(
        unsigned_transfer_txn,
        signer
    )
    composer.add_method_call(
        app_id=main_app_id,
        method=gora_main_app.get_method_by_name("deposit_token"),
        sender=account.address,
        sp=algod_client.suggested_params(),
        signer=signer,
        method_args=[ signed_transfer_txn, token_asset_id, app_addr ]
    )
    composer.execute(algod_client, 4)

"""
Return Algorand storage box name for a Gora request key and requester address.
"""
def get_ora_box_name(req_key, addr):
    pub_key = asdk.encoding.decode_address(addr)
    hash_src = pub_key + req_key
    name_hash = hashlib.new("sha512_256", hash_src)
    return name_hash.digest()

"""
Initialize current Pyteal app for Gora use.
"""
def pt_init_gora():
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

"""
Confirm that current call to a destination app is coming from Gora.
"""
def pt_auth_dest_call():
    return pt.Seq(
        (caller_creator_addr := pt.AppParam.creator(pt.Global.caller_app_id())),
        pt_smart_assert(caller_creator_addr.value() == pt.Bytes(main_app_addr_short_bin)),
    )

"""
Assert with a number to indentify it in API error message. The message will be:
"shr arg too big, (1000000%d)" where in "%d" is the line number.
"""
def pt_smart_assert(cond):
    err_line = sys._getframe().f_back.f_lineno # calling line number
    return pt.If(pt.Not(cond)).Then(
        InlineAssembly("int 0\nint {}\nshr\n".format(1000000 + err_line))
    )

"""
Make an oracle request with specified parameters.
"""
def pt_oracle_request(request_type, request_key, specs_list_abi, dest_app,
                      dest_method, aggr, user_data, box_refs, app_refs,
                      asset_refs, account_refs):

    print("request_type:", request_type)#DB
    spec_class = RequestSpec if request_type == 1 else RequestSpecUrl

    return pt.Seq(
        (request_type_abi := pt.abi.Uint64()).set(request_type),
        (aggr_abi := pt.abi.Uint32()).set(pt.Int(aggr)),
            (user_data_abi := pt.abi.DynamicBytes()).set(pt.Bytes(user_data)),

        (dest_app_abi := pt.abi.Uint64()).set(
            dest_app or pt.Global.current_application_id()),
        (dest_selector_abi := pt.abi.DynamicBytes()).set(pt.Bytes(dest_method)),
        (dest := pt.abi.make(DestinationSpec)).set(dest_app_abi, dest_selector_abi),
        (dest_abi := pt.abi.DynamicBytes()).set(dest.encode()),

        (box_refs_abi := pt.abi.make(pt.abi.DynamicArray[BoxType])).set(box_refs),
        (asset_refs_abi := pt.abi.make(pt.abi.DynamicArray[pt.abi.Uint64])).set(
            asset_refs),
        (account_refs_abi := pt.abi.make(pt.abi.DynamicArray[pt.abi.Address])).set(
            account_refs),
        (app_refs_abi := pt.abi.make(pt.abi.DynamicArray[pt.abi.Uint64])).set(
            app_refs),

        (request_spec := pt.abi.make(spec_class)).set(
            specs_list_abi, aggr_abi, user_data_abi,
        ),
        (request_spec_abi := pt.abi.DynamicBytes()).set(request_spec.encode()),

        pt.InnerTxnBuilder.Begin(),
        pt.InnerTxnBuilder.MethodCall(
            app_id=pt.Int(main_app_id),
            method_signature="request" + request_method_spec,
            args=[ request_spec_abi, dest_abi, request_type_abi, request_key,
                   app_refs_abi, asset_refs_abi, account_refs_abi, box_refs_abi ],
        ),
        pt.InnerTxnBuilder.Submit(),
    )

"""
Make a General URL request with one or more URL sources.
"""
def pt_query_general_url(request_key, dest_app, dest_method, specs_params,
                         aggr = 0, user_data = "", box_refs = [],
                         asset_refs = [], account_refs = [], app_refs = []):

    spec_defaults = {
        "timestamp_expr": "",
        "max_age": 0,
        "round_to": 0,
        "auth_url": "",
        "gateway_url": "",
    }

    result = [
        (url_abi := pt.abi.DynamicBytes()).set(""),
        (value_expr_abi := pt.abi.DynamicBytes()).set(""),
        (timestamp_expr_abi := pt.abi.DynamicBytes()).set(""),
        (auth_url_abi := pt.abi.DynamicBytes()).set(""),
        (gateway_url_abi := pt.abi.DynamicBytes()).set(""),
        (max_age_abi := pt.abi.Uint32()).set(pt.Int(0)),
        (value_type_abi := pt.abi.Uint8()).set(pt.Int(0)),
        (round_to_abi := pt.abi.Uint8()).set(pt.Int(0)),
        (reserved_0_abi := pt.abi.DynamicBytes()).set(pt.Bytes("")),
        (reserved_1_abi := pt.abi.DynamicBytes()).set(pt.Bytes("")),
        (reserved_2_abi := pt.abi.Uint32()).set(pt.Int(0)),
        (reserved_3_abi := pt.abi.Uint32()).set(pt.Int(0)),
    ]

    specs_list = []
    for params in specs_params:
        spec = spec_defaults | params

        result.extend([
            url_abi.set(pt.Bytes(spec["url"])),
            value_expr_abi.set(pt.Bytes(spec["value_expr"])),
            timestamp_expr_abi.set(pt.Bytes(spec["timestamp_expr"])),
            auth_url_abi.set(pt.Bytes(spec["auth_url"])),
            gateway_url_abi.set(pt.Bytes(spec["gateway_url"])),
            max_age_abi.set(pt.Int(spec["max_age"])),
            value_type_abi.set(pt.Int(spec["value_type"])),
            round_to_abi.set(pt.Int(spec["round_to"])),

            (spec_abi := pt.abi.make(SourceSpecUrl)).set(
                url_abi, auth_url_abi, value_expr_abi, timestamp_expr_abi,
                max_age_abi, value_type_abi, round_to_abi, gateway_url_abi,
                reserved_0_abi, reserved_1_abi, reserved_2_abi, reserved_3_abi,
            ),
        ]),
        specs_list.append(spec_abi),

    result.extend([
        (specs_list_abi := pt.abi.make(pt.abi.DynamicArray[SourceSpecUrl])).set(
            specs_list),
        pt_oracle_request(2, request_key, specs_list_abi, dest_app, dest_method,
                          aggr, user_data, box_refs, app_refs, asset_refs,
                          account_refs),

    ])

    return pt.Seq(result)

"""
Make a classic request with one or more URL sources.
"""
def pt_query_classic(request_key, dest_app, dest_method, specs_params,
                     aggr = 0, user_data = "", box_refs = [],
                     asset_refs = [], account_refs = [], app_refs = []):

    result = [];
    specs_list = []

    for spec in specs_params:
        args_pre_abi = [];
        for arg in spec.get("args", []):
            result.append((arg_abi := pt.abi.DynamicBytes()).set(pt.Bytes(arg)))
            args_pre_abi.append(arg_abi)

        result.extend([
            (id_abi := pt.abi.Uint32()).set(pt.Int(spec["id"])),
            (max_age_abi := pt.abi.Uint32()).set(pt.Int(spec.get("max_age", 0))),
            (args_abi := pt.abi.make(pt.abi.DynamicArray[pt.abi.DynamicBytes])).set(
                args_pre_abi),
            (spec_abi := pt.abi.make(SourceSpec)).set(
                id_abi, args_abi, max_age_abi),
        ])
        specs_list.append(spec_abi)

    result.extend([
        (specs_list_abi := pt.abi.make(pt.abi.DynamicArray[SourceSpec])).set(
            specs_list),
        pt_oracle_request(1, request_key, specs_list_abi, dest_app, dest_method,
                          aggr, user_data, box_refs, app_refs, asset_refs,
                          account_refs),
    ])

    return pt.Seq(result)
