import os
import usb.core
import usb.util
import usb.backend.libusb1
import time
import serial


USB_IF, USB_TIMEOUT = 0, 5 # set usb interface and timeout
backend = usb.backend.libusb1.get_backend(find_library=lambda x: "/usr/lib/libusb-1.0.so") # set libusb path. If you didn't occur usb.core.find() error, delete this line and modify the usb.core.find() parameters
ser = serial.Serial("/dev/ttyS0", baudrate=57600)

while True:
    dev = None
    try:
        while dev is None:
            print "Searching keyboard..."
            try:
                idVendor, idProduct = os.popen("lsusb -v | grep -i keyboard -B 4 | grep -E 'idVendor|idProduct' | grep -E -o '0x.{4}'").read().split("\n")[0:2]
                dev = usb.core.find(idVendor=int(idVendor, 16), idProduct=int(idProduct, 16), backend=backend)
                if dev is None:
                    raise ValueError('Device not found')
                # If you didn't use the 'backend', just delete it in find()
                endpoint = dev[0][(0,0)][0]
                if dev.is_kernel_driver_active(USB_IF) is True:
                    dev.detach_kernel_driver(USB_IF)
                usb.util.claim_interface(dev, USB_IF)

                print "Keyboard is ready."
                break

            except:
                print "No keyboards found."

        print "Found keyboard with idVendor {}, and idProduct {}".format(idVendor, idProduct)

        prev_control = None
        while True:
            control = None
            try:
                control = dev.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize, USB_TIMEOUT)
                prev_control = control
            except Exception, e:
                if e.errno == 19:
                    raise

            if control is not None:
                print control
            elif prev_control is not None:
                if all(key_code == 0 for key_code in prev_control):
                    prev_control = None
                else:
                    print prev_control

            time.sleep(0.02)

    except Exception, e:
        print e
        print "Can not read keyboards now, retrying..."
