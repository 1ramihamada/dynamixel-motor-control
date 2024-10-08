from dynamixel_sdk import *  # Uses Dynamixel SDK library
import tkinter as tk
import threading
import time

# Control table address
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132
ADDR_PRESENT_VELOCITY = 128
ADDR_OPERATING_MODE = 11
ADDR_PROFILE_VELOCITY = 112

# Protocol version
PROTOCOL_VERSION = 2.0

# Default setting
DXL_ID = 1
BAUDRATE = 57600
DEVICENAME = '/dev/ttyUSB0'

TORQUE_ENABLE = 1
TORQUE_DISABLE = 0
EXTENDED_POSITION_CONTROL_MODE = 4

class DynamixelController:
    def __init__(self):
        # Initialize PortHandler instance
        self.portHandler = PortHandler(DEVICENAME)
        self.packetHandler = PacketHandler(PROTOCOL_VERSION)

        # Open port
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            quit()

        # Set port baudrate
        if self.portHandler.setBaudRate(BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            quit()

        # Set operating mode to Extended Position Control Mode
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
            self.portHandler, DXL_ID, ADDR_OPERATING_MODE, EXTENDED_POSITION_CONTROL_MODE)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to set Extended Position Control Mode: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            quit()
        elif dxl_error != 0:
            print(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            quit()
        else:
            print("Operating mode set to Extended Position Control Mode")

        # Enable Dynamixel Torque
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
            self.portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to enable torque: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            quit()
        elif dxl_error != 0:
            print(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            quit()
        else:
            print("Dynamixel torque enabled")

        # Initialize variables
        self.velocity = 0
        self.direction = 1
        self.goal_position = 0
        self.running = True

        # Start the thread to update motor position
        self.update_thread = threading.Thread(target=self.update_motor_position)
        self.update_thread.start()

    def set_goal_position(self, goal_position):
        # Write goal position
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(
            self.portHandler, DXL_ID, ADDR_GOAL_POSITION, int(goal_position))
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to write goal position: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            print(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
        else:
            pass  # Successfully set goal position

    def get_present_position(self):
        # Read present position
        dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(
            self.portHandler, DXL_ID, ADDR_PRESENT_POSITION)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to read present position: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            return 0
        elif dxl_error != 0:
            print(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            return 0
        else:
            return dxl_present_position

    def get_present_velocity(self):
        # Read present velocity
        dxl_present_velocity, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(
            self.portHandler, DXL_ID, ADDR_PRESENT_VELOCITY)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to read present velocity: {self.packetHandler.getTxRxResult(dxl_comm_result)}")
            return 0
        elif dxl_error != 0:
            print(f"Dynamixel error: {self.packetHandler.getRxPacketError(dxl_error)}")
            return 0
        else:
            return dxl_present_velocity

    def update_motor_position(self):
        while self.running:
            # Calculate the goal position based on velocity and direction
            self.goal_position += self.velocity * self.direction
            self.set_goal_position(self.goal_position)
            time.sleep(0.1)  # Adjust the sleep time as needed

    def stop(self):
        self.running = False
        self.update_thread.join()
        self.set_goal_position(0)
        self.__del__()

    def __del__(self):
        if self.portHandler.is_open:
            self.packetHandler.write1ByteTxRx(self.portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
            self.portHandler.closePort()

class DynamixelGUI:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Dynamixel Controller")

        # Velocity Slider
        self.velocity_scale = tk.Scale(self.root, from_=0, to=500, orient=tk.HORIZONTAL, label="Velocity")
        self.velocity_scale.set(0)
        self.velocity_scale.pack()
        self.velocity_scale.bind("<B1-Motion>", self.update_velocity)
        self.velocity_scale.bind("<ButtonRelease-1>", self.update_velocity)

        # Direction Buttons
        self.direction_frame = tk.Frame(self.root)
        self.direction_frame.pack()

        self.forward_button = tk.Button(self.direction_frame, text="Forward", command=self.set_forward_direction)
        self.forward_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.reverse_button = tk.Button(self.direction_frame, text="Reverse", command=self.set_reverse_direction)
        self.reverse_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Position Label
        self.position_label = tk.Label(self.root, text="Position: 0")
        self.position_label.pack()

        # Velocity Label
        self.velocity_label = tk.Label(self.root, text="Velocity: 0")
        self.velocity_label.pack()

        # Stop Button
        self.stop_button = tk.Button(self.root, text="Stop Motor", command=self.stop_motor)
        self.stop_button.pack(pady=10)

        # Update Labels periodically
        self.update_labels()

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def set_forward_direction(self):
        self.controller.direction = 1

    def set_reverse_direction(self):
        self.controller.direction = -1

    def update_velocity(self, event):
        self.controller.velocity = int(self.velocity_scale.get())

    def update_labels(self):
        position = self.controller.get_present_position()
        velocity = self.controller.get_present_velocity()

        self.position_label.config(text=f"Position: {position}")
        self.velocity_label.config(text=f"Velocity: {velocity}")

        # Schedule the next update
        self.root.after(100, self.update_labels)

    def stop_motor(self):
        self.controller.velocity = 0
        self.velocity_scale.set(0)

    def on_closing(self):
        self.controller.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

def main():
    controller = DynamixelController()
    gui = DynamixelGUI(controller)
    gui.run()

if __name__ == '__main__':
    main()
