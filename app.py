import sys

from pyaxidraw import axidraw
import socketio


def plot(svg: str):
    # connect to plotter
    ad = axidraw.AxiDraw()

    # plot the svg
    ad.plot_setup(svg)
    ad.options.auto_rotate = False
    ad.options.speed_pendown = 50
    ad.options.speed_penup = 75
    ad.plot_run()

    # turn off the motors
    ad.plot_setup()
    ad.options.mode = "manual"
    ad.options.manual_cmd = "disable_xy"
    ad.plot_run()


sio = socketio.Client()

@sio.on("connect", namespace="/plotter")
def connect():
    print("Connected!")


@sio.on("connect_error", namespace="/plotter")
def connect_error(data):
    print("Connection failed!")


@sio.on("disconnect", namespace="/plotter")
def disconnect():
    print("Disconnected!")


@sio.on("plot", namespace="/plotter")
def on_plot(data):
    print("Received: ")
    print(data["svg"])
    plot(data["svg"])


def main():
    if len(sys.argv) < 2:
        sys.exit("Please state the URL you wish to connect to as a command line argument.\ne.g. python app.py https://example.com")
        
    server_url = sys.argv[1]
    print(f"Connecting to {server_url}")
    print("...")

    # connect to server
    sio.connect(server_url, namespaces=["/plotter"])

    # wait forever
    sio.wait()


if __name__ == "__main__":
    main()