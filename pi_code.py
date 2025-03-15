# This code runs on the Raspberry Pi Zero
import serial
import time
import subprocess
import sys

def install_dependencies():
    print("Checking and installing Raspberry Pi dependencies...")
    try:
        subprocess.check_call(["sudo", "pip3", "install", "adafruit-circuitpython-motorkit"])
        print("Dependencies installed successfully!")
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

# Install dependencies first
install_dependencies()

# Now import the required modules
from adafruit_motorkit import MotorKit
import board
import busio

# Create I2C bus objects for GPIO 2 (SDA) and 3 (SCL)
i2c = busio.I2C(board.D3, board.D2)  # SCL = GPIO3, SDA = GPIO2

# Initialize the two motor HATs with different I2C addresses
hat1 = MotorKit(i2c=i2c, address=0x60)  # Default address
hat2 = MotorKit(i2c=i2c, address=0x61)  # Second HAT must have address jumper set

# Configure serial
ser = serial.Serial('/dev/serial0', 9600)

def get_motor(hat_id, motor_id):
    hat = hat1 if hat_id == 1 else hat2
    return hat.stepper1 if motor_id == 1 else hat.stepper2

def rotate_motor(hat_id, motor_id, steps, direction):
    motor = get_motor(hat_id, motor_id)
    step_direction = 1 if direction == 'cw' else -1
    
    for _ in range(steps):
        motor.onestep(direction=step_direction)
        time.sleep(0.01)  # Small delay between steps
    
    motor.release()  # Release motor to prevent overheating
    return "OK"

while True:
    if ser.in_waiting:
        command = ser.readline().decode().strip()
        parts = command.split(',')
        
        try:
            if parts[0] == 'ROTATE':
                hat_id = int(parts[1])
                motor_id = int(parts[2])
                steps = int(parts[3])
                direction = parts[4]
                
                result = rotate_motor(hat_id, motor_id, steps, direction)
                ser.write(f"{result}\n".encode())
            else:
                ser.write(b"Invalid command\n")
        except Exception as e:
            ser.write(f"Error: {str(e)}\n".encode())