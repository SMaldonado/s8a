from nmigen import *
from nmigen.sim import Simulator, Delay, Settle
from fft import Butterfly

if __name__ == "__main__":
    m = Module()
    m.submodules.butterfly = butterfly = Butterfly()

    sim = Simulator(m)
    sim.add_clock(1e-6) # important

    def test_butterfly():
        yield butterfly.tw_real.eq(1e20 - 1)
        yield butterfly.tw_imag.eq(1e20 - 1)
        for i in range(10):
            yield butterfly.a_real.eq(i)
            yield butterfly.b_real.eq(-i)
            yield butterfly.a_imag.eq(-i)
            yield butterfly.b_imag.eq(i)
            yield
            yield butterfly.start.eq(1)
            yield
            yield butterfly.start.eq(0)

            for j in range(3):
                yield

            got = yield(butterfly.a_prime_real)
            print(got)

    sim.add_sync_process(test_butterfly, domain="sync")
    with sim.write_vcd("sim/test.vcd", "sim/test.gtkw", traces=butterfly.ports()):
        sim.run_until(20e-6, run_passive=True)
