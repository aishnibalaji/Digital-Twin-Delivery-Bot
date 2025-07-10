from controller import Robot
import math

# Initialize Robot
TIME_STEP = 32
robot = Robot()

print("🤖 Digital Twin Delivery Bot Starting...")
print("📦 Initial State: SEEKING_PICKUP")

# Motors
left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# LIDAR - This should work on TurtleBot3
lidar = robot.getDevice("LDS-01")
if lidar is not None:
    lidar.enable(TIME_STEP)
    print("✅ LIDAR sensor found and enabled")
else:
    print("❌ LIDAR sensor not found")

# Try to get GPS (optional)
gps = robot.getDevice("gps")
if gps is not None:
    gps.enable(TIME_STEP)
    print("✅ GPS sensor found and enabled")
else:
    print("ℹ️ GPS sensor not found - using time-based navigation")

# Try to get Compass (optional)
compass = robot.getDevice("compass")
if compass is not None:
    compass.enable(TIME_STEP)
    print("✅ Compass sensor found and enabled")
else:
    print("ℹ️ Compass sensor not found")

# Robot state variables
robot_state = "SEEKING_PICKUP"
max_speed = 2.0
obstacle_threshold = 0.5
mission_timer = 0
pickup_timer = 0
dropoff_timer = 0

def get_position_estimate():
    """Get position from GPS if available, otherwise use timer estimate"""
    if gps is not None:
        try:
            return gps.getValues()
        except:
            pass
    
    # Fallback: estimate position based on time and state
    # This is a simple approximation
    time_seconds = mission_timer * TIME_STEP / 1000.0
    
    if robot_state == "SEEKING_PICKUP":
        # Assume robot moves toward pickup zone over time
        progress = min(time_seconds / 30.0, 1.0)  # 30 seconds to reach
        x = progress * 1.0
        z = progress * 1.0
    elif robot_state == "HAS_PACKAGE":
        # Assume robot moves from pickup to dropoff
        progress = min(dropoff_timer * TIME_STEP / 1000.0 / 35.0, 1.0)  # 35 seconds
        x = 1.0 - progress * 2.0  # Move from (1,1) to (-1,-1)
        z = 1.0 - progress * 2.0
    else:
        x, z = -1.0, -1.0  # At dropoff
    
    return [x, 0, z]

def in_pickup_zone():
    """Check if we should be in pickup zone (time-based or GPS-based)"""
    if gps is not None:
        try:
            pos = gps.getValues()
            x, y, z = pos
            return (0.5 <= x <= 1.5) and (0.5 <= z <= 1.5)
        except:
            pass
    
    # Time-based fallback: assume we reach pickup after moving for a while
    return pickup_timer > 25 * (1000 // TIME_STEP)  # ~25 seconds

def in_dropoff_zone():
    """Check if we should be in dropoff zone"""
    if gps is not None:
        try:
            pos = gps.getValues()
            x, y, z = pos
            return (-1.5 <= x <= -0.5) and (-1.5 <= z <= -0.5)
        except:
            pass
    
    # Time-based fallback
    return dropoff_timer > 30 * (1000 // TIME_STEP)  # ~30 seconds

# Main control loop
print("🚀 Starting main control loop...")

while robot.step(TIME_STEP) != -1:
    mission_timer += 1
    
    # Get sensor data
    obstacle_detected = False
    
    if lidar is not None:
        try:
            ranges = lidar.getRangeImage()
            front_distance = min(ranges[70:110])  # Front center sensors
            obstacle_detected = front_distance < obstacle_threshold
        except:
            # If LIDAR fails, assume no obstacles for now
            obstacle_detected = False
    
    # State machine for delivery task
    if robot_state == "SEEKING_PICKUP":
        pickup_timer += 1
        
        if in_pickup_zone():
            robot_state = "HAS_PACKAGE"
            dropoff_timer = 0
            print("✅ Package picked up! Heading to drop-off zone...")
        
        # Navigate toward pickup zone (right and forward)
        if obstacle_detected:
            # Turn left when obstacle detected
            left_motor.setVelocity(-max_speed * 0.5)
            right_motor.setVelocity(max_speed)
            if mission_timer % 50 == 0:
                print("⚠️ Obstacle detected! Turning left...")
        else:
            # Move forward-right toward pickup zone
            left_motor.setVelocity(max_speed)
            right_motor.setVelocity(max_speed * 0.8)  # Slight right turn
    
    elif robot_state == "HAS_PACKAGE":
        dropoff_timer += 1
        
        if in_dropoff_zone():
            robot_state = "DELIVERED"
            print("🎉 Package delivered successfully!")
        
        # Navigate toward dropoff zone (left and backward)
        if obstacle_detected:
            # Turn right when obstacle detected
            left_motor.setVelocity(max_speed)
            right_motor.setVelocity(-max_speed * 0.5)
            if mission_timer % 50 == 0:
                print("⚠️ Obstacle detected! Turning right...")
        else:
            # Move toward dropoff zone
            left_motor.setVelocity(max_speed * 0.8)  # Slight left turn
            right_motor.setVelocity(max_speed)
    
    elif robot_state == "DELIVERED":
        # Mission complete - stop
        left_motor.setVelocity(0)
        right_motor.setVelocity(0)
        if mission_timer % 100 == 0:
            print("🏁 Mission complete! Robot stopped.")
    
    # Debug output every 3 seconds
    if mission_timer % (3000 // TIME_STEP) == 0:
        pos = get_position_estimate()
        x, y, z = pos
        time_sec = mission_timer * TIME_STEP / 1000.0
        print(f"🤖 Time: {time_sec:.1f}s | State: {robot_state} | Est. Position: ({x:.2f}, {z:.2f})")
        
        if obstacle_detected:
            print("   ⚠️ Obstacle in front!")
        
        # Show pickup/dropoff progress
        if robot_state == "SEEKING_PICKUP":
            pickup_progress = min(pickup_timer / (25 * 1000 // TIME_STEP) * 100, 100)
            print(f"   📦 Pickup progress: {pickup_progress:.1f}%")
        elif robot_state == "HAS_PACKAGE":
            dropoff_progress = min(dropoff_timer / (30 * 1000 // TIME_STEP) * 100, 100)
            print(f"   🚚 Delivery progress: {dropoff_progress:.1f}%")