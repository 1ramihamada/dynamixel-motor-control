# Dynamixel Motor Control in Extended Position Mode

This project controls a Dynamixel motor using Python and the Dynamixel SDK. The motor operates in extended position mode, allowing continuous rotation beyond 360 degrees. A `tkinter` GUI provides user control over velocity, direction, and real-time monitoring.

## Features
- Continuous rotation with extended position control mode.
- GUI control for velocity and direction using `tkinter`.
- Real-time position and velocity updates displayed in the GUI.
- Multithreaded motor position updates for smooth operation.

## Dependencies
- `Dynamixel SDK`
- `tkinter`

## Usage
1. Connect the Dynamixel motor to your system (e.g., `/dev/ttyUSB0`).
2. Run the code to open the GUI and control the motor interactively.
3. Use the slider to set the velocity and buttons to adjust the direction.

## Setup
1. Install dependencies using pip:
   ```bash
   pip install dynamixel-sdk
