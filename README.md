# Stepper Motor Control System

This project implements a dual-HAT stepper motor control system using a Raspberry Pi Zero as the motor controller and a computer as the command interface. The system allows precise control of up to 4 stepper motors through a simple command-line interface.

## System Architecture

The system consists of two main components:

1. **Computer-side Controller** (`motor_control.py`):
   - Handles user input
   - Manages serial communication with the Raspberry Pi
   - Provides command validation and error handling
   - Auto-installs required dependencies

2. **Raspberry Pi Controller** (`pi_code.py`):
   - Controls the motor HATs via I2C
   - Executes motor movement commands
   - Manages motor timing and coordination
   - Auto-installs required dependencies

## System Requirements

### Hardware
- Computer (Windows/Linux)
- Raspberry Pi Zero
- 2× Adafruit DC & Stepper Motor HAT
- 4× Stepper Motors (compatible with the HAT)
- USB cable (for Pi-to-Computer connection)
- Power supply for motors (12V recommended)

### Software
- Python 3.6 or higher on both computer and Raspberry Pi
- Required Python packages (auto-installed):
  - Computer: `pyserial`
  - Raspberry Pi: `adafruit-circuitpython-motorkit`

## Detailed Hardware Setup

### 1. I2C Configuration

Both Motor HATs share the same I2C bus using GPIO pins:
```
GPIO 2 (SDA) → I2C Data
GPIO 3 (SCL) → I2C Clock
```

The I2C bus configuration is implemented in `pi_code.py`:

```python
# Create I2C bus objects for GPIO 2 (SDA) and 3 (SCL)
i2c = busio.I2C(board.D3, board.D2)  # SCL = GPIO3, SDA = GPIO2
```

This approach was chosen because:
- Reduces pin usage by sharing the I2C bus
- Simplifies wiring with just two connections
- Provides reliable communication with multiple devices
- Allows for future expansion with additional I2C devices

### 2. Motor HAT Address Configuration

The HATs are configured with different I2C addresses to allow communication on the same bus:

```python
# Initialize the two motor HATs with different I2C addresses
hat1 = MotorKit(i2c=i2c, address=0x60)  # Default address
hat2 = MotorKit(i2c=i2c, address=0x61)  # Second HAT must have address jumper set
```

#### First HAT
- Uses default I2C address (0x60)
- No jumper configuration needed

#### Second HAT
- Must be set to address 0x61
- Address Jumper Configuration:
  1. Locate the address jumpers (A0, A1, A2)
  2. Configure for address 0x61:
     ```
     A0: Bridged (Connected)
     A1: Open   (Not connected)
     A2: Open   (Not connected)
     ```

### 3. Motor Connections

Connect the four-lead stepper motors to the HATs. Each motor requires four connections (two per coil):

```
HAT 1:
- Motor 1: 
  - Coil 1: M1 terminals (A+ and A-)
  - Coil 2: M2 terminals (B+ and B-)
- Motor 2:
  - Coil 1: M3 terminals (A+ and A-)
  - Coil 2: M4 terminals (B+ and B-)

HAT 2:
- Motor 1:
  - Coil 1: M1 terminals (A+ and A-)
  - Coil 2: M2 terminals (B+ and B-)
- Motor 2:
  - Coil 1: M3 terminals (A+ and A-)
  - Coil 2: M4 terminals (B+ and B-)
```

#### Wiring Diagram

The Adafruit Motor HAT has 5 terminals per motor, but we only need 4 for our bipolar stepper motors. Here's how to connect them:

```
Motor (4 wires)    HAT (5 terminals)
---------------    ----------------
Red (Coil 1A)  →   M1A
Blue (Coil 1B) →   M1B
Green (Coil 2A) →  M2A
Black (Coil 2B) →  M2B
                   GND (not used)

Connection diagram for each motor:

┌──────────────────────────────────┐
│           Motor HAT              │
│                                  │
│  M1A   M1B   GND   M2A   M2B    │
│   │     │     ╳     │     │     │
│   │     │           │     │     │
│   ▼     ▼           ▼     ▼     │
│  Red   Blue       Green Black    │
│   [Coil 1]        [Coil 2]      │
│        4-wire Stepper Motor      │
└──────────────────────────────────┘

Note: ╳ = Not Connected
```

Wire Color Guide:
- Colors shown are typical but may vary by manufacturer
- What matters is keeping coil pairs together:
  - Coil 1: Connect to M1A and M1B
  - Coil 2: Connect to M2A and M2B
- The GND (middle) terminal is not used for 4-wire steppers

Wiring Tips:
- Each coil pair should be connected to adjacent terminals
- If motor rotation is reversed, swap the connections for either coil
- Color codes may vary by manufacturer, consult your motor's datasheet
- Test connections with low current first to verify proper wiring
- You can identify coil pairs using a multimeter:
  1. Set multimeter to resistance (Ω) mode
  2. Pairs of wires from the same coil will show ~2-5Ω resistance
  3. Wires from different coils will show no connectivity

