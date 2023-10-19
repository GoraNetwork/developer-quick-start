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

print(main_app_addr)
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

def get_ora_box_name(req_key, addr):
    pub_key = asdk.encoding.decode_address(addr)
    hash_src = pub_key + req_key
    name_hash = hashlib.new("sha512_256", hash_src)
    return name_hash.digest()

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