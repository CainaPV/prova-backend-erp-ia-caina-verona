from rq import Worker

from fila import redis_sync

if __name__ == "__main__":
    Worker(["estoque"], connection=redis_sync()).work()
