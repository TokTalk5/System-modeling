import numpy as np
import heapq
import time
import itertools
import matplotlib.pyplot as plt

# Параметры модели
LAMBDA = 80
K = 2
PROCESSING_TIME = 0.136
QUEUE_SIZE = 5
MAX_SIM_TIME = 50
MAX_REQUESTS = 500

# Статистика
processed_requests = 0
rejected_requests = 0
waiting_times = []
total_busy_time = 0.0


queue = []
current_request = None


current_time = 0.0


counter = itertools.count()

# Для построения графика
time_points = []
buffer_sizes = []

# Генерация времени между заявками
def erlang_time(lambda_, k):
    return np.sum(np.random.exponential(1 / lambda_, k))

# Генерация новой заявки
def generate_request():
    priority = np.random.randint(1, 9)  # Приоритет от 1 до 8
    return {
        "priority": priority,
        "arrival_time": current_time,
    }

# Обработка очереди
def enqueue_request(request):
    global queue, rejected_requests
    count = next(counter)
    if len(queue) < QUEUE_SIZE:
        heapq.heappush(queue, (-request["priority"], count, request))
    else:
        lowest_priority, _, _ = queue[0]
        if -lowest_priority < request["priority"]:
            heapq.heappop(queue)
            heapq.heappush(queue, (-request["priority"], count, request))
        else:
            rejected_requests += 1

# Моделирование системы
start_time = time.time()
while current_time < MAX_SIM_TIME and processed_requests + rejected_requests < MAX_REQUESTS:
    interarrival_time = erlang_time(LAMBDA, K)
    current_time += interarrival_time

    request = generate_request()
    if current_request is None:
        current_request = request
        end_processing_time = current_time + PROCESSING_TIME
        total_busy_time += PROCESSING_TIME
    else:
        enqueue_request(request)
    time_points.append(current_time)
    buffer_sizes.append(len(queue))
    while current_request and current_time >= end_processing_time:
        processed_requests += 1
        waiting_times.append(current_time - current_request["arrival_time"])
        if queue:
            _, _, current_request = heapq.heappop(queue)
            end_processing_time = current_time + PROCESSING_TIME
            total_busy_time += PROCESSING_TIME
        else:
            current_request = None


average_waiting_time = np.mean(waiting_times) if waiting_times else 0.0
efficiency = total_busy_time / current_time if current_time > 0 else 0


print("Результаты моделирования:")
print(f"Обработано заявок: {processed_requests}")
print(f"Отброшено заявок: {rejected_requests}")
print(f"Среднее время ожидания: {average_waiting_time:.4f} сек")
print(f"Суммарное время занятости процессора: {total_busy_time:.4f} сек")
print(f"Эффективность системы: {efficiency:.2%}")

# Построение графика
plt.figure(figsize=(10, 6))
plt.plot(time_points, buffer_sizes, label="Количество заявок в очереди")
plt.xlabel("Время (с)")
plt.ylabel("Размер очереди")
plt.title("Изменение количества заявок в буфере с течением времени")
plt.legend()
plt.grid()
plt.show()