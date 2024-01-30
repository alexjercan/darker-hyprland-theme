#!/usr/bin/python

import os
import json
import argparse

CSS_TEMPLATE = """
* {
    border: none;
    border-radius: 0;
    font-family: Cartograph CF Nerd Font, Iosevka Term;
    font-weight: bold;
    font-size: 14px;
    min-height: 0;
}

window#waybar {
    background: rgba(0, 0, 0, 0);
    color: @foreground;
}

tooltip {
    background: @background;
    border-radius: 10px;
    border-width: 2px;
    border-style: solid;
    border-color: @background;
}
"""

JSON_TEMPLATE = {
    "layer": "top",
    "position": "top",
    "mod": "dock",
    "exclusive": True,
    "passthrough": False,
    "gtk-layer-shell": True,
    "height": 0,
    "margin-left": 4,
    "margin-right": 4,
    "spacing": 0,
    "modules-left": [],
    "modules-center": [],
    "modules-right": [],
}

HYPRLAND_WORKSPACES = "hyprland/workspaces"
HYPRLAND_WINDOW = "hyprland/window"
CLOCK_MODULE = "clock"
WEATHER_MODULE = "custom/weather"
UPDATES_MODULE = "custom/updates"
DAILY_MODULE = "custom/tasks"
CPUINFO_MODULE = "cpu"
MEMINFO_MODULE = "memory"
DISKINFO_MODULE = "disk"
NETWORK_MODULE = "network"
BLUETOOTH_MODULE = "bluetooth"
BATTERY_MODULE = "battery"
BACKLIGHT_MODULE = "backlight"
VOLUME_MODULE = "pulseaudio"
TRAY_MODULE = "tray"


def hyprland_workspaces_json():
    return {
        "format": "{name}",
        "disable-scroll": True,
        "all-outputs": True,
        "on-click": "activate",
        "on-scroll-up": "hyprctl dispatch workspace e+1",
        "on-scroll-down": "hyprctl dispatch workspace e-1",
    }


def hyprland_window_json():
    return {
        "format": "  {}",
        "max-length": 35
    }


def clock_json():
    return {
        "interval": 1,
        "format": "{:%b %d %Y - %H:%M}",
        "tooltip-format": "{: %A %d/%m/%Y %T}"
    }


def weather_json():
    return {
        "tooltip": True,
        "format": "{}",
        "interval": 3600,
        "exec": "wttrbar",
        "return-type": "json"
    }


def updates_json():
    return {
        "format": "🡻 {}",
        "interval": 7200,
        "exec": "i=$(checkupdates); echo \"$i\" |wc -l; echo \"$i\" |column -t |tr '\n' '\r'",
        "exec-if": "exit 0",
        "on-click": "kitty -e sudo pacman -Syu",
        "signal": 8
    }


def daily_json():
    return {
        "format": " {}",
        "interval": 60,
        "exec": "daily.sh",
        "tooltip": True,
        "tooltip-format": "{}",
        "return-type": "json"
    }


def cpu_json():
    return {
        "interval": 1,
        "format": " {usage}%",
        "on-click": "kitty --start-as=fullscreen --title htop sh -c 'htop'"
    }


def memory_json():
    return {
        "interval": 1,
        "format": " {}%",
        "tooltip": True,
        "tooltip-format": "Memory - {used:0.1f}GB used",
        "on-click": "kitty --start-as=fullscreen --title htop sh -c 'htop'"
    }


def disk_json():
    return {
        "interval": 1,
        "format": "󰋊 {percentage_used}%",
        "path": "/",
        "format-alt-click": "click-right",
        "format-alt": "󰋊 {percentage_used}%",
        "tooltip": True,
        "tooltip-format": "Disk - {used} used out of {total} on {path} ({percentage_used}%)",
        "on-click": "kitty --start-as=fullscreen --title htop sh -c 'htop'"
    }


def battery_json():
    return {
        "states": {
            "good": 95,
            "warning": 30,
            "critical": 20
        },
        "format": "{icon} {capacity}%",
        "format-charging": " {capacity}%",
        "format-plugged": " {capacity}%",
        "format-alt": "{time} {icon}",
        "format-icons": ["󰂎", "󰁺", "󰁻", "󰁼", "󰁽", "󰁾", "󰁿", "󰂀", "󰂁", "󰂂", "󰁹"]
    }