## Software Installation and Setup

### 1. Raspberry Pi Setup

1. Install Raspberry Pi OS (Lite is sufficient)
2. Enable I2C:
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → I2C → Enable
   ```

3. Copy `pi_code.py` to the Raspberry Pi:
   ```bash
   scp pi_code.py pi@raspberrypi.local:~/
   ```

4. Run the code (dependencies will auto-install):
   ```bash
   python3 pi_code.py
   ```

### 2. Computer Setup

1. Clone this repository
2. Run the control program (dependencies will auto-install):
   ```bash
   python motor_control.py
   ```

## Code Architecture and Implementation Details

### 1. Dependency Management

Both scripts implement automatic dependency installation to ensure a smooth setup:

```python
# From motor_control.py
def install_dependencies():
    print("Checking and installing dependencies...")
    try:
        import pip
    except ImportError:
        print("Installing pip...")
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--default-pip"])
    
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyserial"])
```

This approach was chosen because:
- Eliminates manual dependency installation
- Ensures consistent environment setup
- Reduces setup errors
- Makes the system more user-friendly

### 2. Serial Communication

The system uses a simple yet robust serial communication protocol:

```python
# From motor_control.py
def send_command(self, command):
    if self.serial and self.serial.is_open:
        self.serial.write(f"{command}\n".encode())
        response = self.serial.readline().decode().strip()
        return response
    return "Not connected"
```

Key design decisions:
- Uses newline-terminated commands for reliable parsing
- Implements command encoding/decoding for data integrity
- Includes connection state validation
- Returns meaningful responses

### 3. Motor Control Protocol

The system uses a comma-separated command protocol:

```python
# Command format: ROTATE,<hat_id>,<motor_id>,<steps>,<direction>
def rotate_motor(hat_id, motor_id, steps, direction):
    motor = get_motor(hat_id, motor_id)
    step_direction = 1 if direction == 'cw' else -1
    
    for _ in range(steps):
        motor.onestep(direction=step_direction)
        time.sleep(0.01)  # Small delay between steps
    
    motor.release()  # Release motor to prevent overheating
```

Design rationale:
- Simple parsing with clear parameter separation
- Easy error detection
- Human-readable format
- Extensible for future commands

### 4. Error Handling

Comprehensive error handling ensures system reliability:

```python
# From motor_control.py
try:
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
```

Implementation benefits:
- Validates all input parameters
- Provides clear error messages
- Prevents invalid operations
- Maintains system stability

### 5. Motor Management

The motor control implementation includes safety features:

```python
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
```

Key features:
- Automatic motor release prevents overheating
- Configurable step timing for speed control
- Clean motor selection logic
- Safe direction control

## Usage Guide

### Basic Commands

1. Rotate a motor:
   ```bash
   rotate <hat_id> <motor_id> <steps> <direction>
   ```
   Example:
   ```bash
   rotate 1 1 100 cw  # Rotate motor 1 on hat 1 clockwise 100 steps
   ```

2. Exit the program:
   ```bash
   quit
   ```

### Parameter Details

- `hat_id`: Motor HAT identifier
  - `1`: First HAT (address 0x60)
  - `2`: Second HAT (address 0x61)

- `motor_id`: Motor identifier on the specified HAT
  - `1`: First motor (M1/M2 terminals)
  - `2`: Second motor (M3/M4 terminals)

- `steps`: Number of steps to rotate
  - Positive integer
  - Each step is typically 1.8° (200 steps/revolution)

- `direction`: Rotation direction
  - `cw`: Clockwise
  - `ccw`: Counter-clockwise

## Troubleshooting

### Common Issues

1. **Communication Errors**
   - Check USB connection
   - Verify correct serial port (`COM3` on Windows, `/dev/ttyACM0` on Linux)
   - Ensure Raspberry Pi is powered on

2. **Motor Issues**
   - Verify power supply connection
   - Check motor wiring
   - Confirm HAT address jumper settings

3. **I2C Issues**
   - Verify I2C is enabled on Raspberry Pi
   - Check GPIO connections
   - Confirm HAT addresses are correct

### Debugging

Use the following commands on the Raspberry Pi to verify I2C setup:
```bash
# List I2C devices
i2cdetect -y 1

# Expected output should show devices at 0x60 and 0x61
```

## Safety Considerations

1. **Power Management**
   - Use appropriate power supply for motors
   - Don't modify wiring while powered
   - Allow motors to cool between operations

2. **Code Safety**
   - Motor release after operation prevents overheating
   - Command validation prevents invalid operations
   - Error handling prevents system crashes

## Maintenance

1. **Regular Checks**
   - Verify jumper connections
   - Check motor connections
   - Test I2C communication

2. **Software Updates**
   - Keep Python packages updated
   - Check for library compatibility
   - Backup configuration files

## Future Improvements

Potential enhancements:
1. GUI interface
2. Speed control
3. Multiple motor coordination
4. Position tracking
5. Automated sequences