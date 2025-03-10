import io
import sys
from PyQt5.QtWidgets import QApplication
from PIL import Image
from PyQt5.QtCore import QDataStream, pyqtSlot
from PyQt5.QtNetwork import QLocalServer

from model_server.run_model import apply_model_to_image, load_model

model_path = R"F:\runs\pix2sat_patch_size_34\latest_net_G.pth"

models = {
    0: R"F:\runs\pix2pix_base\latest_net_G.pth",
    1: R"F:\runs\pix2sat_resnet\latest_net_G.pth",
    2: R"F:\runs\pix2sat_patch_size_34\latest_net_G.pth",
    3: R"F:\runs\pix2sat_total_variation_0.0001\latest_net_G.pth",
}


class Server(QLocalServer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.newConnection.connect(self.handleConnection)

    @pyqtSlot()
    def handleConnection(self):
        print("Connected")
        # Accept the incoming connection
        socket = self.nextPendingConnection()

        # Wait for the complete data to be available
        while socket.bytesAvailable() < 4:
            socket.waitForReadyRead()

        # Read the size of the data to receive
        stream = QDataStream(socket)
        stream.setVersion(QDataStream.Qt_5_0)
        model_type = stream.readUInt32()
        dataSize = stream.readUInt32()
        print(f"Read data size: {dataSize}")

        # Wait for the complete data to be available
        while socket.bytesAvailable() < dataSize:
            socket.waitForReadyRead()

        # Read the complete data
        data = stream.readRawData(dataSize)

        # create an in-memory stream of the bytes data
        image_stream = io.BytesIO(data)

        # open the image stream using PIL
        input_image = Image.open(image_stream)
        print("Loading model...")
        model = load_model(models[model_type], model_type= 'resnet' if model_type == 1 else 'unet')
        print("Applying model...")
        output_image = apply_model_to_image(model, input_image)
        print("Model applied")

        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format="PNG")
        send_data = output_buffer.getvalue()

        print(f"Sending image of size {len(send_data)}")

        stream.writeUInt32(len(send_data))
        socket.flush()
        socket.waitForBytesWritten()

        socket.write(send_data)
        socket.flush()
        socket.waitForBytesWritten()

        # Clean up
        print("Disconnecting")
        socket.disconnectFromServer()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create the server and start listening for connections
    server = Server()
    server.listen('model_server')

    sys.exit(app.exec_())