def network_json():
    return {
        "format-wifi": " {signalStrength}%",
        "format-ethernet": "",
        "tooltip-format": "{ifname} {ipaddr}/{cidr} via {gwaddr} ",
        "format-linked": "{ifname} ",
        "format-disconnected": "⚠",
        "format-alt": "{ifname}",
        "max-length": 50
    }


def bluetooth_json():
    return {
        "format": "",
        "format-disabled": "⊝",
        "format-connected": " {num_connections}",
        "tooltip-format": "{device_alias}",
        "tooltip-format-connected": " {device_enumerate}",
        "tooltip-format-enumerate-connected": "{device_alias}",
        "on-click": "blueman-manager"
    }


def backlight_json():
    return {
        "device": "intel_backlight",
        "format": "{icon} {percent}%",
        "format-icons": ["󰃞", "󰃟", "󰃠"],
        "on-scroll-up": "swayosd-client --brightness 10",
        "on-scroll-down": "swayosd-client --brightness -10",
        "min-length": 6
    }


def volume_json():
    return {
        "format": "{icon} {volume}%",
        "format-muted": " Muted",
        "on-click": "pavucontrol",
        "on-click-right": "swayosd-client --output-volume mute-toggle",
        "on-scroll-up": "swayosd-client --output-volume 5",
        "on-scroll-down": "swayosd-client --output-volume -5",
        "scroll-step": 5,
        "format-icons": {
            "headphone": "",
            "hands-free": "",
            "headset": "",
            "phone": "",
            "portable": "",
            "car": "",
            "default": ["", "", ""]
        },
        "tooltip": True,
        "tooltip-format": "{icon} at {volume}%"
    }


def tray_json():
    return {
        "icon-size": 13,
        "spacing": 10
    }


def hyprland_workspaces_css(island):
    return """
#workspaces {{
    background: @background;
    color: @foreground;
    padding: 3px 10px;
    margin: {};
    border-radius: {};
}}

#workspaces > * {{
    margin: 0px 5px;
}}

#workspaces button {{
    color: @foreground;
    background: @background;
    border-radius: 10px;
}}

#workspaces button.active {{
    background: @color0;
}}

#workspaces button.urgent {{
    color: @color1;
}}

#workspaces button:hover {{
    background: @color6;
    border-radius: 10px;
}}
""".format(
        get_margin_for(HYPRLAND_WORKSPACES, island),
        get_border_radius_for(HYPRLAND_WORKSPACES, island)
    )


def hyprland_window_css(island):
    return """
#window {{
    background: @background;
    color: @foreground;
    padding: 3px 10px;
    margin: {};
    border-radius: {};
}}
""".format(
        get_margin_for(HYPRLAND_WINDOW, island),
        get_border_radius_for(HYPRLAND_WINDOW, island)
    )


def clock_css(island):
    return """
#clock {{
    background: @background;
    color: @foreground;
    padding: 3px 10px;
    margin: {};
    border-radius: {};
}}
""".format(
        get_margin_for(CLOCK_MODULE, island),
        get_border_radius_for(CLOCK_MODULE, island)
    )


def weather_css(island):
    return """
#custom-weather {{
    background: @background;
    color: @foreground;
    padding: 3px 10px;
    margin: {};
    border-radius: {};
}}
""".format(
        get_margin_for(WEATHER_MODULE, island),
        get_border_radius_for(WEATHER_MODULE, island)
    )


def updates_css(island):
    return """
#custom-updates {{
    background: @background;
    color: @cursor;
    padding: 3px 10px;
    margin: {};
    border-radius: {};
}}
""".format(
        get_margin_for(UPDATES_MODULE, island),
        get_border_radius_for(UPDATES_MODULE, island)
    )


def daily_css(island):
    return """
#custom-tasks {{
    background: @background;
    color: @cursor;
    padding: 3px 10px;
    margin: {};
    border-radius: {};
}}
""".format(
        get_margin_for(DAILY_MODULE, island),
        get_border_radius_for(DAILY_MODULE, island)
    )


