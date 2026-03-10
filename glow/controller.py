"""MQTT controller daemon for Home Assistant integration.

Connects to an MQTT broker (e.g. Mosquitto on Home Assistant) and publishes
MQTT Discovery payloads so HA auto-discovers a "Glow LED Matrix" device with:
  - A select entity to pick visualizations
  - A switch entity for power on/off
  - Dynamic parameter entities per visualization (text inputs, number sliders, etc.)
"""

import argparse
import json
import logging
import os
import signal
import threading
import time
from typing import Any

import paho.mqtt.client as mqtt

from glow.display import create_display
from glow.visualizations import REGISTRY

log = logging.getLogger(__name__)

DEVICE_ID = "glow_led_matrix"
DEVICE_INFO = {
    "identifiers": [DEVICE_ID],
    "name": "Glow LED Matrix",
    "manufacturer": "DIY",
    "model": "RGB LED Matrix",
}

TOPIC_VIZ_SET = "glow/visualization/set"
TOPIC_VIZ_STATE = "glow/visualization/state"
TOPIC_POWER_SET = "glow/power/set"
TOPIC_POWER_STATE = "glow/power/state"
TOPIC_AVAILABILITY = "glow/availability"

# How long a visualization runs before the controller restarts it (effectively infinite)
VIZ_DURATION = 86400.0


