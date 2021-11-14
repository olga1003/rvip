from multiprocessing import Process, Pipe


def send_requests(pipe1, id, time, condition):
    if condition == 0:
        condition = 1
    time += 1
    print('Процесс Р' + str(id) + ' запрашивает вход в КС')
    pipe1.send((id, time))

    return time, condition


def send_reply(pipe, id):
    reply = 1
    print('Процесс Р' + str(id) + ' разрешает вход в КС')
    pipe.send((id, reply))


def receive_request(pipe, id, time, condition, DR, waiting_pipe):
    id_rec, timestamp = pipe.recv()
    print('Процесс Р' + str(id) + ' получил запрос от P' + str(id_rec), end='\n')

    if condition == 0:
        send_reply(pipe, id)
    elif condition == 1 and timestamp > time:
        send_reply(pipe, id)
    elif condition == 2:
        print('Процесс Р' + str(id) + ' откладывает отправку ответа P' + str(id_rec))
        DR[id_rec - 1] = 1
        waiting_pipe[id_rec - 1] = pipe

    time = maxTime(timestamp, time)

    return time, DR, waiting_pipe


def receive_reply(pipe, id):
    id_rec ,reply = pipe.recv()
    print('Процесс Р' + str(id) + ' получил разрешение от Р' + str(id_rec), end='\n')
    return reply


def maxTime(receive_time, time):
    return max(receive_time, time) + 1


def process1(pipe12, pipe21):
    id = 1
    time = 0
    condition1 = 0
    DR1 = [0, 0]
    permission = 0

    waiting_pipe1 = [0, 0]
    time, DR1, waiting_pipe1 = receive_request(pipe12, id, time, condition1, DR1, waiting_pipe1)
    time, condition1 = send_requests(pipe12, id, time, condition1)
    permission += receive_reply(pipe12, id)
    condition1, permission = check_entry(id, permission, condition1)
    condition1 = exitingKS(id, condition1, DR1, waiting_pipe1)


def process2(pipe12, pipe21):
    id = 2
    condition2 = 0
    time = 0
    DR2 = [0, 0]
    waiting_pipe2 = [0, 0]
    permission = 0

    time, condition2 = send_requests(pipe21, id, time, condition2)
    permission += receive_reply(pipe21, id)
    condition2, permission = check_entry(id, permission, condition2)
    time, DR2, waiting_pipe2 = receive_request(pipe21, id, time, condition2, DR2, waiting_pipe2)

    condition2 = exitingKS(id, condition2, DR2, waiting_pipe2)


def check_entry(id, permission, condition):
    if permission == 1:
        condition = 2
        print('Процесс Р' + str(id) + ' вошёл в КС')
        permission = 0
    return condition, permission


def exitingKS(id, condition, DR, waiting_pipe):
    if condition == 2:
        condition = 0
        print('Процесс Р' + str(id) + ' вышел из КС')
        for i in range(2):
            if DR[i - 1] == 1:
                send_reply(waiting_pipe[i - 1], id)
                DR[i - 1] = 0

    return condition


if __name__ == '__main__':

    print("Алгоритм Рикарта-Агравалы ")
    print()
    one_two, two_one = Pipe()

    proc1 = Process(target=process1, args=(one_two, two_one))
    proc2 = Process(target=process2, args=(one_two, two_one))

    proc2.start()
    proc1.start()

    proc1.join()
    proc2.join()