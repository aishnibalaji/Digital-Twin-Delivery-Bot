# Digital-Twin-Delivery-Bot
Simulate a small warehouse delivery robot that navigates from point A to B, avoids obstacles, and picks up/drops off a package all in a digital twin

---

##  Project Overview


**Key Features:**
- Obstacle avoidance using LIDAR
- Autonomous point-to-point navigation
- Simulated pickup/drop-off logic
- Extendable to real-world twin sync with MQTT/Streamlit dashboard

---

## Tech Stack

| Component       | Tool/Library         |
|-----------------|----------------------|
| Simulation      | [Webots](https://cyberbotics.com/) |
| Programming     | Python 3             |
| Control Logic   | Webots API           |
| Sensors         | LIDAR (LDS-01)       |
| Visualization   | Webots 3D Viewer     |
| Optional UI     | Streamlit (for dashboard) |

---



### 1. Install Webots

Download and install Webots for macOS:  
 [https://cyberbotics.com/#download](https://cyberbotics.com/#download)

### 2. Clone this repository

```bash
git clone https://github.com/your-username/DigitalTwin-DeliveryBot.git
cd DigitalTwin-DeliveryBot
