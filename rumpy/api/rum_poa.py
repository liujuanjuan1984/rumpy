from web3 import Web3


class RumChain:
    def __init__(self, http_url="http://149.56.22.113:8545"):
        self.w3 = Web3(Web3.HTTPProvider(http_url))
        print(self.w3.isConnected())

    def get_balance(self, address):
        _addr = Web3.toChecksumAddress(address)
        balance = self.w3.eth.getBalance(_addr)
        return balance

    def get_transaction(self, transaction_hash: str):
        transaction = self.w3.eth.getTransaction(transaction_hash)
        return transaction
