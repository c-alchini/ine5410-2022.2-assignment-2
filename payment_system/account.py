from dataclasses import dataclass
from threading import Lock

from utils.currency import Currency
from utils.logger import LOGGER

# Ideia: Foi adicionado um mutex em cada conta e o mutex é solicitado
# dentro das operações depositar ou sacar. O ponto é que não está implementado
# de modo que o payment_processor tenha que ter os mutexes tanto da conta origem
# como da conta destino antes de realizar as operações entre contas. Se fosse assim, as operações de
# lock e unlock seriam realizadas pela função do payment_processor.

# Optei por deixar os mutexes aqui nas funções de "deposit" e "withdraw" pois
# os comentários do trabalho diziam pra adicionar os códigos relativos a concorrência
# nestas funções. A princípio essa é uma solução que é simples e funciona,
# mas ainda fico na dúvida se teria que ser feito de modo diferente.


@dataclass
class Account:
    """
    Uma classe para representar uma conta bancária.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id: int
        Identificador da conta bancária.
    _bank_id: int
        Identificador do banco no qual a conta bancária foi criada.
    currency : Currency
        Moeda corrente da conta bancária.
    balance : int
        Saldo da conta bancária.
    overdraft_limit : int
        Limite de cheque especial da conta bancária.
    lock : Lock
        Mutex de acesso ao atributo 'balance'

    Métodos
    -------
    info() -> None:
        Printa informações sobre a conta bancária.
    deposit(amount: int) -> None:
        Adiciona o valor `amount` ao saldo da conta bancária.
    withdraw(amount: int) -> None:
        Remove o valor `amount` do saldo da conta bancária.
    """

    _id: int
    _bank_id: int
    currency: Currency
    balance: int = 0
    overdraft_limit: int = 0
    lock = Lock()

    def info(self) -> None:
        """
        Esse método printa informações gerais sobre a conta bancária.
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!
        self.balance = int(self.balance)
        self.overdraft_limit = int(self.overdraft_limit)

        pretty_balance = f"{format(round(self.balance/100), ',d')}.{self.balance%100:02d} {self.currency.name}"
        pretty_overdraft_limit = f"{format(round(self.overdraft_limit/100), ',d')}.{self.overdraft_limit%100:02d} {self.currency.name}"
        LOGGER.info(
            f"Account::{{ _id={self._id}, _bank_id={self._bank_id}, balance={pretty_balance}, overdraft_limit={pretty_overdraft_limit} }}")

    def deposit(self, amount: int) -> bool:
        """
        Esse método deverá adicionar o valor `amount` passado como argumento ao saldo da conta bancária 
        (`balance`). Lembre-se que esse método pode ser chamado concorrentemente por múltiplos 
        PaymentProcessors, então modifique-o para garantir que não ocorram erros de concorrência!
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES NECESSÁRIAS NESTE MÉTODO !

        self.lock.acquire()
        self.balance += amount
        LOGGER.info(f"deposit({amount}) successful!")
        self.lock.release()
        return True

    def withdraw(self, amount: int) -> bool:
        """
        Esse método deverá retirar o valor `amount` especificado do saldo da conta bancária (`balance`).
        Deverá ser retornado um valor bool indicando se foi possível ou não realizar a retirada.
        Lembre-se que esse método pode ser chamado concorrentemente por múltiplos PaymentProcessors, 
        então modifique-o para garantir que não ocorram erros de concorrência!
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES NECESSÁRIAS NESTE MÉTODO !

        self.lock.acquire()
        if self.balance >= amount:
            self.balance -= amount
            LOGGER.info(f"withdraw({amount}) successful!")
            self.lock.release()
            return True
        else:
            overdrafted_amount = abs(self.balance - amount)
            if self.overdraft_limit >= overdrafted_amount:
                self.balance -= amount
                LOGGER.info(f"withdraw({amount}) successful with overdraft!")
                self.lock.release()
                return True
            else:
                LOGGER.warning(f"withdraw({amount}) failed, no balance!")
                self.lock.release()
                return False


@dataclass
class CurrencyReserves:
    """
    Uma classe de dados para armazenar as reservas do banco, que serão usadas
    para câmbio e transferências internacionais.
    OBS: NÃO É PERMITIDO ALTERAR ESSA CLASSE!
    """

    USD: Account = Account(_id=1, _bank_id=0, currency=Currency.USD)
    EUR: Account = Account(_id=2, _bank_id=0, currency=Currency.EUR)
    GBP: Account = Account(_id=3, _bank_id=0, currency=Currency.GBP)
    JPY: Account = Account(_id=4, _bank_id=0, currency=Currency.JPY)
    CHF: Account = Account(_id=5, _bank_id=0, currency=Currency.CHF)
    BRL: Account = Account(_id=6, _bank_id=0, currency=Currency.BRL)
