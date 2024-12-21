from pathlib import Path

import algosdk
from algokit_utils import (
    ApplicationClient,
    get_algod_client,
    get_default_localnet_config,
    get_indexer_client,
    get_localnet_default_account,
)
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionWithSigner,
)

# Gathering clients
algod_client_config = get_default_localnet_config("algod")
algod_client = get_algod_client(algod_client_config)
indexer_client_config = get_default_localnet_config("indexer")
indexer_client = get_indexer_client(indexer_client_config)
default_account = get_localnet_default_account(algod_client)

# Creating transactions
sp = algod_client.suggested_params()
payment = algosdk.transaction.PaymentTxn(
    sender=default_account.address, receiver=default_account.address, amt=1000000, sp=sp
)
signed_payment = payment.sign(default_account.private_key)

# Sending transactions
tx_id = algod_client.send_transactions([signed_payment])
print(f"Transaction ID: {tx_id}")

# Transaction groups
atc = AtomicTransactionComposer()
g_pay_1 = algosdk.transaction.PaymentTxn(
    sender=default_account.address,
    receiver=default_account.address,
    amt=10000,
    sp=sp,
    note=b"Hello1",
)
g_pay_2 = algosdk.transaction.PaymentTxn(
    sender=default_account.address,
    receiver=default_account.address,
    amt=10000,
    sp=sp,
    note=b"Hello2",
)
atc.add_transaction(TransactionWithSigner(g_pay_1, default_account.signer))
atc.add_transaction(TransactionWithSigner(g_pay_2, default_account.signer))

response = atc.submit(algod_client)
print(response)

# Old App Client interactions
app_client = ApplicationClient(
    algod_client,
    Path(__file__).parent / "artifacts" / "testing_app" / "arc32_app_spec.json",
    creator=default_account,
    indexer_client=indexer_client,
)
deploy_response = app_client.deploy(
    signer=default_account.signer,
    sender=default_account.address,
    template_values={"VALUE": 1},
    allow_delete=True,
    allow_update=False,
)

## Metadata is accessible via `app` attribute
assert deploy_response.app.app_id == app_client.app_id
## You can infer operation perfomed via `operation_performed` attribute
print(deploy_response.action_taken)
## Response exposes corresponding return type for each operation
print(
    deploy_response.create_response
)  # Set when create or replace operation is performed
print(deploy_response.delete_response)  # Set when replace operation is performed
print(deploy_response.update_response)  # Set when update operation is performed

## Metadata is accessible via `app` attribute
assert deploy_response.app.app_id == app_client.app_id

## Now you can interact with the app via the app client instance
call = app_client.call("call_abi", value="test")
assert call.return_value == "Hello, test"

## Accessing state
assert app_client.get_global_state()["value"] == 1
