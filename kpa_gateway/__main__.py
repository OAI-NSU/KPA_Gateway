from kpa_gateway.api_gateway import API_Gateway


app = API_Gateway()


@app.position_telemetry(telemetry_type=2)
def pos_tel_handler(data):
    print(f'pos tel: {data}')


@app.control_command(cmd_type=2, cmd_code=3)
def cmd_handler(*args):
    print('cmd: ', args)
    return True


def worker1_func(data1, data2):
    print(f'worker 1: {data1, data2}')


def worker2_func(data1, data2):
    print(f'worker 2: {data1, data2}')


if __name__ == "__main__":
    app.add_worker(worker1_func, name='worker1', period_sec=3, args=[1, 2])
    app.add_worker(worker2_func, name='worker2', period_sec=1, args=[1, 2])
    app.start()
    try:
        while True:
            in_data: str = input('>')
            if in_data == 'stop app':
                app.stop()
    except KeyboardInterrupt:
        print('shutdown')