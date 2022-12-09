from locale import currency
import time
from threading import Thread

from globals import *
from payment_system.bank import Bank
from utils.transaction import Transaction, TransactionStatus
from utils.logger import LOGGER
from utils.currency import *

# TODO
#  * Retirar o valor das reservas internacionais do banco:
# talvez criar uma função que verifique qual moeda está sendo utilizada
# e retirar a quantia necessaria das reservas dessa moeda


class PaymentProcessor(Thread):
    """
    Uma classe para representar um processador de pagamentos de um banco.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        Identificador do processador de pagamentos.
    bank: Bank
        Banco sob o qual o processador de pagamentos operará.

    Métodos
    -------
    run():
        Inicia thread to PaymentProcessor
    deposit_bank_reserves(self, amount) -> None:
        Deposita o valor retirado da conta de origem nas reservas da moeda nacional
    withdraw_from_international_reserves(self, currency, amount_converted) -> None:
        Retira o valor convertido das reservas da moeda internacional
    process_transaction(transaction: Transaction) -> TransactionStatus:
        Processa uma transação bancária.
    """

    def __init__(self, _id: int, bank: Bank):
        Thread.__init__(self)
        self._id = _id
        self.bank = bank

    def run(self):
        """
        Esse método deve buscar Transactions na fila de transações do banco e processá-las
        utilizando o método self.process_transaction(self, transaction: Transaction).
        Ele não deve ser finalizado prematuramente (antes do banco realmente fechar).
        """
        # TODO: IMPLEMENTE/MODIFIQUE O CÓDIGO NECESSÁRIO ABAIXO !

        LOGGER.info(
            f"Inicializado o PaymentProcessor {self._id} do Banco {self.bank._id}!")
        queue = banks[self.bank._id].transaction_queue

        # ALTERADO: adicionado condição de parada no while e verificação do tamanho da fila
        operating = True
        while operating:
            try:
                # tenta pegar o semáforo dos consumidores
                self.bank.queue_sem_cons.acquire()
                # pega um transação da fila
                transaction = self.bank.transaction_queue_get()
                # libera o semáforo dos produtores
                self.bank.queue_sem_prod.release()

                # LOGGER.info(
                # f"Transaction_queue do Banco {self.bank._id}: {queue}")
            except Exception as err:
                LOGGER.error(f"Falha em PaymentProcessor.run(): {err}")
            else:
                self.process_transaction(transaction)
            operating = self.bank.operating

        LOGGER.info(
            f"O PaymentProcessor {self._id} do banco {self.bank._id} foi finalizado.")

    # Depositando o valor da transferência nas reservas internas
    # O depósito é feito na conta da própria moeda nacional
    def deposit_bank_reserves(self, amount) -> None:
        if (self.bank.currency == Currency.USD):
            self.bank.reserves.USD.deposit(amount)
        elif (self.bank.currency == Currency.EUR):
            self.bank.reserves.EUR.deposit(amount)
        elif (self.bank.currency == Currency.GBP):
            self.bank.reserves.GBP.deposit(amount)
        elif (self.bank.currency == Currency.JPY):
            self.bank.reserves.JPY.deposit(amount)
        elif (self.bank.currency == Currency.CHF):
            self.bank.reserves.CHF.deposit(amount)
        elif (self.bank.currency == Currency.BRL):
            self.bank.reserves.BRL.deposit(amount)
        # LOGGER.info(
        #     f"Depositado {amount} nas reservas do banco cuja moeda é {self.bank.currency}")

    # Retirando o valor na nova moeda das reservas internacionais do banco
    def withdraw_from_international_reserves(self, currency, amount_converted) -> None:
        if (currency == Currency.USD):
            self.bank.reserves.USD.withdraw(amount_converted)
            # print("Dolares retirados:", amount_converted)
        if (currency == Currency.EUR):
            self.bank.reserves.EUR.withdraw(amount_converted)
            # print("Euros retirados", amount_converted)
        if (currency == Currency.GBP):
            self.bank.reserves.GBP.withdraw(amount_converted)
            # print("Euros retirados", amount_converted)
        if (currency == Currency.JPY):
            self.bank.reserves.JPY.withdraw(amount_converted)
            # print("JPY retirados", amount_converted)
        if (currency == Currency.CHF):
            self.bank.reserves.CHF.withdraw(amount_converted)
            # print("CHF retirados", amount_converted)
        if (currency == Currency.BRL):
            self.bank.reserves.BRL.withdraw(amount_converted)
            # print("BRL retirados", amount_converted)

    def process_transaction(self, transaction: Transaction) -> TransactionStatus:
        """
        Esse método deverá processar as transações bancárias do banco ao qual foi designado.
        Caso a transferência seja realizada para um banco diferente (em moeda diferente), a
        lógica para transações internacionais detalhada no enunciado (README.md) deverá ser
        aplicada.
        Ela deve retornar o status da transacão processada.
        """
        # TODO: IMPLEMENTE/MODIFIQUE O CÓDIGO NECESSÁRIO ABAIXO !

        LOGGER.info(
            f"PaymentProcessor {self._id} do Banco {self.bank._id} iniciando processamento da Transaction {transaction._id}!")
        # LOGGER.info(
        #     f"Da conta {transaction.origin[1]} do banco {transaction.origin[1]} para a conta {transaction.destination[1]} do banco {transaction.origin[0]}")

        # NÃO REMOVA ESSE SLEEP!
        # Ele simula uma latência de processamento para a transação.
        time.sleep(3 * time_unit)

        # ALTERAÇÕES \/

        operating = self.bank.operating
        # Caso o banco feche
        if (not operating):
            return None

        # conta de origem
        origin_acc = self.bank.accounts[transaction.origin[1]]
        # conta de destino
        destination_acc = banks[transaction.destination[0]
                                ].accounts[transaction.destination[1]]

        # tentativa de saque: recebe valor booleano
        withdraw_op = origin_acc.withdraw(transaction.amount)

        if (not withdraw_op):
            # caso não haja dinheiro suficiente na conta
            transaction.set_status(TransactionStatus.FAILED)
            LOGGER.info(
                f"Transaction {transaction._id}, status: {transaction.status}")
            return transaction.status

        # transaction.taxes inicia com valor 0
        if (origin_acc.balance < 0):
            # foi usado cheque especial -> 5% de taxa
            transaction.taxes = transaction.amount * 0.05

        if (transaction.origin[0] == transaction.destination[0]):
            # Transação nacional na mesma moeda
            final_value = transaction.amount - transaction.taxes
            # --> aqui pode ser incrementado o lucro do banco,
            # --> transaction.taxes terá o valor zero ou o valor do cheque especial
            destination_acc.deposit(final_value)
        else:
            # Transação internacional

            # transfere o valor em moeda nacional para a conta de reservas do banco
            self.deposit_bank_reserves(transaction.amount)

            # a taxa será descontada do valor final convertido em moeda estrangeira

            # soma taxa do cheque especial à taxa de transações internacionais (1%)
            transaction.taxes += transaction.amount * 0.01

            # --> aqui pode ser incrementado o lucro do banco,
            # --> transaction.taxes terá o valor de todas as taxas somadas (ou zero)

            # valor que será convertido (com o desconto das taxas)
            value_to_convert = transaction.amount - transaction.taxes

            # taxa de conversão entre as moedas
            transaction.exchange_fee = get_exchange_rate(
                self.bank.currency, transaction.currency)

            # valor final na nova moeda
            final_value = value_to_convert * transaction.exchange_fee

            # retira o valor das reservas internacionais do banco
            self.withdraw_from_international_reserves(
                transaction.currency, final_value)

            # deposita na conta de destino
            destination_acc.deposit(final_value)

        transaction.set_status(TransactionStatus.SUCCESSFUL)
        LOGGER.info(
            f"Transaction {transaction._id}, status: {transaction.status}")
        return transaction.status
