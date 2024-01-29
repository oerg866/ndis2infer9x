import configparser
import argparse

parser = argparse.ArgumentParser(description='NDIS2 to Windows 9x INF converter', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('--id', type=str, help='PCI Vendor/device ID (hexadecimal string in the format of ven:dev i.e. "10EC:8139")', action="append", required=True)
parser.add_argument('--nif', type=str, help='NDIS 2 driver NIF file', required=True)
parser.add_argument('--out', type=str, help='Windows 9x INF output file name', required=True)

args = parser.parse_args()

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the configuration file
config.read(args.nif)

print(config.sections())

# Extract information from the 'File' section
file_section = config['File']
fileName = file_section['Name']

deviceSection = ""
deviceType = ""
deviceTitle = ""
driverVersion = ""
driverName = ""
driverFile = ""

for secName in config.sections():
    driverName = config.get(secName, 'DriverName', fallback=None)

    if (driverName is not None):
        print(f"Device Section {secName}")

        deviceType = config.get(secName, 'Type', fallback=None)
        deviceTitle = config.get(secName, 'Title', fallback=None).replace('"','')
        driverVersion = config.get(secName, 'Version', fallback=None)

        deviceSection = secName
        break

if (deviceType != 'NDIS'):
    print(f"Device type {deviceType} doesn't match expected value 'NDIS'\n")
    exit(1)

driverFile = config.get('File', 'Name', fallback=None)

if (driverFile is None):
    print(f"NIF file malformed - no file name specified!")

print("Device Name:", deviceTitle)
print("Driver Version:", driverVersion)
print("Driver Name:", driverName)
print("File Name:", driverFile)


with open(args.out, 'w', encoding='cp1252') as outinf:
    outinf.write(f'; NDIS2 Wrapper Inf\n')
    outinf.write(f'; (C) 2024 Eric Voirin (oerg866@googlemail.com)\n')
    outinf.write(f'[Version]\n')
    outinf.write(f'LayoutFile=layout.inf\n')
    outinf.write(f'Signature="$CHICAGO$"\n')
    outinf.write(f'Class=Net\n')
    outinf.write(f'Provider=%VENDOR%\n')
    outinf.write(f'\n')
    outinf.write(f'[Manufacturer]\n')
    outinf.write(f'%VENDOR%=ND2WRAP\n')
    outinf.write(f'\n')
    outinf.write(f'[ND2WRAP]\n')


    # Iterate through every supplied ID (we have to do this again later for the NDI device reg key section)

    idCount = 0

    for id in args.id:
        pciVen, pciDev = id.split(':')
        outinf.write(f'%DEVICE%=nd2wrap{idCount}.ndi,PCI\VEN_{pciVen}&DEV_{pciDev}\n')
        idCount +=1

    outinf.write(f'\n')
    outinf.write(f'[SourceDisksNames]\n')
    outinf.write(f'1="NDIS2 Driver",,\n')
    outinf.write(f'\n')
    outinf.write(f'[SourceDisksFiles]\n')
    outinf.write(f'{driverFile}=1\n')
    outinf.write(f'\n')

    idCount = 0

    for id in args.id:
        pciVen, pciDev = id.split(':')
        outinf.write(f'[nd2wrap{idCount}.ndi]\n')
        outinf.write(f'AddReg=nd2wrap{idCount}.ndi.reg,nd2wrap.ndi.reg\n')
        outinf.write(f'\n')
        outinf.write(f'[nd2wrap{idCount}.ndi.reg]\n')
        outinf.write(f'HKR,Ndi,DeviceID,,"PCI\VEN_{pciVen}&DEV_{pciDev}"\n')
        outinf.write(f'\n')

        idCount +=1

    outinf.write(f'\n')
    outinf.write(f'[nd2wrap.ndi.reg]\n')
    outinf.write(f'HKR,,DevLoader,,*ndis\n')
    outinf.write(f'HKR,,EnumPropPages,,"netdi.dll,EnumPropPages"\n')
    outinf.write(f'; NDIS Info\n')

    driverNameWithoutDollar = driverName.replace('$', '')

    outinf.write(f'HKR,NDIS,LogDriverName,,"{driverNameWithoutDollar}"\n')
    outinf.write(f'HKR,NDIS,MajorNdisVersion,1,03\n')
    outinf.write(f'HKR,NDIS,MinorNdisVersion,1,0A\n')
    outinf.write(f'HKR,NDIS\\NDIS2,DriverName,,"{driverName}"\n')
    outinf.write(f'HKR,NDIS\\NDIS2,FileName,,"{driverFile}"\n')
    outinf.write(f'; Interfaces\n')
    outinf.write(f'HKR,Ndi\\Interfaces,DefUpper,,"ndis2"\n')
    outinf.write(f'HKR,Ndi\\Interfaces,DefLower,,"ethernet"\n')
    outinf.write(f'HKR,Ndi\\Interfaces,UpperRange,,"ndis2"\n')
    outinf.write(f'HKR,Ndi\\Interfaces,LowerRange,,"ethernet"\n')
    outinf.write(f'; Install sections\n')
    outinf.write(f'HKR,Ndi\\Install,ndis2,,"nd2wrap.inst.ndis2"\n')
    outinf.write(f'HKR,Ndi\\Remove,ndis2,,"nd2wrap.rmv.ndis2"\n')
    outinf.write(f'\n')
    outinf.write(f'\n')
    outinf.write(f'\n')

    # Parse parameter sections and convert them to win9x registry layout

    for secName in config.sections():
        if (secName == deviceSection or secName == 'File'):
            continue

        print(f'Parameter: {secName}')

        
        # I actually couldn't find too much documentation about these types so I'm just assuming:
        # - Everything that's a string is also editable
        # - Everything that's not a string is an integer
        
        if (config.get(secName, "type", fallback="") == "string"):
            paramType = "edit"
        else:
            paramType = "int"

        if (config.get(secName, "optional", fallback="") == "YES"):
            optional = "1"
        else:
            optional = "0"

        stringSize = config.get(secName, "Strlength", fallback=None)

        # Trim extra "s

        paramDesc = config.get(secName, "display", fallback="").replace('"', '')
        paramDesc = config.get(secName, "display", fallback="").replace('"', '')

        outinf.write(f'HKR, , {secName}, 0, ""\n')
        outinf.write(f'HKR, Ndi\\params\\{secName},ParamDesc,0,"{paramDesc}"\n')
        outinf.write(f'HKR, Ndi\\params\\{secName},Default,  0,""\n')
        outinf.write(f'HKR, Ndi\\params\\{secName},type,     0,"{paramType}"\n')

        if (paramType == "edit" and stringSize):
            outinf.write(f'HKR, Ndi\\params\\{secName},LimitText,0,"{stringSize}"\n')
            
        outinf.write(f'HKR, Ndi\\params\\{secName},optional,0,"{optional}"\n')
        outinf.write(f'HKR, Ndi\\params\\{secName},flag, 1, "20, "00", "00, "00"\n')
        outinf.write(f'\n')

    outinf.write(f'HKR,,MsPciScan,0,"2"\n')
    outinf.write(f'\n')
    outinf.write(f'[nd2wrap.inst.ndis2]\n')
    outinf.write(f'CopyFiles=nd2wrap.ndis2.CopyFiles\n')
    outinf.write(f'AddReg=nd2wrap.inst.ndis2.reg\n')
    outinf.write(f'\n')
    outinf.write(f'[nd2wrap.rmv.ndis2]\n')
    outinf.write(f'AddReg=nd2wrap.rmv.ndis2.reg\n')
    outinf.write(f'\n')
    outinf.write(f'[nd2wrap.inst.ndis2.reg]\n')
    outinf.write(f'HKLM,"Software\\Microsoft\\Windows\\CurrentVersion\\Network\\Real Mode Net",{driverFile},,low\n')
    outinf.write(f'\n')
    outinf.write(f'[nd2wrap.rmv.ndis2.reg]\n')
    outinf.write(f'HKLM,"Software\\Microsoft\\Windows\\CurrentVersion\\Network\\Real Mode Net",{driverFile}\n')
    outinf.write(f'\n')
    outinf.write(f'[nd2wrap.ndis2.CopyFiles]\n')
    outinf.write(f'{driverFile}\n')
    outinf.write(f'\n')
    outinf.write(f'[DestinationDirs]\n')
    outinf.write(f'nd2wrap.ndis2.CopyFiles=26\n')
    outinf.write(f'\n')
    outinf.write(f'[Strings]\n')
    outinf.write(f'VENDOR="NDIS2Infer by Oerg866"\n')
    outinf.write(f'DEVICE="{deviceTitle}"\n')
    outinf.write(f'\n')

