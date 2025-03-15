import serial
import sys
import time
import subprocess
import os

def install_dependencies():
    print("Checking and installing dependencies...")
    try:
        import pip
    except ImportError:
        print("Installing pip...")
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--default-pip"])
    
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyserial"])
    print("Dependencies installed successfully!")

class MotorController:
    def __init__(self):
        # Detect OS and set appropriate port
        if sys.platform.startswith('win'):
            self.port = 'COM3'
        else:
            self.port = '/dev/ttyACM0'
        
        self.baudrate = 9600
        self.serial = None

    def connect(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Connected to {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Error connecting to {self.port}: {e}")
            return False

    def send_command(self, command):
        if self.serial and self.serial.is_open:
            self.serial.write(f"{command}\n".encode())
            response = self.serial.readline().decode().strip()
            return response
        return "Not connected"

    def rotate_motor(self, hat_id, motor_id, steps, direction):
        command = f"ROTATE,{hat_id},{motor_id},{steps},{direction}"
        return self.send_command(command)

    def close(self):
        if self.serial:
            self.serial.close()

def main():
    # Install dependencies first
    install_dependencies()
    
    controller = MotorController()
    
    if not controller.connect():
        return

    print("\nStepper Motor Control")
    print("-------------------")
    print("Commands:")
    print("rotate <hat_id> <motor_id> <steps> <direction>")
    print("  hat_id: 1 or 2")
    print("  motor_id: 1 or 2")
    print("  steps: number of steps")
    print("  direction: cw (clockwise) or ccw (counter-clockwise)")
    print("quit - Exit program")

    try:
        while True:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'quit':
                break
                
            parts = command.split()
            if len(parts) == 0:
                continue

            if parts[0] == 'rotate' and len(parts) == 5:
                hat_id = int(parts[1])
                motor_id = int(parts[2])
                steps = int(parts[3])
                direction = parts[4]

                if hat_id not in [1, 2] or motor_id not in [1, 2]:
                    print("Invalid hat_id or motor_id. Must be 1 or 2.")
                    continue

                if direction not in ['cw', 'ccw']:
                    print("Invalid direction. Must be 'cw' or 'ccw'.")
                    continue

                response = controller.rotate_motor(hat_id, motor_id, steps, direction)
                print(f"Response: {response}")
            else:
                print("Invalid command. Use 'rotate <hat_id> <motor_id> <steps> <direction>' or 'quit'")

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        controller.close()

if __name__ == "__main__":
    main()