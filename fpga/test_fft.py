from nmigen import *
from nmigen.sim import Simulator, Delay, Settle
from fft import Butterfly

if __name__ == "__main__":
    m = Module()
    m.submodules.butterfly = butterfly = Butterfly()

    sim = Simulator(m)
    sim.add_clock(1e-6) # important

    def process():
        yield
        yield butterfly.start.eq(1)
        yield
        yield butterfly.start.eq(0)

    sim.add_sync_process(process, domain="sync") # or sim.add_sync_process(process), see below
    with sim.write_vcd("sim/test.vcd", "sim/test.gtkw", traces=butterfly.ports()):
        sim.run_until(20e-6, run_passive=True)
