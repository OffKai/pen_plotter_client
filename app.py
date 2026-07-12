import socketio

from config import parse_settings


def plot(svg: str):
    from pyaxidraw import axidraw

    ad = axidraw.AxiDraw()

    ad.plot_setup(svg)
    ad.options.auto_rotate = False
    ad.options.speed_pendown = 50
    ad.options.speed_penup = 75
    ad.plot_run()

    ad.plot_setup()
    ad.options.mode = "manual"
    ad.options.manual_cmd = "disable_xy"
    ad.plot_run()


sio = socketio.Client()
settings = None


@sio.on("connect", namespace="/plotter")
def connect():
    print(f"Connected as {settings.plotter_id}.")


@sio.on("connect_error", namespace="/plotter")
def connect_error(data):
    print(f"Connection failed: {data}")


@sio.on("disconnect", namespace="/plotter")
def disconnect():
    print("Disconnected!")


@sio.on("plot", namespace="/plotter")
def on_plot(data):
    svg = data["svg"]
    print(f"Received plot ({len(svg)} bytes).")

    if settings.dry_run:
        print(svg)
    else:
        plot(svg)


def main(argv=None):
    global settings
    settings = parse_settings(argv)

    print(
        f"Connecting to {settings.server_url} as {settings.plotter_id} "
        f"(dry_run={settings.dry_run})"
    )
    sio.connect(
        settings.server_url,
        namespaces=["/plotter"],
        auth={"id": settings.plotter_id},
    )

    sio.wait()


if __name__ == "__main__":
    main()