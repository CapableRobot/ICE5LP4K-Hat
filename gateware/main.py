
import os
import sys
import argparse

from litex.soc.integration.builder import Builder

import platform
import trigger

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--load",  action="store_true", help="Load bitstream")

    args = parser.parse_args()

    soc = platform.BaseSoC()

    ## soc.submodules.rgb = platform.RGBLed(led_pads)
    ## soc.add_csr("rgb")

    ## Create a 1 kHz clock (1 ms) so that register 
    ## settings are in ms instead of 1/6 us intervals
    soc.submodules.wall = trigger.ClockDivider(12000)
    
    io = [soc.platform.request("bank0", num) for num in range(8)]
    soc.submodules.trigger  = trigger.TriggerController(soc.wall.strobe, 8, io)
    soc.add_csr("trigger")

    builder = Builder(soc, output_dir="build", csr_csv="csr.csv", compile_software=False)
    builder.build()

    print("Bitstream : {}".format(os.path.join(builder.gateware_dir, soc.build_name + ".bin")))

if __name__ == "__main__":
    main()