class GlowController:
    def __init__(
        self,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self._broker_host = broker_host
        self._broker_port = broker_port

        self._power_on = False
        self._current_viz: str | None = None
        self._param_values: dict[str, Any] = {}
        self._prev_viz_params: set[str] = set()

        self._viz_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

        self._client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=DEVICE_ID,
        )
        if username:
            self._client.username_pw_set(username, password)
        self._client.will_set(TOPIC_AVAILABILITY, "offline", retain=True)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

    # ------------------------------------------------------------------
    # MQTT callbacks
    # ------------------------------------------------------------------

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: Any,
        reason_code: mqtt.ReasonCode,
        properties: Any = None,
    ) -> None:
        if reason_code != 0:
            log.error("MQTT connection failed: %s", reason_code)
            return
        log.info("Connected to MQTT broker")

        client.subscribe(TOPIC_VIZ_SET)
        client.subscribe(TOPIC_POWER_SET)
        client.subscribe("glow/param/+/set")

        self._publish_discovery()
        self._publish_state()
        client.publish(TOPIC_AVAILABILITY, "online", retain=True)

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: Any,
        msg: mqtt.MQTTMessage,
    ) -> None:
        payload = msg.payload.decode("utf-8")
        topic = msg.topic
        log.debug("Message on %s: %s", topic, payload)

        if topic == TOPIC_POWER_SET:
            self._handle_power(payload)
        elif topic == TOPIC_VIZ_SET:
            self._handle_visualization(payload)
        elif topic.startswith("glow/param/") and topic.endswith("/set"):
            param_name = topic.split("/")[2]
            self._handle_param(param_name, payload)

    # ------------------------------------------------------------------
    # Command handlers
    # ------------------------------------------------------------------

    def _handle_power(self, payload: str) -> None:
        if payload == "ON":
            self._power_on = True
            if self._current_viz:
                self._start_visualization(self._current_viz)
        elif payload == "OFF":
            self._power_on = False
            self._stop_current()
            # Clear the display
            try:
                display = create_display()
                display.show(
                    __import__("PIL.Image", fromlist=["Image"]).new(
                        "RGB", (display.width, display.height), (0, 0, 0)
                    )
                )
            except Exception:
                log.exception("Failed to clear display")
        self._publish_state()

    def _handle_visualization(self, payload: str) -> None:
        if payload not in REGISTRY:
            log.warning("Unknown visualization: %s", payload)
            return
        self._current_viz = payload
        # Initialize default param values for this viz
        viz_params = REGISTRY[payload]["params"]
        self._param_values = {k: v["default"] for k, v in viz_params.items()}
        self._publish_param_entities(payload)
        if self._power_on:
            self._start_visualization(payload)
        self._publish_state()

    def _handle_param(self, param_name: str, payload: str) -> None:
        if not self._current_viz:
            return
        viz_params = REGISTRY[self._current_viz]["params"]
        if param_name not in viz_params:
            log.warning("Unknown param %s for %s", param_name, self._current_viz)
            return

        # Coerce value to the right type
        param_def = viz_params[param_name]
        if param_def["type"] == "number":
            value: Any = int(float(payload))
        else:
            value = payload

        self._param_values[param_name] = value
        self._client.publish(f"glow/param/{param_name}/state", str(value), retain=True)

        # Restart the visualization with updated params
        if self._power_on and self._current_viz:
            self._start_visualization(self._current_viz)

    # ------------------------------------------------------------------
    # Visualization lifecycle
    # ------------------------------------------------------------------

    def _stop_current(self) -> None:
        self._stop_event.set()
        if self._viz_thread and self._viz_thread.is_alive():
            self._viz_thread.join(timeout=5.0)
            if self._viz_thread.is_alive():
                log.warning("Visualization thread did not stop in time")
        self._viz_thread = None

    def _start_visualization(self, name: str) -> None:
        self._stop_current()
        self._stop_event = threading.Event()

        entry = REGISTRY[name]
        fn = entry["fn"]
        kwargs: dict[str, Any] = {
            "duration": VIZ_DURATION,
            "stop_event": self._stop_event,
        }
        kwargs.update(self._param_values)

        self._viz_thread = threading.Thread(
            target=self._run_viz, args=(fn, kwargs), daemon=True
        )
        self._viz_thread.start()
        log.info("Started visualization: %s (params=%s)", name, self._param_values)

    @staticmethod
    def _run_viz(fn: Any, kwargs: dict[str, Any]) -> None:
        try:
            fn(**kwargs)
        except Exception:
            log.exception("Visualization crashed")

    # ------------------------------------------------------------------
    # MQTT Discovery
    # ------------------------------------------------------------------

    def _publish_discovery(self) -> None:
        viz_names = list(REGISTRY.keys())

        # Select entity — visualization picker
        select_config = {
            "name": "Visualization",
            "unique_id": f"{DEVICE_ID}_visualization",
            "command_topic": TOPIC_VIZ_SET,
            "state_topic": TOPIC_VIZ_STATE,
            "options": viz_names,
            "availability_topic": TOPIC_AVAILABILITY,
            "device": DEVICE_INFO,
        }
        self._client.publish(
            f"homeassistant/select/{DEVICE_ID}/visualization/config",
            json.dumps(select_config),
            retain=True,
        )

        # Switch entity — power on/off
        switch_config = {
            "name": "Power",
            "unique_id": f"{DEVICE_ID}_power",
            "command_topic": TOPIC_POWER_SET,
            "state_topic": TOPIC_POWER_STATE,
            "availability_topic": TOPIC_AVAILABILITY,
            "device": DEVICE_INFO,
        }
        self._client.publish(
            f"homeassistant/switch/{DEVICE_ID}/power/config",
            json.dumps(switch_config),
            retain=True,
        )

    def _publish_param_entities(self, viz_name: str) -> None:
        # Remove previous viz's param entities
        for old_param in self._prev_viz_params:
            for entity_type in ("text", "number", "select"):
                self._client.publish(
                    f"homeassistant/{entity_type}/{DEVICE_ID}/param_{old_param}/config",
                    "",
                    retain=True,
                )
        self._prev_viz_params.clear()

        # Publish new viz's param entities
        viz_params = REGISTRY[viz_name]["params"]
        for param_name, param_def in viz_params.items():
            self._prev_viz_params.add(param_name)
            entity_type = param_def["type"]

            config: dict[str, Any] = {
                "name": param_def["name"],
                "unique_id": f"{DEVICE_ID}_param_{param_name}",
                "command_topic": f"glow/param/{param_name}/set",
                "state_topic": f"glow/param/{param_name}/state",
                "availability_topic": TOPIC_AVAILABILITY,
                "device": DEVICE_INFO,
            }

            if entity_type == "number":
                config["min"] = param_def.get("min", 0)
                config["max"] = param_def.get("max", 100)
                config["step"] = param_def.get("step", 1)
            elif entity_type == "select":
                config["options"] = param_def["options"]

            self._client.publish(
                f"homeassistant/{entity_type}/{DEVICE_ID}/param_{param_name}/config",
                json.dumps(config),
                retain=True,
            )

            # Publish current value
            value = self._param_values.get(param_name, param_def["default"])
            self._client.publish(
                f"glow/param/{param_name}/state", str(value), retain=True
            )

    def _publish_state(self) -> None:
        self._client.publish(
            TOPIC_POWER_STATE, "ON" if self._power_on else "OFF", retain=True
        )
        if self._current_viz:
            self._client.publish(TOPIC_VIZ_STATE, self._current_viz, retain=True)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        shutdown = threading.Event()

        def _signal_handler(sig: int, frame: Any) -> None:
            log.info("Received signal %s, shutting down...", sig)
            shutdown.set()

        signal.signal(signal.SIGINT, _signal_handler)
        signal.signal(signal.SIGTERM, _signal_handler)

        log.info("Connecting to %s:%s", self._broker_host, self._broker_port)
        self._client.connect(self._broker_host, self._broker_port)
        self._client.loop_start()

        shutdown.wait()

        log.info("Cleaning up...")
        self._stop_current()
        self._client.publish(TOPIC_AVAILABILITY, "offline", retain=True)
        time.sleep(0.5)
        self._client.loop_stop()
        self._client.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Glow MQTT controller daemon")
    parser.add_argument(
        "--broker",
        default=os.environ.get("MQTT_BROKER", "localhost"),
        help="MQTT broker hostname (env: MQTT_BROKER)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("MQTT_PORT", "1883")),
        help="MQTT broker port (env: MQTT_PORT)",
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("MQTT_USERNAME"),
        help="MQTT username (env: MQTT_USERNAME)",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("MQTT_PASSWORD"),
        help="MQTT password (env: MQTT_PASSWORD)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    controller = GlowController(
        broker_host=args.broker,
        broker_port=args.port,
        username=args.username,
        password=args.password,
    )
    controller.run()


if __name__ == "__main__":
    main()