def cpu_css(island):
    return """
#cpu {{
    background: @background;
    color: @foreground;
    padding: 3px 10px;
    margin: {};
    border-radius: {};
}}
""".format(
        get_margin_for(CPUINFO_MODULE, island),
        get_border_radius_for(CPUINFO_MODULE, island)
    )


def memory_css(island):
    return """
#memory {{
    background: @background;
    color: @foreground;
    padding: 3px 10px;
    margin: {};
    border-radius: {};
}}
""".format(
        get_margin_for(MEMINFO_MODULE, island),
        get_border_radius_for(MEMINFO_MODULE, island)
    )


def disk_css(island):
    return """
#disk {{
    background: @background;
    color: @cursor;
    padding: 3px 10px;
    margin: {};
    border-radius: {};
}}
""".format(
        get_margin_for(DISKINFO_MODULE, island),
        get_border_radius_for(DISKINFO_MODULE, island)
    )


def battery_css(island):
    return """
#battery {{
    background: @background;
    color: @foreground;
    padding: 3px 10px;
    margin: {};
    border-radius: {};
}}
""".format(
        get_margin_for(BATTERY_MODULE, island),
        get_border_radius_for(BATTERY_MODULE, island)
    )


def network_css(island):
    return """
#network {{
    background: @background;
    color: @foreground;
    padding: 3px 10px;
    margin: {};
    border-radius: {};
}}
""".format(
        get_margin_for(NETWORK_MODULE, island),
        get_border_radius_for(NETWORK_MODULE, island)
    )


def bluetooth_css(island):
    return """
#bluetooth {{
    background: @background;
    color: @cursor;
    padding: 3px 10px;
    margin: {};
    border-radius: {};
}}
""".format(
        get_margin_for(BLUETOOTH_MODULE, island),
        get_border_radius_for(BLUETOOTH_MODULE, island)
    )


def backlight_css(island):
    return """
#backlight {{
    background: @background;
    color: @foreground;
    padding: 3px 10px;
    margin: {};
    border-radius: {};
}}
""".format(
        get_margin_for(BACKLIGHT_MODULE, island),
        get_border_radius_for(BACKLIGHT_MODULE, island)
    )


def volume_css(island):
    return """
#pulseaudio {{
    background: @background;
    color: @foreground;
    padding: 3px 10px;
    margin: {};
    border-radius: {};
}}
""".format(
        get_margin_for(VOLUME_MODULE, island),
        get_border_radius_for(VOLUME_MODULE, island)
    )


def tray_css(island):
    return """
#tray {{
    background: @background;
    color: @foreground;
    padding: 3px 10px;
    margin: 3px 0px 3px 0px;
    border-radius: {};
}}
""".format(get_border_radius_for("tray", island))


def get_border_radius_for(module, island):
    if len(island) == 1:
        return "10px"

    if module == island[0]:
        return "10px 0px 0px 10px"

    if module == island[-1]:
        return "0px 10px 10px 0px"

    return "0px"


