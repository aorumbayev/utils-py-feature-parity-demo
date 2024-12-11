import algosdk
from algokit_utils import get_algod_client, get_default_localnet_config, get_localnet_default_account
from algosdk.atomic_transaction_composer import AtomicTransactionComposer, TransactionWithSigner

# Gathering clients
algod_client_config = get_default_localnet_config()
algod_client = get_algod_client(algod_client_config)
default_account = get_localnet_default_account(algod_client)

# Creating transactions
sp = algod_client.suggested_params()
payment = algosdk.transaction.PaymentTxn(sender=default_account.address,
                                         receiver=default_account.address,
                                         amt=1000000,
                                         sp=sp)
signed_payment = payment.sign(default_account.private_key)

# Sending transactions
tx_id = algod_client.send_transactions([signed_payment])
print(f"Transaction ID: {tx_id}")

# Transaction groups
atc = AtomicTransactionComposer()
g_pay_1 = algosdk.transaction.PaymentTxn(sender=default_account.address, receiver=default_account.address, amt=10000, sp=sp, note=b"Hello1")
g_pay_2 = algosdk.transaction.PaymentTxn(sender=default_account.address, receiver=default_account.address, amt=10000, sp=sp, note=b"Hello2")
atc.add_transaction(TransactionWithSigner(g_pay_1, default_account.signer))
atc.add_transaction(TransactionWithSigner(g_pay_2, default_account.signer))

response = atc.submit(algod_client)
print(response)
