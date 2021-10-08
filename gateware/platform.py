""" Board definitions (mapping of I/O pins, clock, etc.) """
import os
import sys

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.soc.integration.soc_core import SoCCore
from litex.soc.integration.builder import Builder
from litex.soc.interconnect.csr import AutoCSR, CSRStatus, CSRStorage

from litex.soc.cores.clock import iCE40PLL

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.generic_programmer import GenericProgrammer

import spi_slave

class RGBLed(Module, AutoCSR):
    def __init__(self, pads):
        self.output = CSRStatus(3)

        pu = Signal()

        self.specials += Instance("SB_LED_DRV_CUR",
            i_EN = 0b1,
            o_LEDPU = pu
        )

        self.pwm = Signal(3, reset=0)

        self.specials += Instance("SB_RGB_DRV",
            i_RGBLEDEN = 0b1,
            i_RGBPU = pu,
            i_RGB0PWM = self.output.status[0],
            i_RGB1PWM = self.output.status[1],
            i_RGB2PWM = self.output.status[2],
            o_RGB0 = pads.r,
            o_RGB1 = pads.g,
            o_RGB2 = pads.b,
            p_RGB0_CURRENT = "0b000011",
            p_RGB1_CURRENT = "0b000011",
            p_RGB2_CURRENT = "0b000011",
        )

class CRG(Module):
    def __init__(self, platform, sys_clk_freq):

        clk = ClockSignal()

        self.reset = Signal()
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_wish = ClockDomain(reset_less=True)
        self.clock_domains.cd_por = ClockDomain(reset_less=True)

        # "0b00" Sets 48MHz HFOSC output
        # "0b01" Sets 24MHz HFOSC output
        # "0b10" Sets 12MHz HFOSC output
        # "0b11" Sets  6MHz HFOSC output

        clkhf_div = 'NONE'

        if sys_clk_freq == 48e6:
            clkhf_div = "0b00"
        elif sys_clk_freq == 24e6:
            clkhf_div = "0b01"
        elif sys_clk_freq == 12e6:
            clkhf_div = "0b10"
        elif sys_clk_freq == 6e6:
            clkhf_div = "0b11"
        else:
            print("ERROR: SB_HFOSC cannot be set to desired freq : {}".format(sys_clk_freq))
            sys.exit(0)

        self.specials += Instance(
            "SB_HFOSC",
            i_CLKHFEN=1,
            i_CLKHFPU=1,
            o_CLKHF=clk,
            p_CLKHF_DIV=clkhf_div,
        )

        ## POR reset logic 
        por_cycles = 4096
        por_count = Signal(log2_int(por_cycles), reset=por_cycles - 1)
        por_done  = Signal()

        self.comb += self.cd_por.clk.eq(ClockSignal())
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        ## Create clock for wishbone SPI interface
        wish_freq = sys_clk_freq*3
        
        self.submodules.pll = pll = iCE40PLL()
        pll.register_clkin(clk, sys_clk_freq)
        pll.create_clkout(self.cd_wish, wish_freq, with_reset=False)

        self.specials += AsyncResetSynchronizer(self.cd_wish, ~por_done | ~pll.locked)
        platform.add_period_constraint(self.cd_wish.clk, 1e9/wish_freq)

        self.comb += self.cd_sys.clk.eq(clk)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)
        

class HatPlatform(LatticePlatform):
    
    _io = [

        ('rgb_led', 0,
            Subsignal('r', Pins('41')),
            Subsignal('g', Pins('40')),
            Subsignal('b', Pins('39')),
            IOStandard('LVCMOS33')
        ),

        ("spi", 0,
            Subsignal("clk",  Pins("15")),
            Subsignal("cs_n", Pins("16")),
            Subsignal("mosi", Pins("17")),
            Subsignal("miso", Pins("14")),
            IOStandard("LVCMOS33")
        ),

        ("bank0", 0, Pins("42"), IOStandard("LVCMOS18")),
        ("bank0", 1, Pins("38"), IOStandard("LVCMOS18")),
        ("bank0", 2, Pins("37"), IOStandard("LVCMOS18")),
        ("bank0", 3, Pins("36"), IOStandard("LVCMOS18")),
        ("bank0", 4, Pins("35"), IOStandard("LVCMOS18")),
        ("bank0", 5, Pins("34"), IOStandard("LVCMOS18")),
        ("bank0", 6, Pins("32"), IOStandard("LVCMOS18")),
        ("bank0", 7, Pins("31"), IOStandard("LVCMOS18")),

        ("bank2", 0, Pins("4"), IOStandard("LVCMOS18")),
        ("bank2", 1, Pins("3"), IOStandard("LVCMOS18")),
        ("bank2", 2, Pins("2"), IOStandard("LVCMOS18")),
        ("bank2", 3, Pins("48"), IOStandard("LVCMOS18")),
        ("bank2", 4, Pins("47"), IOStandard("LVCMOS18")),
        ("bank2", 5, Pins("46"), IOStandard("LVCMOS18")),
        ("bank2", 6, Pins("45"), IOStandard("LVCMOS18")),
        ("bank2", 7, Pins("44"), IOStandard("LVCMOS18")),
    ]

    _connectors = [
        ('bank0', "42 38 37 36 35 34 32 31"),
        ('bank2', "4 3 2 48 47 46 45 44")
    ]

    default_clk_name = "sb_hfosc"

    def __init__(self, sys_clk_freq):
        LatticePlatform.__init__(self, 'ice40-u4k-sg48', self._io, self._connectors, toolchain='icestorm')
        self.default_clk_period = 1e9 / sys_clk_freq

class BaseSoC(SoCCore):

    def __init__(self, sys_clk_freq = 12e6, **kwargs):

        self.platform = platform = HatPlatform(sys_clk_freq)

        kwargs["cpu_type"] = None
        kwargs["with_uart"] = False
        kwargs["with_timer"] = False
        kwargs["with_ctrl"] = True

        kwargs["csr_data_width"] = 32

        SoCCore.__init__(self, platform, sys_clk_freq, **kwargs)

        self.submodules.crg = CRG(platform, sys_clk_freq)

        spi_pads = platform.request("spi")
        self.submodules.bridge = spi_slave.SPIBridge(spi_pads)
        self.bus.add_master(name="bridge", master=self.bridge.wishbone)
