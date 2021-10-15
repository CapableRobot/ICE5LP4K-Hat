
import os
import sys
import argparse
import shutil
import pathlib

from litex.soc.integration.builder import Builder

import platform
import trigger

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--load",  action="store_true", help="Load bitstream")

    args = parser.parse_args()

    soc = platform.BaseSoC()

    soc.submodules.rgb = platform.RGBLed(soc.platform.request("rgb_led"))
    soc.add_csr("rgb")

    ## Create a 1 kHz clock (1 ms) so that register 
    ## settings are in ms instead of 1/6 us intervals
    soc.submodules.wall = trigger.ClockDivider(12000)
    
    io = [soc.platform.request("bank0", num) for num in range(8)]
    soc.submodules.trigger  = trigger.TriggerController(soc.wall.strobe, 8, io)
    soc.add_csr("trigger")

    builder = Builder(soc, output_dir="build", csr_csv="build/csr.csv", compile_software=False)
    builder.build()

    binfile = os.path.join(builder.gateware_dir, soc.build_name + ".bin")
    csrfile = os.path.join(builder.gateware_dir, "..", "csr.csv")

    gen_dir = os.path.join(pathlib.Path(__file__).parent.absolute(), "..", "generated")
    
    print("Bitstream : {}".format(binfile))

    shutil.copy(binfile, gen_dir)
    shutil.copy(csrfile, gen_dir)

if __name__ == "__main__":
    main()