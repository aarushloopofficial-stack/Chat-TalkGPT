"""
Chat&Talk GPT - IoT Control Manager
Control smart home devices (lights, switches, thermostats, etc.)
Supports multiple protocols: HTTP, MQTT, WebSocket
"""
import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger("IoTManager")

# Try to import required libraries
MQTT_AVAILABLE = False
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
    logger.info("MQTT is available")
except ImportError:
    logger.warning("MQTT not available")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class IoTManager:
    """
    IoT Manager for smart home device control
    
    Features:
    - Support for multiple device types (lights, switches, thermostats, cameras)
    - Multiple protocols (HTTP REST, MQTT, direct control)
    - Device discovery
    - Automation routines
    - Scene management
    - Scheduling
    """
    
    # Device types
    DEVICE_TYPES = [
        "light", "switch", "thermostat", "camera", "lock",
        "sensor", "speaker", "tv", "fan", "blind", "outlet"
    ]
    
    # Device states
    DEVICE_STATES = ["on", "off", "unknown"]
    
    def __init__(self):
        """Initialize IoT Manager"""
        self.devices = {}
        self.scenes = {}
        self.routines = {}
        self.mqtt_client = None
        self.mqtt_connected = False
        
        # Default configuration
        self.config = {
            "mqtt_broker": os.getenv("MQTT_BROKER", "localhost"),
            "mqtt_port": int(os.getenv("MQTT_PORT", "1883")),
            "mqtt_username": os.getenv("MQTT_USERNAME"),
            "mqtt_password": os.getenv("MQTT_PASSWORD"),
            "home_assistant_url": os.getenv("HOME_ASSISTANT_URL"),
            "home_assistant_token": os.getenv("HOME_ASSISTANT_TOKEN")
        }
        
        logger.info("IoT Manager initialized")
    
    def configure(self, **kwargs):
        """Configure IoT settings"""
        self.config.update(kwargs)
        
        # Initialize MQTT if configured
        if self.config.get("mqtt_broker"):
            self._init_mqtt()
    
    def _init_mqtt(self):
        """Initialize MQTT client"""
        if not MQTT_AVAILABLE:
            logger.warning("MQTT not available")
            return
        
        try:
            self.mqtt_client = mqtt.Client()
            
            if self.config.get("mqtt_username"):
                self.mqtt_client.username_pw_set(
                    self.config["mqtt_username"],
                    self.config.get("mqtt_password")
                )
            
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_message = self._on_mqtt_message
            
            self.mqtt_client.connect(
                self.config["mqtt_broker"],
                self.config["mqtt_port"],
                60
            )
            self.mqtt_client.loop_start()
            
            logger.info(f"MQTT connecting to {self.config['mqtt_broker']}")
            
        except Exception as e:
            logger.error(f"MQTT initialization error: {e}")
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.mqtt_connected = True
            logger.info("MQTT connected")
            
            # Subscribe to device topics
            if self.devices:
                for device_id in self.devices:
                    topic = f"home/{device_id}/state"
                    client.subscribe(topic)
        else:
            logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            device_id = msg.topic.split('/')[1]
            state = msg.payload.decode()
            
            if device_id in self.devices:
                self.devices[device_id]["state"] = state
                logger.info(f"Device {device_id} state updated: {state}")
                
        except Exception as e:
            logger.error(f"MQTT message error: {e}")
    
    def add_device(
        self,
        device_id: str,
        device_name: str,
        device_type: str,
        protocol: str = "http",
        endpoint: Optional[str] = None,
        mqtt_topic: Optional[str] = None,
        capabilities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add a new IoT device
        
        Args:
            device_id: Unique device identifier
            device_name: Display name
            device_type: Type of device
            protocol: Communication protocol (http, mqtt, direct)
            endpoint: HTTP endpoint URL
            mqtt_topic: MQTT topic for device
            capabilities: List of device capabilities
            
        Returns:
            Add status
        """
        try:
            if device_type not in self.DEVICE_TYPES:
                return {
                    "success": False,
                    "error": f"Invalid device type. Choose from: {', '.join(self.DEVICE_TYPES)}"
                }
            
            device = {
                "id": device_id,
                "name": device_name,
                "type": device_type,
                "protocol": protocol,
                "endpoint": endpoint,
                "mqtt_topic": mqtt_topic,
                "state": "unknown",
                "capabilities": capabilities or self._get_default_capabilities(device_type),
                "last_updated": datetime.now().isoformat()
            }
            
            self.devices[device_id] = device
            
            # Subscribe to MQTT topic if applicable
            if protocol == "mqtt" and mqtt_topic and self.mqtt_client:
                self.mqtt_client.subscribe(mqtt_topic)
            
            logger.info(f"Device added: {device_id}")
            
            return {
                "success": True,
                "device": device,
                "message": f"Device {device_name} added successfully"
            }
            
        except Exception as e:
            logger.error(f"Add device error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_default_capabilities(self, device_type: str) -> List[str]:
        """Get default capabilities for device type"""
        capabilities_map = {
            "light": ["on", "off", "brightness", "color"],
            "switch": ["on", "off"],
            "thermostat": ["temperature", "mode", "fan"],
            "camera": ["stream", "record", "snapshot"],
            "lock": ["lock", "unlock", "status"],
            "sensor": ["read"],
            "speaker": ["play", "pause", "volume"],
            "tv": ["power", "volume", "channel", "input"],
            "fan": ["on", "off", "speed"],
            "blind": ["open", "close", "position"],
            "outlet": ["on", "off", "power"]
        }
        return capabilities_map.get(device_type, ["on", "off"])
    
    def remove_device(self, device_id: str) -> Dict[str, Any]:
        """Remove a device"""
        if device_id in self.devices:
            del self.devices[device_id]
            return {
                "success": True,
                "message": f"Device {device_id} removed"
            }
        return {
            "success": False,
            "error": "Device not found"
        }
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device information"""
        return self.devices.get(device_id)
    
    def list_devices(
        self,
        device_type: Optional[str] = None,
        state: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all devices with optional filters
        
        Args:
            device_type: Filter by device type
            state: Filter by state
            
        Returns:
            List of devices
        """
        devices = list(self.devices.values())
        
        if device_type:
            devices = [d for d in devices if d["type"] == device_type]
        if state:
            devices = [d for d in devices if d["state"] == state]
        
        return devices
    
    def control_device(
        self,
        device_id: str,
        command: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Control a device
        
        Args:
            device_id: Device identifier
            command: Command to send
            parameters: Additional parameters
            
        Returns:
            Control result
        """
        try:
            if device_id not in self.devices:
                return {
                    "success": False,
                    "error": "Device not found"
                }
            
            device = self.devices[device_id]
            protocol = device["protocol"]
            
            if protocol == "http":
                result = self._control_http(device, command, parameters)
            elif protocol == "mqtt":
                result = self._control_mqtt(device, command, parameters)
            elif protocol == "homeassistant":
                result = self._control_homeassistant(device, command, parameters)
            else:
                result = self._control_direct(device, command, parameters)
            
            # Update device state
            if result.get("success"):
                device["state"] = result.get("state", device["state"])
                device["last_updated"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Control device error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _control_http(
        self,
        device: Dict[str, Any],
        command: str,
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Control device via HTTP"""
        if not device.get("endpoint"):
            return {
                "success": False,
                "error": "No endpoint configured"
            }
        
        try:
            url = f"{device['endpoint']}/{command}"
            data = parameters or {}
            
            response = requests.post(url, json=data, timeout=5)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "state": "on" if command == "on" else "off",
                    "response": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _control_mqtt(
        self,
        device: Dict[str, Any],
        command: str,
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Control device via MQTT"""
        if not device.get("mqtt_topic"):
            return {
                "success": False,
                "error": "No MQTT topic configured"
            }
        
        if not self.mqtt_connected:
            return {
                "success": False,
                "error": "MQTT not connected"
            }
        
        try:
            topic = f"home/{device['id']}/command"
            payload = json.dumps({
                "command": command,
                "parameters": parameters or {}
            })
            
            self.mqtt_client.publish(topic, payload)
            
            return {
                "success": True,
                "state": command,
                "message": f"Command sent to {device['name']}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _control_homeassistant(
        self,
        device: Dict[str, Any],
        command: str,
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Control device via Home Assistant"""
        url = self.config.get("home_assistant_url")
        token = self.config.get("home_assistant_token")
        
        if not url or not token:
            return {
                "success": False,
                "error": "Home Assistant not configured"
            }
        
        try:
            entity_id = device.get("entity_id", device["id"])
            service = f"homeassistant.{command}"
            
            response = requests.post(
                f"{url}/api/services/{service}",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "entity_id": entity_id,
                    **(parameters or {})
                },
                timeout=5
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "state": command,
                    "message": "Command sent via Home Assistant"
                }
            else:
                return {
                    "success": False,
                    "error": f"Home Assistant error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _control_direct(
        self,
        device: Dict[str, Any],
        command: str,
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Direct device control (simulated)"""
        return {
            "success": True,
            "state": command,
            "message": f"Command '{command}' sent to {device['name']}"
        }
    
    # Scene Management
    def create_scene(
        self,
        scene_id: str,
        scene_name: str,
        device_states: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a scene (preset device states)
        
        Args:
            scene_id: Unique scene ID
            scene_name: Display name
            device_states: Dict of device commands
            
        Returns:
            Scene creation status
        """
        scene = {
            "id": scene_id,
            "name": scene_name,
            "devices": device_states,
            "created_at": datetime.now().isoformat()
        }
        
        self.scenes[scene_id] = scene
        
        return {
            "success": True,
            "scene": scene,
            "message": f"Scene '{scene_name}' created"
        }
    
    def activate_scene(self, scene_id: str) -> Dict[str, Any]:
        """Activate a scene"""
        if scene_id not in self.scenes:
            return {
                "success": False,
                "error": "Scene not found"
            }
        
        scene = self.scenes[scene_id]
        results = []
        
        for device_id, commands in scene["devices"].items():
            command = commands.get("command", "on")
            parameters = commands.get("parameters")
            
            result = self.control_device(device_id, command, parameters)
            results.append({
                "device_id": device_id,
                "success": result.get("success", False)
            })
        
        return {
            "success": True,
            "message": f"Scene '{scene['name']}' activated",
            "results": results
        }
    
    # Automation Routines
    def create_routine(
        self,
        routine_id: str,
        routine_name: str,
        trigger: Dict[str, Any],
        actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create an automation routine
        
        Args:
            routine_id: Unique routine ID
            routine_name: Display name
            trigger: Trigger configuration
            actions: List of actions to perform
            
        Returns:
            Routine creation status
        """
        routine = {
            "id": routine_id,
            "name": routine_name,
            "trigger": trigger,
            "actions": actions,
            "enabled": True,
            "last_triggered": None
        }
        
        self.routines[routine_id] = routine
        
        return {
            "success": True,
            "routine": routine,
            "message": f"Routine '{routine_name}' created"
        }
    
    def execute_routine(self, routine_id: str) -> Dict[str, Any]:
        """Execute a routine manually"""
        if routine_id not in self.routines:
            return {
                "success": False,
                "error": "Routine not found"
            }
        
        routine = self.routines[routine_id]
        results = []
        
        for action in routine["actions"]:
            device_id = action.get("device_id")
            command = action.get("command")
            parameters = action.get("parameters")
            
            if device_id and command:
                result = self.control_device(device_id, command, parameters)
                results.append(result)
        
        routine["last_triggered"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": f"Routine '{routine['name']}' executed",
            "results": results
        }
    
    def get_all_scenes(self) -> List[Dict[str, Any]]:
        """Get all scenes"""
        return list(self.scenes.values())
    
    def get_all_routines(self) -> List[Dict[str, Any]]:
        """Get all routines"""
        return list(self.routines.values())


# Singleton instance
iot_manager = IoTManager()


# Standalone functions
def add_device(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function to add device"""
    return iot_manager.add_device(*args, **kwargs)


def control_device(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function to control device"""
    return iot_manager.control_device(*args, **kwargs)


def activate_scene(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function to activate scene"""
    return iot_manager.activate_scene(*args, **kwargs)
