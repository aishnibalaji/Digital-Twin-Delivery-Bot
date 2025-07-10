from controller import Robot
import math

# Initialize Robot
TIME_STEP = 32
robot = Robot()

# Motors
left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# Sensors
lidar = robot.getDevice("LDS-01")
lidar.enable(TIME_STEP)

gps = robot.getDevice("gps")
gps.enable(TIME_STEP)

compass = robot.getDevice("compass")
compass.enable(TIME_STEP)

# Robot state variables
robot_state = "SEEKING_PICKUP"  # States: SEEKING_PICKUP, HAS_PACKAGE, DELIVERED
max_speed = 3.0
obstacle_threshold = 0.5

# Zone definitions (adjust based on your warehouse layout)
PICKUP_ZONE = {"x_range": (0.5, 1.5), "z_range": (0.5, 1.5)}
DROPOFF_ZONE = {"x_range": (-1.5, -0.5), "z_range": (-1.5, -0.5)}

def normalize_bearing(bearing):
    """Normalize bearing to [0, 2*pi]"""
    while bearing < 0:
        bearing += 2 * math.pi
    while bearing > 2 * math.pi:
        bearing -= 2 * math.pi
    return bearing

def get_bearing():
    """Get robot's current bearing from compass"""
    north = compass.getValues()
    bearing = math.atan2(north[0], north[2])
    return normalize_bearing(bearing)

def get_position():
    """Get robot's current position from GPS"""
    return gps.getValues()

def in_zone(position, zone):
    """Check if robot is in specified zone"""
    x, y, z = position
    return (zone["x_range"][0] <= x <= zone["x_range"][1] and 
            zone["z_range"][0] <= z <= zone["z_range"][1])

def calculate_angle_to_target(current_pos, target_pos):
    """Calculate angle to target position"""
    dx = target_pos[0] - current_pos[0]
    dz = target_pos[2] - current_pos[2]
    return math.atan2(dx, dz)

def obstacle_avoidance(ranges):
    """Simple obstacle avoidance using LIDAR data"""
    # Check different sectors of LIDAR
    left_side = min(ranges[0:60])
    front_left = min(ranges[60:90])
    front_center = min(ranges[90:120])
    front_right = min(ranges[120:150])
    right_side = min(ranges[150:210])
    
    left_vel = max_speed
    right_vel = max_speed
    
    # Obstacle detected in front
    if front_center < obstacle_threshold:
        if left_side > right_side:
            # Turn left
            left_vel = -max_speed * 0.5
            right_vel = max_speed
        else:
            # Turn right
            left_vel = max_speed
            right_vel = -max_speed * 0.5
    elif front_left < obstacle_threshold:
        # Turn right
        left_vel = max_speed
        right_vel = max_speed * 0.3
    elif front_right < obstacle_threshold:
        # Turn left
        left_vel = max_speed * 0.3
        right_vel = max_speed
    
    return left_vel, right_vel

def navigate_to_target(current_pos, target_pos, current_bearing):
    """Navigate towards target position"""
    target_angle = calculate_angle_to_target(current_pos, target_pos)
    angle_diff = target_angle - current_bearing
    
    # Normalize angle difference
    while angle_diff > math.pi:
        angle_diff -= 2 * math.pi
    while angle_diff < -math.pi:
        angle_diff += 2 * math.pi
    
    # Simple proportional control for steering
    turn_speed = angle_diff * 2.0
    
    # Limit turn speed
    turn_speed = max(-max_speed, min(max_speed, turn_speed))
    
    left_vel = max_speed - turn_speed
    right_vel = max_speed + turn_speed
    
    return left_vel, right_vel

# Main control loop
print("🤖 Digital Twin Delivery Bot Starting...")
print("📦 Initial State: SEEKING_PICKUP")

while robot.step(TIME_STEP) != -1:
    # Get sensor data
    ranges = lidar.getRangeImage()
    position = get_position()
    bearing = get_bearing()
    
    # State machine for delivery task
    if robot_state == "SEEKING_PICKUP":
        target_pos = [1.0, 0, 1.0]  # Center of pickup zone
        
        if in_zone(position, PICKUP_ZONE):
            robot_state = "HAS_PACKAGE"
            print("✅ Package picked up! Heading to drop-off zone...")
        else:
            # Navigate to pickup zone
            left_vel, right_vel = navigate_to_target(position, target_pos, bearing)
    
    elif robot_state == "HAS_PACKAGE":
        target_pos = [-1.0, 0, -1.0]  # Center of drop-off zone
        
        if in_zone(position, DROPOFF_ZONE):
            robot_state = "DELIVERED"
            print("🎉 Package delivered successfully!")
        else:
            # Navigate to drop-off zone
            left_vel, right_vel = navigate_to_target(position, target_pos, bearing)
    
    elif robot_state == "DELIVERED":
        # Task complete - stop or return to base
        left_vel = 0
        right_vel = 0
        print("🏁 Delivery mission complete!")
    
    # Override navigation with obstacle avoidance if needed
    front_distance = min(ranges[70:110])  # Front center sensors
    if front_distance < obstacle_threshold:
        left_vel, right_vel = obstacle_avoidance(ranges)
        print("⚠️ Obstacle detected! Avoiding...")
    
    # Apply motor velocities
    left_motor.setVelocity(left_vel)
    right_motor.setVelocity(right_vel)
    
    # Debug output (every 100 steps to avoid spam)
    if robot.getTime() % 3.2 < 0.1:  # Approximately every 3.2 seconds
        x, y, z = position
        print(f"🤖 State: {robot_state} | Position: ({x:.2f}, {z:.2f}) | Bearing: {math.degrees(bearing):.1f}°")