from typing import Tuple
from queue import Queue
from threading import Lock, Semaphore

from payment_system.account import Account, CurrencyReserves
from utils.transaction import Transaction
from utils.currency import Currency
from utils.logger import LOGGER

queue_max_size = 5


class Bank():
    """
    Uma classe para representar um Banco.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        Identificador do banco.
    currency : Currency
        Moeda corrente das contas bancárias do banco.
    reserves : CurrencyReserves
        Dataclass de contas bancárias contendo as reservas internas do banco.
    operating : bool
        Booleano que indica se o banco está em funcionamento ou não.
    accounts : List[Account]
        Lista contendo as contas bancárias dos clientes do banco.
    transaction_queue : Queue[Transaction]
        Fila FIFO contendo as transações bancárias pendentes que ainda serão processadas.
    queue_lock : Lock()
        Mutex utilizado para inserção/remoção de elementos da fila de transações
    queue_sem_prod : Semaphore()
        Semaforo utilizado pelo transaction_generator para adicionar mais transações na fila
    queue_sem_cons : Semaphore()
        Semaforo utilizado pelo payment_processor para retirar transações da fila

    Métodos
    -------
    open_bank() -> None:
        Inicia o banco: seta o atributo 'operating' para True
    close_bank() -> None:
        Fecha o banco: seta o atributo 'operating' para False
    transaction_queue_put() -> Transaction:
        Insere uma transação na fila de transações
    transaction_queue_get() -> Transaction:
        Retira e retorna o primeiro elemento da fila de transações
    new_account(balance: int = 0, overdraft_limit: int = 0) -> None:
        Cria uma nova conta bancária (Account) no banco.
    new_transfer(origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> None:
        Cria uma nova transação bancária.
    info() -> None:
        Printa informações e estatísticas sobre o funcionamento do banco.

    """

    def __init__(self, _id: int, currency: Currency):
        self._id = _id
        self.currency = currency
        self.reserves = CurrencyReserves()
        self.operating = False
        self.accounts = []
        self.transaction_queue = Queue()  # Alterada lista pela fila
        self.queue_lock = Lock()
        self.queue_sem_prod = Semaphore(queue_max_size)
        self.queue_sem_cons = Semaphore(0)

    def open_bank(self) -> None:
        """
        Esse método seta o atributo 'operating' para True
        """
        print("Abrindo banco", self._id)  # print de teste
        self.operating = True

    def close_bank(self) -> None:
        """
        Esse método seta o atributo 'operating' para False
        """
        self.queue_sem_prod.release(2)
        print("Encerrando banco", self._id)  # print de teste
        self.operating = False

    def transaction_queue_put(self, transaction: Transaction) -> None:
        """
        Esse método insere uma transição na fila de transações
        """
        self.queue_lock.acquire()
        self.transaction_queue.put(transaction)
        self.queue_lock.release()

    def transaction_queue_get(self) -> Transaction:
        """
        Esse método retira e retorna o primeiro elemento da fila de transações
        """
        self.queue_lock.acquire()
        transaction = self.transaction_queue.get()
        self.queue_lock.release()
        return transaction

    def new_account(self, balance: int = 0, overdraft_limit: int = 0) -> None:
        """
        Esse método deverá criar uma nova conta bancária (Account) no banco com determinado
        saldo (balance) e limite de cheque especial (overdraft_limit).
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        # Gera _id para a nova Account
        acc_id = len(self.accounts)

        # Cria instância da classe Account
        acc = Account(_id=acc_id, _bank_id=self._id, currency=self.currency,
                      balance=balance, overdraft_limit=overdraft_limit)

        # LOGGER.info(f"Conta criada no banco {self._id}")
        # acc.info()

        # Adiciona a Account criada na lista de contas do banco
        self.accounts.append(acc)

    def info(self) -> None:
        """
        Essa função deverá printar os seguintes dados utilizando o LOGGER fornecido:
        1. Saldo de cada moeda nas reservas internas do banco
        2. Número de transferências nacionais e internacionais realizadas
        3. Número de contas bancárias registradas no banco
        4. Saldo total de todas as contas bancárias (dos clientes) registradas no banco
        5. Lucro do banco: taxas de câmbio acumuladas + juros de cheque especial acumulados
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        LOGGER.info(f"Estatísticas do Banco Nacional {self._id}:")
        LOGGER.info(f"...")
