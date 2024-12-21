from pathlib import Path

from algokit_utils import AlgorandClient, ApplicationSpecification
from algokit_utils.applications.app_client import AppClientMethodCallWithSendParams
from algokit_utils.models.amount import AlgoAmount
from algokit_utils.transactions.transaction_composer import PaymentParams

hello_world_arc32_app_spec = ApplicationSpecification.from_json(
    (
        Path(__file__).parent / "artifacts" / "testing_app" / "arc32_app_spec.json"
    ).read_text()
)

# Gathering clients
algorand = AlgorandClient.default_local_net()
default_account = algorand.account.localnet_dispenser()

# Creating transactions
payment_params = PaymentParams(
    sender=default_account.address,
    receiver=default_account.address,
    amount=AlgoAmount.from_algo(1),
    note=b"Hello World",
)

payment_response = algorand.send.payment(
    PaymentParams(
        sender=default_account.address,
        receiver=default_account.address,
        amount=AlgoAmount.from_algo(1),
        note=b"Hello World",
    )
)
print(payment_response)

# Transaction groups
response = (
    algorand.new_group()
    .add_payment(
        PaymentParams(
            sender=default_account.address,
            receiver=default_account.address,
            amount=AlgoAmount.from_algo(1),
            note=b"Hello World1",
        )
    )
    .add_payment(
        PaymentParams(
            sender=default_account.address,
            receiver=default_account.address,
            amount=AlgoAmount.from_algo(1),
            note=b"Hello World2",
        )
    )
    .send()
)
txn_response_1 = response.transactions[0]
assert txn_response_1.payment
# payment property is coming from TransactionWrapper that mimics behaviour of js-algorand-sdk v3 Transaction object
assert txn_response_1.payment.amt == AlgoAmount.from_algo(
    1
)  # AlgoAmount can be compared to int

## New App Client interactions
### When passing an app spec to app factory, arc32 specs are auto converted ot arc56
factory = algorand.client.get_app_factory(
    app_spec=hello_world_arc32_app_spec, default_sender=default_account.address
)

## Response is a tuple of app client and deploy result
app_client, deploy_response = factory.deploy(
    deploy_time_params={"VALUE": 1}, deletable=True, updatable=False
)
## Now you can interact with the app via the app client instance
call = app_client.send.call(
    AppClientMethodCallWithSendParams(method="call_abi", args=["test"])
)
assert call.abi_return.value == "Hello, test"

## Metadata is accessible via `app` attribute
assert deploy_response.app.app_id == app_client.app_id
## You can infer operation perfomed via `operation_performed` attribute
print(deploy_response.operation_performed)
## Response exposes corresponding return type for each operation
print(
    deploy_response.create_response
)  # Set when create or replace operation is performed
print(deploy_response.delete_response)  # Set when replace operation is performed
print(deploy_response.update_response)  # Set when update operation is performed

## Accessing state
assert app_client.state.global_state.get_all()["value"] == 1
assert app_client.state.global_state.get_value("value") == 1
