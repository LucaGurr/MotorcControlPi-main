# Stepper Motor Control System

This project allows you to control stepper motors connected to a Raspberry Pi Zero using a computer via USB serial connection.

## System Requirements

- Computer running Windows or Linux
- Raspberry Pi Zero
- 2x Adafruit Motor HATs
- 4x Stepper Motors
- USB cable for connecting Pi to computer

## Hardware Setup

1. Connect the Adafruit Motor HATs to the Raspberry Pi using GPIO 2 (SDA) and GPIO 3 (SCL):
   - Both HATs share the same I2C bus
   - First HAT: Default I2C address (0x60)
   - Second HAT: Address jumper set to 0x61
2. Connect stepper motors to the HATs
3. Connect Raspberry Pi to computer via USB

## Installation

1. Copy `pi_code.py` to your Raspberry Pi Zero
2. Set the address jumper on the second Motor HAT to 0x61
3. Run the following command on your Raspberry Pi to install required dependencies:
   ```bash
   sudo pip3 install adafruit-circuitpython-motorkit
   ```
4. Run the motor control program on your computer:
   ```bash
   python motor_control.py
   ```

## Usage

Available commands:
- `rotate <hat_id> <motor_id> <steps> <direction>`
  - hat_id: 1 or 2
  - motor_id: 1 or 2
  - steps: number of steps
  - direction: cw (clockwise) or ccw (counter-clockwise)
- `quit` - Exit program

Example:
```bash
rotate 1 1 100 cw  # Rotate motor 1 on hat 1 clockwise 100 steps
```

## Important Notes

- The second Motor HAT must have its address jumper set to 0x61 to avoid I2C address conflicts
- Both HATs share the same I2C bus on GPIO 2 (SDA) and GPIO 3 (SCL)