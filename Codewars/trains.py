from random import randint


def randomize_data():
    response = []
    for _ in range(randint(2, 25)):
        name = chr(randint(65, 90)) + chr(randint(65, 90)) + str(randint(10, 99))
        wait_time = randint(1, 100) / 10
        accel_rate = randint(1, 10) / 10
        accel_time = randint(3, 60) / 10
        decel_rate = randint(4, 28) / 10
        response.append(
            {
                "name": name,
                "wait_time": wait_time,
                "accel": accel_rate,
                "accel_time": accel_time,
                "decel": decel_rate,
            }
        )
    return response, randint(1000, 5000)


def trains(train_data, track_length):
    train_times = []
    for train in train_data:
        # wait period (step 1)
        wait_time = float(train["wait_time"])
        # acceleration period to cruising speed (step 2)
        time_accel = float(train["accel_time"])
        distance_accel = (0.5) * train["accel"] * (time_accel ** 2)
        cruising_speed = train["accel"] * time_accel
        # deceleration period from cruising speed to 0 (step 4)
        time_decel = cruising_speed / train["decel"]
        distance_decel = cruising_speed * time_decel - (0.5) * train["decel"] * (
            time_decel ** 2
        )
        # cruising period (step 3)
        crusing_distance = track_length - distance_accel - distance_decel
        time_cruising = crusing_distance / cruising_speed
        # total time
        total_time = wait_time + time_accel + time_cruising + time_decel
        train_times.append((train["name"], total_time))
    return [i[0] for i in sorted(train_times, key=lambda i: i[1], reverse=False)]


"""
train_data = [
    {"name": "A", "wait_time": 35, "accel": 2.5, "accel_time": 18, "decel": 8},
    {"name": "D", "wait_time": 42, "accel": 4.5, "accel_time": 22, "decel": 7},
    {"name": "E", "wait_time": 88, "accel": 6, "accel_time": 45, "decel": 3},
    {"name": "S", "wait_time": 12, "accel": 1, "accel_time": 30, "decel": 9},
]
track_length = 600
"""

train_data = [
    {
        "name": "AE86",
        "wait_time": 0.8,
        "accel": 5.4,
        "accel_time": 3.2,
        "decel": 2,
    },
    {
        "name": "BT98",
        "wait_time": 6.5,
        "accel": 3.8,
        "accel_time": 2.8,
        "decel": 2.2,
    },
    {
        "name": "CW34",
        "wait_time": 2.6,
        "accel": 6.1,
        "accel_time": 4.1,
        "decel": 1.4,
    },
    {
        "name": "DJ77",
        "wait_time": 1.9,
        "accel": 5.2,
        "accel_time": 2.2,
        "decel": 1.2,
    },
    {
        "name": "EY12",
        "wait_time": 3.3,
        "accel": 4.6,
        "accel_time": 5.0,
        "decel": 0.8,
    },
]
track_length = 1250


train_data, track_length = randomize_data()
g = trains(train_data, track_length)
print(g)
