from pathlib import Path

from algokit_utils import AlgorandClient, ApplicationSpecification
from algokit_utils.applications.app_client import AppClientMethodCallWithSendParams
from algokit_utils.models.amount import AlgoAmount
from algokit_utils.transactions.transaction_composer import PaymentParams

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

payment_response = algorand.send.payment(PaymentParams(
                                            sender=default_account.address,
                                            receiver=default_account.address,
                                            amount=AlgoAmount.from_algo(1),
                                            note=b"Hello World",
                                        ))
print(payment_response)

# Transaction groups
pay_params_1 = PaymentParams(sender=default_account.address,
                             receiver=default_account.address,
                             amount=AlgoAmount.from_algo(1),
                             note=b"Hello World1")
pay_params_2 = PaymentParams(sender=default_account.address,
                             receiver=default_account.address,
                             amount=AlgoAmount.from_algo(1),
                             note=b"Hello World2")
response = algorand.new_group().add_payment(pay_params_1).add_payment(pay_params_2).send()
txn_response_1 = response.transactions[0]
assert txn_response_1.payment
# payment property is coming from TransactionWrapper that mimics behaviour of js-algorand-sdk v3 Transaction object
assert txn_response_1.payment.amt == pay_params_1.amount

# Raw App Client interactions
random_account = algorand.account.random()
dispenser_account = algorand.account.localnet_dispenser()
algorand.account.ensure_funded(
    account_to_fund=random_account.address,
    dispenser_account=dispenser_account.address,
    min_spending_balance=AlgoAmount.from_algo(10),
    min_funding_increment=AlgoAmount.from_algo(1),
)

## Manually creating an application
raw_json_spec = Path(__file__).parent / "artifacts" / "testing_app" / "arc32_app_spec.json"
hello_world_arc32_app_spec = ApplicationSpecification.from_json(raw_json_spec.read_text())

# When passing an app spec to app factory, arc32 specs are auto converted ot arc56
factory = algorand.client.get_app_factory(app_spec=hello_world_arc32_app_spec, default_sender=default_account.address)

# Response is a tuple of app client and deploy result
app_client, deploy_result = factory.deploy(
    deploy_time_params={
        "VALUE": 1,
    },
    deletable=True,
    populate_app_call_resources=False,
)

print(deploy_result)

# Now you can interact with the app via the app client instance
call = app_client.send.call(AppClientMethodCallWithSendParams(method="call_abi", args=["test"]))

assert call.return_value
assert call.return_value.return_value == "Hello, test"
