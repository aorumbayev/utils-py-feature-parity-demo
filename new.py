from pathlib import Path

from algokit_utils import ApplicationSpecification
from algokit_utils.applications.app_client import AppClient, AppClientParams
from algokit_utils.clients.algorand_client import AlgorandClient
from algokit_utils.models.amount import AlgoAmount
from algokit_utils.transactions.transaction_composer import AppCreateParams, PaymentParams

# Gathering clients
algorand = AlgorandClient.default_local_net()
default_account = algorand.account.localnet_default()

# Creating transactions
payment_params = PaymentParams(
    sender=default_account.address,
    receiver=default_account.address,
    amount=AlgoAmount.from_algo(1),
    note=b"Hello World",
)

payment_response = algorand.send.payment(PaymentParams(
                                            sender=default_account.address,
                                            receiver=default_account.address,
                                            amount=AlgoAmount.from_algo(1),
                                            note=b"Hello World",
                                        ))
print(payment_response)

# Transaction groups
algorand.new_group().add_payment(PaymentParams()).add_payment(PaymentParams()).send()

# Raw App Client interactions
random_account = algorand.account.random()
dispenser_account = algorand.account.localnet_dispenser()
algorand.account.ensure_funded(
    account_fo_fund=random_account.address,
    dispenser_account=dispenser_account.address,
    min_spending_balance=AlgoAmount.from_algo(10),
    min_funding_increment=AlgoAmount.from_algo(1),
)

## Manually creating an application
raw_json_spec = Path(__file__).parent.parent / "artifacts" / "hello_world" / "arc32_app_spec.json"
hello_world_arc32_app_spec = ApplicationSpecification.from_json(raw_json_spec.read_text())
global_schema = hello_world_arc32_app_spec.global_state_schema
local_schema = hello_world_arc32_app_spec.local_state_schema
response = algorand.send.app_create(
    AppCreateParams(
        sender=random_account.address,
        approval_program=hello_world_arc32_app_spec.approval_program,
        clear_state_program=hello_world_arc32_app_spec.clear_program,
        schema={
            "global_ints": global_schema.num_uints,
            "global_bytes": global_schema.num_byte_slices,
            "local_ints": local_schema.num_uints,
            "local_bytes": local_schema.num_byte_slices,
        },  # type: ignore[arg-type]
    )
)

## Using the AppClient
app_client = AppClient(
    AppClientParams(
        default_sender=random_account.address,
        default_signer=random_account.signer,
        app_id=response.app_id,
        algorand=algorand,
        app_spec=hello_world_arc32_app_spec,
    )
)
