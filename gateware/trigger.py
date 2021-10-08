
from migen import *
from litex.soc.interconnect.csr import *

class ClockDivider(Module):
    def __init__(self, maxperiod):
        counter = Signal(max=maxperiod)
        period  = Signal(max=maxperiod)

        self.clock = Signal()
        self.strobe = Signal()

        self.comb += period.eq(maxperiod-1)
        self.sync += If(counter == 0,
                            self.clock.eq(~self.clock),
                            self.strobe.eq(1),
                            counter.eq(period),
                        ).Else(
                            self.strobe.eq(0),
                            counter.eq(counter - 1),
                        )

TRIG_MODE_STOP     = 0x00
TRIG_MODE_IDLE     = 0x01
TRIG_MODE_INTERVAL = 0x02
TRIG_MODE_ONESHOT  = 0x03
TRIG_MODE_CONSTANT = 0x04

class Trigger(Module):

    def __init__(self, strobe, width):
    
        self.trigger  = Signal()
        self.mode     = Signal(width)
        self.interval = Signal(width)
        self.duration = Signal(width)

        interval_counter = Signal(width)
        duration_counter = Signal(width)
        
        self.sync += If(strobe,
            Case(self.mode, {
                ## Make sure trigger is stopped (it might already be low)
                TRIG_MODE_STOP: [self.trigger.eq(0)],

                ## Return state after a one-shot trigger
                TRIG_MODE_IDLE: [self.trigger.eq(self.trigger)],

                ## Make sure we have a value (non zero) duration & interval before continuing
                ## They are set outside of this module, and may not be set on the first clock edge
                TRIG_MODE_INTERVAL: [
                    If(self.duration != 0,
                        If(self.interval != 0, 
                            If(interval_counter == 0,
                                duration_counter.eq(self.duration-1),   # Setup the trigger duration
                                self.trigger.eq(1),                     # Start the trigger
                                interval_counter.eq(self.interval-1),   # Reset the trigger interval
                            ).Else(
                                interval_counter.eq(interval_counter - 1),
                            )
                        )
                    )
                ],

                TRIG_MODE_ONESHOT: [
                    If(self.duration != 0, 
                        duration_counter.eq(self.duration-1),   # Setup the trigger duration
                        self.trigger.eq(1),                     # Start the trigger 
                    )
                ],

                TRIG_MODE_CONSTANT: [self.trigger.eq(1)]

            }).makedefault(TRIG_MODE_IDLE),

            If(self.trigger == 1,
                # Skip if in constant trigger mode (where trigger duration is ignored)
                If(self.mode != TRIG_MODE_CONSTANT,                 
                    If(duration_counter == 0,                       
                        self.trigger.eq(0)                          # Stop the trigger 
                    ).Else(                             
                        duration_counter.eq(duration_counter - 1)   # Keep the trigger going
                    )
                )
            )
        )

class TriggerController(Module, AutoCSR):

    def __init__(self, strobe, width, pins):
        self.submodules.trigger = Trigger(strobe, width)

        self.mode     = CSRStorage(8, description="Trigger Mode", reset=TRIG_MODE_STOP)
        self.interval = CSRStorage(8, description="Trigger Interval")
        self.duration = CSRStorage(8, description="Trigger Duration")
        self.mask     = CSRStorage(8, description="Trigger Mask")

        self.comb += [
            self.trigger.mode.eq(self.mode.storage),
            self.trigger.interval.eq(self.interval.storage),
            self.trigger.duration.eq(self.duration.storage),
        ]

        self.sync += [
            If(strobe,
                ## We've started the trigger, can now return to IDLE mode
                If(self.mode.storage == TRIG_MODE_ONESHOT,
                    If(self.trigger.trigger == 1,
                        self.mode.storage.eq(TRIG_MODE_IDLE) 
                    )
                ),
                ## We've IDLE and trigger has stopped, go to STOP
                If(self.mode.storage == TRIG_MODE_IDLE,
                    If(self.trigger.trigger == 0,
                        self.mode.storage.eq(TRIG_MODE_STOP)
                    )
                )
            )
        ]

        ## Apply mask between internal trigger signal and hardware pins
        for i in range(len(pins)):
            self.comb  += pins[i].eq(self.mask.storage[i] & self.trigger.trigger)
            