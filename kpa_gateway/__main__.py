from kpa_gateway.api_gateway import API_Gateway

app = API_Gateway()

@app.position_telemetry(2)
def pos_tel_handler(data):
    print(f'pos tel: {data}')



@app.control_command(2, 3)
def cmd_handler(*args):
    print('cmd: ', args)
    app.send_ack(2)


if __name__ == "__main__":
    app.start()
    try:
        in_data = input('>')
    except KeyboardInterrupt:
        print('shutdown')