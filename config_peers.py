starting_port = 5000
num_miners = 50

peers = [f'http://127.0.0.1:{port}/' for port in range(starting_port, starting_port + num_miners)]
