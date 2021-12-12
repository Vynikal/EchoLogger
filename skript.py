import pynmea2, serial, os, time, sys, glob, datetime
from porty import _scan_ports
from pynmea2 import nmea

def logfilename():
    now = datetime.datetime.now()
    return 'NMEA_%0.4d-%0.2d-%0.2d_%0.2d-%0.2d-%0.2d.nmea' % \
                (now.year, now.month, now.day,
                 now.hour, now.minute, now.second)
outfname = logfilename()

try:
    while True:
        ports = _scan_ports()
        if len(ports) == 0:
            sys.stderr.write('No ports found, waiting 10 seconds...press Ctrl-C to quit...\n')
            time.sleep(10)
            continue

        for port in ports:
            # try to open serial port
            sys.stderr.write('Trying port %s\n' % port)
            try:
                # try to read a line of data from the serial port and parse
                with serial.Serial(port, 115200, timeout=1) as ser:
                    # 'warm up' with reading some input
                    for i in range(10):
                        ser.readline()
                    # try to parse (will throw an exception if input is not valid NMEA)
                    pynmea2.parse(ser.readline().decode('ascii', errors='replace'))
                
                    # log data
                    sys.stderr.write('Logging data on %s to %s\n' % (port, outfname))
                    with open(outfname, 'wb') as f:
                        # loop will exit with Ctrl-C, which raises a
                        # KeyboardInterrupt
                        while True:
                            line = ser.readline()
                            line_nmea = pynmea2.parse(line.decode('ascii', errors='replace'))
                            depth = line_nmea.depth_meters
                            # print(line.decode('ascii', errors='replace').strip())
                            f.write(depth)
                
            except Exception as e:
                sys.stderr.write('Error reading serial port %s: %s\n' % (type(e).__name__, e))
            except KeyboardInterrupt as e:
                sys.stderr.write('Ctrl-C pressed, exiting log of %s to %s\n' % (port, outfname))

        sys.stderr.write('Scanned all ports, waiting 10 seconds...press Ctrl-C to quit...\n')
        time.sleep(10)
except KeyboardInterrupt:
    sys.stderr.write('Ctrl-C pressed, exiting port scanner\n')