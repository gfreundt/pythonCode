import time
from threading import Thread
from updates import *


def gather_no_threads(db_conn, db_cursor, monitor, all_updates):

    # auto gathering
    gather_brevetes.gather(db_cursor, monitor, all_updates["brevetes"])
    gather_revtecs.gather(db_cursor, monitor, all_updates["revtecs"])
    gather_sutrans.gather(db_cursor, monitor, all_updates["sutrans"])
    gather_satimps.gather(db_cursor, monitor, all_updates["satimpCodigos"])
    gather_recvehic.gather(db_cursor, monitor, all_updates["recvehic"])
    gather_sunarps.gather(db_cursor, monitor, all_updates["sunarps"])

    # manual gathering
    gather_soats.gather(db_conn, db_cursor, monitor, all_updates["soats"])
    gather_satmuls.gather(db_conn, db_cursor, monitor, all_updates["satmuls"])

    # in development
    # gather_sunats.gather(db_cursor, monitor, all_updates["sunats"])


def gather_threads(db_conn, db_cursor, monitor, all_updates):

    threads = []

    # auto gathering
    threads.append(
        Thread(
            target=gather_brevetes.gather,
            args=(db_cursor, monitor, all_updates["brevetes"]),
        )
    )
    threads.append(
        Thread(
            target=gather_revtecs.gather,
            args=(db_cursor, monitor, all_updates["revtecs"]),
        )
    )
    threads.append(
        Thread(
            target=gather_sutrans.gather,
            args=(db_cursor, monitor, all_updates["sutrans"]),
        )
    )
    threads.append(
        Thread(
            target=gather_satimps.gather,
            args=(db_cursor, monitor, all_updates["satimpCodigos"]),
        )
    )
    threads.append(
        Thread(
            target=gather_recvehic.gather,
            args=(db_cursor, monitor, all_updates["recvehic"]),
        )
    )
    # threads.append(
    #     Thread(
    #         target=gather_sunats.gather,
    #         args=(db_cursor, monitor, all_updates["sunats"]),
    #     )
    # )
    threads.append(
        Thread(
            target=gather_sunarps.gather,
            args=(db_cursor, monitor, all_updates["sunarps"]),
        )
    )

    # start all threads with a 2 second gap to avoid webdriver conflict
    for thread in threads:
        thread.start()
        time.sleep(2)

    # manual gathering (non-threaded)
    gather_satmuls.gather(db_conn, db_cursor, monitor, all_updates["satmuls"])
    gather_soats.gather(db_conn, db_cursor, monitor, all_updates["soats"])

    # wait for all active threads to finish in case manual gathering finishes before auto
    while any([i.is_alive() for i in threads]):
        print("waiting threads")
        time.sleep(10)
