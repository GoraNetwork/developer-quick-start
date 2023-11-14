import pyteal as pt
import beaker as bk
import uuid
import base64
import re
import gora

class ExampleOffChainState:
    last_oracle_value = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        descr="Last oracle value received"
    )

example_off_chain_app = bk.Application("ExampleOffChain", state=ExampleOffChainState)

# Opt in to Gora token asset, necessary to make oracle requests.
@example_off_chain_app.external
def init_gora(token_ref: pt.abi.Asset, main_app_ref: pt.abi.Application):
    return gora.pt_init_gora()

# Response handler.
@example_off_chain_app.external
def handle_oracle_off_chain(resp_type: pt.abi.Uint32,
                            resp_body_bytes: pt.abi.DynamicBytes):
    return pt.Seq(
        gora.pt_auth_dest_call(),
        gora.pt_smart_assert(resp_type.get() == pt.Int(1)),
        (resp_body := pt.abi.make(gora.ResponseBody)).decode(resp_body_bytes.get()),
        resp_body.oracle_value.store_into(
            oracle_value := pt.abi.make(pt.abi.DynamicBytes)
        ),
        example_off_chain_app.state.last_oracle_value.set(oracle_value.get())
    )

# Make an off-chain computation request.
@example_off_chain_app.external
def query_oracle_off_chain(request_key: pt.abi.DynamicBytes) -> pt.Expr:

    return pt.Seq(
        gora.pt_query_off_chain(
            request_key, None, "handle_oracle_off_chain", 1, 0,
            pt.Bytes("base16", "0x0061736d01000000018f808080000360017f017f60027f7f0060017f0002cd808080000303656e760f5f5f6c696e6561725f6d656d6f727902000103656e7610676f72615f726571756573745f75726c000103656e7617676f72615f7365745f6e6578745f75726c5f706172616d00020382808080000100078c808080000108676f72614d61696e00020c8180808000040a948180800001910101017f41e6002101024002400240024020002802040e03000102030b41808080800041a5808080001080808080002000410c6a10818080800041010f0b024020002d00ac8d060d0041e5000f0b41dc8080800041b181808000108080808000200041ac8d066a1081808080002000419495066a10818080800041010f0b2000200041ac8d066a360208410021010b20010b0bef81808000040041000b25687474703a2f2f6170692e706f7374636f6465732e696f2f706f7374436f6465732f2323000041250b376a736f6e706174683a242e726573756c742e6c61746974756465096a736f6e706174683a242e726573756c742e6c6f6e676974756465000041dc000b5568747470733a2f2f6170692e6f70656e2d6d6574656f2e636f6d2f76312f666f7265636173743f63757272656e745f776561746865723d74727565266c617469747564653d2323266c6f6e6769747564653d2323000041b1010b276a736f6e706174683a242e63757272656e745f776561746865722e74656d70657261747572650000ab81808000076c696e6b696e670208cb808080000700a4010209676f72615f6d61696e0102062e4c2e7374720000250102082e4c2e7374722e310100370010000010010102082e4c2e7374722e320200550102082e4c2e7374722e3303002705cb80808000040e2e726f646174612e2e4c2e7374720000102e726f646174612e2e4c2e7374722e310000102e726f646174612e2e4c2e7374722e320000102e726f646174612e2e4c2e7374722e33000000ac808080000a72656c6f632e434f444505090420010004260200002c030037040451050004570600005d03006a0400770400a6808080000970726f647563657273010c70726f6365737365642d62790105636c616e670631322e302e31"),
            [ pt.Bytes("sm14hp") ],
        ),
    )

if __name__ == "__main__":
    gora.run_demo_app(example_off_chain_app, query_oracle_off_chain)
