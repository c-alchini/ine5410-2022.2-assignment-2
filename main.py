import argparse
import time
import sys
from logging import INFO, DEBUG
from random import randint
from datetime import datetime, timedelta


from globals import *
from payment_system.bank import Bank
from payment_system.payment_processor import PaymentProcessor
from payment_system.transaction_generator import TransactionGenerator
from utils.currency import Currency
from utils.logger import CH, LOGGER


if __name__ == "__main__":
    # Verificação de compatibilidade da versão do python:
    if sys.version_info < (3, 5):
        sys.stdout.write(
            'Utilize o Python 3.5 ou mais recente para desenvolver este trabalho.\n')
        sys.exit(1)

    # Captura de argumentos da linha de comando:
    parser = argparse.ArgumentParser()
    parser.add_argument("--time_unit", "-u",
                        help="Valor da unidade de tempo de simulação")
    parser.add_argument("--total_time", "-t", help="Tempo total de simulação")
    parser.add_argument("--debug", "-d", help="Printar logs em nível DEBUG")
    args = parser.parse_args()
    if args.time_unit:
        time_unit = float(args.time_unit)
    if args.total_time:
        total_time = int(args.total_time)
    if args.debug:
        debug = True

    # Configura logger
    if debug:
        LOGGER.setLevel(DEBUG)
        CH.setLevel(DEBUG)
    else:
        LOGGER.setLevel(INFO)
        CH.setLevel(INFO)

    # Printa argumentos capturados da simulação
    LOGGER.info(
        f"Iniciando simulação com os seguintes parâmetros:\n\ttotal_time = {total_time}\n\tdebug = {debug}\n")
    time.sleep(3)

    # Inicializa variável `tempo`:
    t = 0

    # Cria os Bancos Nacionais e popula a lista global `banks`:
    for i, currency in enumerate(Currency):

        # Cria Banco Nacional
        bank = Bank(_id=i, currency=currency)

        # Deposita valores aleatórios nas contas internas (reserves) do banco
        bank.reserves.BRL.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.CHF.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.EUR.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.GBP.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.JPY.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.USD.deposit(randint(100_000_000, 10_000_000_000))

        # Adiciona banco na lista global de bancos
        banks.append(bank)

    # ALTERAÇÕES: Criando contas e inicializando bancos
    # Os valores aqui são arbitrários, inclusive o número de contas criadas
    # Não sei se é a ideia do trabalho iniciar as contas aqui. De qualquer modo,
    # está facilitando a execução
    for bank in banks:
        for i in range(10):
            balance = randint(10000, 100000)
            overdraft_limit = balance
            bank.new_account(balance, overdraft_limit)
        bank.open_bank()

    # ALTERAÇÃO: Criação de listas para armazenar as threads
    # Elas serão posteriormente inicializadas e finalizadas
    transaction_threads = []
    processing_threads = []

    # Inicializa gerador de transações e processadores de pagamentos para os Bancos Nacionais:
    for i, bank in enumerate(banks):
        # Cria um TransactionGenerator thread por banco:
        transaction_threads.append(
            TransactionGenerator(_id=i, bank=bank))  # alterado
        # Cria um PaymentProcessor thread por banco.
        # Sua solução completa deverá funcionar corretamente com múltiplos PaymentProcessor threads para cada banco.
        processing_threads.append(PaymentProcessor(_id=i, bank=bank))
        processing_threads.append(PaymentProcessor(_id=(i+6), bank=bank))
        processing_threads.append(PaymentProcessor(_id=(i+12), bank=bank))

    for i in range(len(transaction_threads)):
        transaction_threads[i].start()

    for i in range(len(processing_threads)):
        processing_threads[i].start()

    # As accounts são criadas aqui?
    # Enquanto o tempo total de simuação não for atingido:
    while t < total_time:
        # Aguarda um tempo aleatório antes de criar o próximo cliente:
        dt = randint(0, 3)
        time.sleep(dt * time_unit)

        # Alteração: Criando uma conta nova em cada banco a cada ciclo
        for bank in banks:
            balance = randint(10000, 100000)
            overdraft_limit = balance
            bank.new_account(balance, overdraft_limit)

        # Atualiza a variável tempo considerando o intervalo de criação dos clientes:
        t += dt

    # Finaliza todas as threads
    # TODO

    # ALTERAÇÃO: Fechar os Bancos
    for bank in banks:
        bank.close_bank()

    for i in range(len(transaction_threads)):
        # print(transaction_threads[i].name, transaction_threads[i].is_alive())
        transaction_threads[i].join()

    for i in range(len(processing_threads)):
        processing_threads[i].join()

    # Termina simulação. Após esse print somente dados devem ser printados no console.
    LOGGER.info(f"A simulação chegou ao fim!\n")

    # Cálculo do número de transações incompletas e da média de tempo
    # delas na fila de espera
    trans_incompletas = 0
    soma_medias = timedelta()
    for bank in banks:
        (len_queue, media) = bank.info_transaction_incompleted()
        trans_incompletas += len_queue
        soma_medias += media

    LOGGER.info(
        f"Quantidade total (de todos os bancos) de transações não processadas: {trans_incompletas}")
    LOGGER.info(
        f"Média de tempo destas transações na fila de espera até o fechamento do banco: {soma_medias/6}")
