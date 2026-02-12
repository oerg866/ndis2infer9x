# NDIS2INFER9X

(C) 2024-2026 Eric Voirin (oerg866@googlemail.com)

This is a small script that allows you to associate one or more PCI hardware IDs with any existing DOS NDIS 2 driver and generates a Windows 9x-style INF file for it. 

This allows the Windows 9x hardware installation wizard / hardware detection to find this driver for the associated hardware and install it automatically, without having to manually load the legacy driver.

## Requirements

* A Python interpreter (duh)
* A NDIS2 driver containing an NDIS2 `OEMSETUP.INF` file

## Usage

`python3 ndis2infer9x.py --inf [OEMSETUP_INF] --out [OUTPUT_INF_FILE_NAME] --id xxxx:yyyy:"name" --id wwww:zzzz:"name2" ...`

Where

* `--inf` points to the input OEMSETUP.INF file
* `--out` is the filename for the generated INF file
* `--id` is a PCI ID in the format of `xxxx:yyyy:"name"` where xxxx is the PCI Vendor ID and yyyy is the PCI Device ID in hexadecimal format.
    * The `:"name"` part is optional and can be used to override the default device name pullled from `OEMSETUP.INF`
    * This parameter can be repeated multiple times for as many different IDs you wish to associate with this driver.

### Example

`python3 ndis2infer9x.py --nif ATL1C.NIF --out NETATL1C.INF --id 1969:1063:"Atheros L1 PCIe Ethernet"`

### Intel-Style OEMSETUP files

Intel network drivers provide a `[PCI]` section with `VENDOR_ID` and a `DEVICE_ID` list.

The INF parser will parse it if present and add these IDs to the INF file automatically.

## Why NDIS2?

There is a quite strange situation here:

* DOS / MS LAN Manager / Microsoft Network Client for DOS uses NDIS 2.
* Windows for Workgroups 3.1 / NT 3.x uses NDIS 3.0
* Windows 95 uses NDIS 3.1 / NDIS 4.0
* Windows 98 uses NDIS 4.1
* Windows 98SE / ME uses NDIS 5.0

Windows 9x as successors of NDIS 2 have backwards compatibility to NDIS 2 drivers and allow to load them.

However, NDIS 3/4/5 were abandoned soon after official support for their respective operating systems had ceased.

NDIS 2 fared differently, because networking under DOS remained a key component in industrial computing and some consumer software such as Norton GHOST which allowed disk imaging over the network.

As a result, we have a vast array of drivers available for modern network cards and chips much newer than Windows 9x, written for NDIS 2, a standard much *older* than Windows 9x, which will happily load these drivers as part of its backwards compatibility layers.

These drivers do not come with a dedicated Windows 9x-style INF file, therefore have no way to determine the hardware ID that belongs to them (ISAPNP or PCI or such).

At the time of release of these systems, some cards, due to lack of time to develop a dedicated NDIS3/4 driver (or laziness I guess), have had NDIS 2 drivers officially supplied for Windows 9x with an INF file that automatically installs them. This is the behavior this script aims to replicate.

## License

CC-BY-NC 3.0