def get_margin_for(module, island):
    if len(island) == 1:
        return "3px 10px 3px 0px"

    if module == island[-1]:
        return "3px 10px 3px 0px"

    return "3px 0px 3px 0px"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weather", action="store_true")
    parser.add_argument("--updates", action="store_true")
    parser.add_argument("--daily", action="store_true")
    parser.add_argument("--sysinfo", action="store_true")
    parser.add_argument("--network", action="store_true")
    parser.add_argument("--bluetooth", action="store_true")
    parser.add_argument("--battery", action="store_true")
    parser.add_argument("--volume", action="store_true")

    args = parser.parse_args()

    path_to_dir = os.path.dirname(os.path.realpath(__file__))

    workspaces_island = [HYPRLAND_WORKSPACES]
    window_island = [HYPRLAND_WINDOW]
    clock_island = [CLOCK_MODULE]

    weather_island = []
    if args.weather:
        weather_island.append(WEATHER_MODULE)

    status_island = []
    if args.updates:
        status_island.append(UPDATES_MODULE)
    if args.daily:
        status_island.append(DAILY_MODULE)
    if args.sysinfo:
        status_island.append(CPUINFO_MODULE)
        status_island.append(MEMINFO_MODULE)
        status_island.append(DISKINFO_MODULE)
    if args.network:
        status_island.append(NETWORK_MODULE)
    if args.bluetooth:
        status_island.append(BLUETOOTH_MODULE)
    if args.battery:
        status_island.append(BATTERY_MODULE)
        status_island.append(BACKLIGHT_MODULE)
    if args.volume:
        status_island.append(VOLUME_MODULE)

    tray_island = [TRAY_MODULE]

    with open(os.path.join(path_to_dir, "colors.conf"), "r") as colors_file:
        colors = colors_file.readlines()
        colors = [color.strip() for color in colors
                  if color.strip() != "" and not color.startswith("#")]
        colors = ["@define-color " + color for color in colors]

    json_template = JSON_TEMPLATE
    css_template = "\n".join(colors) + "\n\n" + CSS_TEMPLATE

    json_template["modules-left"].append(HYPRLAND_WORKSPACES)
    json_template[HYPRLAND_WORKSPACES] = hyprland_workspaces_json()
    css_template += hyprland_workspaces_css(workspaces_island)

    json_template["modules-left"].append(HYPRLAND_WINDOW)
    json_template[HYPRLAND_WINDOW] = hyprland_window_json()
    css_template += hyprland_window_css(window_island)

    json_template["modules-center"].append(CLOCK_MODULE)
    json_template[CLOCK_MODULE] = clock_json()
    css_template += clock_css(clock_island)

    if args.weather:
        json_template["modules-right"].append(WEATHER_MODULE)
        json_template[WEATHER_MODULE] = weather_json()
        css_template += weather_css(weather_island)

    if args.updates:
        json_template["modules-right"].append(UPDATES_MODULE)
        json_template[UPDATES_MODULE] = updates_json()
        css_template += updates_css(status_island)

    if args.daily:
        json_template["modules-right"].append(DAILY_MODULE)
        json_template[DAILY_MODULE] = daily_json()
        css_template += daily_css(status_island)

    if args.sysinfo:
        json_template["modules-right"].append(CPUINFO_MODULE)
        json_template[CPUINFO_MODULE] = cpu_json()
        css_template += cpu_css(status_island)

        json_template["modules-right"].append(MEMINFO_MODULE)
        json_template[MEMINFO_MODULE] = memory_json()
        css_template += memory_css(status_island)

        json_template["modules-right"].append(DISKINFO_MODULE)
        json_template[DISKINFO_MODULE] = disk_json()
        css_template += disk_css(status_island)

    if args.network:
        json_template["modules-right"].append(NETWORK_MODULE)
        json_template[NETWORK_MODULE] = network_json()
        css_template += network_css(status_island)

    if args.bluetooth:
        json_template["modules-right"].append(BLUETOOTH_MODULE)
        json_template[BLUETOOTH_MODULE] = bluetooth_json()
        css_template += bluetooth_css(status_island)

    if args.battery:
        json_template["modules-right"].append(BATTERY_MODULE)
        json_template[BATTERY_MODULE] = battery_json()
        css_template += battery_css(status_island)

        json_template["modules-right"].append(BACKLIGHT_MODULE)
        json_template[BACKLIGHT_MODULE] = backlight_json()
        css_template += backlight_css(status_island)

    if args.volume:
        json_template["modules-right"].append(VOLUME_MODULE)
        json_template[VOLUME_MODULE] = volume_json()
        css_template += volume_css(status_island)

    json_template["modules-right"].append(TRAY_MODULE)
    json_template[TRAY_MODULE] = tray_json()
    css_template += tray_css(tray_island)

    path_to_json = os.path.join(path_to_dir, "config.jsonc")
    path_to_css = os.path.join(path_to_dir, "style.css")

    with open(path_to_json, "w") as json_file:
        json.dump(json_template, json_file, indent=4)

    with open(path_to_css, "w") as css_file:
        css_file.write(css_template)


if __name__ == "__main__":
    main()
